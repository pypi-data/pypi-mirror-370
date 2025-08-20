"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import glob
import pandas as pd
from typing import Optional, List
from io import StringIO, BytesIO
import requests
from sqlalchemy import create_engine, inspect
from abc import ABC, abstractmethod

DEFAULT_PORTS = {
    "5432": "postgresql",
    "3306": "mysql",
    "1433": "mssql+pymssql",
    "1521": "oracle",
    "27017": "mongodb",
    "6379": "redis",
    "50000": "db2",
    "1434": "sybase",
    "3307": "mariadb",
    "5433": "greenplum",
    "5000": "sqlite",
}

class DataSource(ABC):
    @abstractmethod
    def get_data(self, table_or_query=None, pack_config=None):
        pass

class FileSource(DataSource):
    def __init__(self, file_path):
        self.file_path = file_path

    def get_data(self, table_or_query=None, pack_config=None):
        if os.path.isfile(self.file_path):
            return self._load_file(self.file_path, pack_config)
        if os.path.isdir(self.file_path):
            data_files = glob.glob(os.path.join(self.file_path, "*.csv")) + glob.glob(
                os.path.join(self.file_path, "*.xlsx")
            )
            if not data_files:
                raise FileNotFoundError(
                    "No CSV or XLSX files found in the provided path."
                )
            return self._load_file(data_files[0], pack_config)
        raise FileNotFoundError(
            f"The path {self.file_path} is neither a file nor a directory, or it can't be reached."
        )

    @staticmethod
    def _load_file(file_path, pack_config):
        skiprows = 0
        if pack_config:
            skiprows = pack_config.get("job", {}).get("source", {}).get("skiprows", 0)
        if file_path.endswith(".csv"):
            return pd.read_csv(
                file_path,
                low_memory=False,
                memory_map=True,
                skiprows=int(skiprows),
                on_bad_lines="warn",
                encoding="utf-8",
            )
        if file_path.endswith(".xlsx"):
            return pd.read_excel(
                file_path,
                engine="openpyxl",
                skiprows=int(skiprows),
            )
        raise ValueError(
            f"Unsupported file extension or missing 'skiprows' for file: {file_path}"
        )

class DatabaseSource(DataSource):
    def __init__(self, connection_string=None, config=None):
        if connection_string:
            self.engine = create_engine(connection_string)
        elif config:
            db_type = config.get("type") or DEFAULT_PORTS.get(str(config.get("port")), "unknown")
            if db_type == "unknown":
                raise ValueError(f"Unsupported or unknown database port: {config.get('port')}")
            # Handle SQLite specially as it does not use username/host/port
            if db_type.startswith("sqlite"):
                database_path = config.get("database") or ":memory:"
                if database_path == ":memory:":
                    conn_str = "sqlite:///:memory:"
                else:
                    # Accept absolute or relative filesystem path
                    conn_str = f"sqlite:///{database_path}"
                self.engine = create_engine(conn_str)
            else:
                self.engine = create_engine(
                    f"{db_type}://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
                )
        else:
            raise ValueError("DatabaseSource requires a connection_string or a config dict.")

    def get_data(self, table_or_query=None, pack_config=None):
        """
        Load data from the database.

        - If table_or_query is a string table name: return a single DataFrame for that table
        - If table_or_query is a SQL query string: return a single DataFrame for the query
        - If table_or_query is a list/tuple/set of table names: return a list of DataFrames in the same order
        - If table_or_query is '*' or None: scan all tables in the database and return a list of DataFrames
        """

        # Optional future use of pack_config (e.g., schema), kept minimal for now
        schema = None
        if pack_config:
            schema = (
                pack_config.get("job", {})
                .get("source", {})
                .get("schema")
            )

        # Default behavior: scan all tables
        if table_or_query is None or (isinstance(table_or_query, str) and table_or_query.strip() == "*"):
            table_names = self._get_all_table_names(schema)
            if not table_names:
                raise ValueError("No tables found in the database for the given schema.")
            return [self._read_table(table_name, schema) for table_name in table_names]

        # If a list/tuple/set of table names is provided
        if isinstance(table_or_query, (list, tuple, set)):
            table_names = list(table_or_query)
            return [self._read_table(table_name, schema) for table_name in table_names]

        # If a single string is provided, determine if it's a table name or SQL query
        if isinstance(table_or_query, str):
            if self._is_sql_query(table_or_query):
                return pd.read_sql(table_or_query, self.engine)
            return self._read_table(table_or_query, schema)

        raise TypeError(
            "table_or_query must be None, '*', a string (table name or SQL), or a list/tuple/set of table names."
        )

    def _read_table(self, table_name: str, schema: Optional[str] = None) -> pd.DataFrame:
        """Read a full table as a DataFrame using dialect-aware SQL."""
        try:
            return pd.read_sql_table(table_name, self.engine, schema=schema)
        except Exception:
            # Fallback to a simple SELECT * if read_sql_table is unsupported for the dialect
            qualified = f"{schema}.{table_name}" if schema else table_name
            return pd.read_sql(f"SELECT * FROM {qualified}", self.engine)

    def _get_all_table_names(self, schema: Optional[str] = None) -> List[str]:
        """Return all table names (and views) in the database for the given schema, sorted alphabetically."""
        inspector = inspect(self.engine)
        try:
            tables = inspector.get_table_names(schema=schema)
        except Exception:
            tables = []
        try:
            views = inspector.get_view_names(schema=schema)
        except Exception:
            views = []
        # Remove duplicates and sort for deterministic ordering
        names = sorted(set((tables or []) + (views or [])))
        return names

    def _is_sql_query(self, s: str) -> bool:
        """Heuristic to detect if a string is a SQL query rather than a bare table name."""
        sql = s.strip().lower()
        if ";" in sql or "\n" in sql:
            return True
        starters = ("select", "with", "show", "describe", "pragma", "explain")
        return any(sql.startswith(token) for token in starters)

def _infer_format_from_path(path: str, explicit_format: Optional[str] = None) -> str:
    if explicit_format:
        return explicit_format.lower()
    lower = path.lower()
    if lower.endswith(".csv"):
        return "csv"
    if lower.endswith(".json"):
        return "json"
    if lower.endswith(".parquet") or lower.endswith(".pq"):
        return "parquet"
    if lower.endswith(".xlsx") or lower.endswith(".xls"):
        return "excel"
    return "csv"


def _read_remote_with_pandas(path: str, fmt: str, storage_options: Optional[dict], pack_config: Optional[dict]):
    skiprows = 0
    if pack_config:
        skiprows = pack_config.get("job", {}).get("source", {}).get("skiprows", 0)

    if fmt == "csv":
        return pd.read_csv(
            path,
            storage_options=storage_options,
            low_memory=False,
            memory_map=True,
            skiprows=int(skiprows),
            on_bad_lines="warn",
            encoding="utf-8",
        )
    if fmt == "json":
        # Let pandas handle the URL/FS path; this supports ndjson via lines=True if needed later
        return pd.read_json(path, storage_options=storage_options)
    if fmt == "parquet":
        return pd.read_parquet(path, storage_options=storage_options)
    if fmt == "excel":
        return pd.read_excel(path, storage_options=storage_options, engine="openpyxl", skiprows=int(skiprows))
    # Fallback to CSV
    return pd.read_csv(path, storage_options=storage_options)


class S3Source(DataSource):
    def __init__(self, config):
        self.config = config or {}

    def get_data(self, table_or_query=None, pack_config=None):
        # Expect either a full s3 path in config['path'] or bucket/key
        path = self.config.get("path")
        if not path:
            bucket = self.config.get("bucket")
            key = self.config.get("key")
            if bucket and key:
                path = f"s3://{bucket}/{key}"
        if not path:
            raise ValueError("S3Source requires either 'path' or 'bucket'+'key' in config.")

        storage_options = {}
        for opt_key in [
            "key",  # aws_access_key_id
            "secret",  # aws_secret_access_key
            "token",  # aws_session_token
            "client_kwargs",  # e.g., {"region_name": "us-east-1"}
        ]:
            if opt_key in self.config:
                storage_options[opt_key] = self.config[opt_key]

        fmt = _infer_format_from_path(path, self.config.get("format"))
        return _read_remote_with_pandas(path, fmt, storage_options or None, pack_config)

class GCSSource(DataSource):
    def __init__(self, config):
        self.config = config or {}

    def get_data(self, table_or_query=None, pack_config=None):
        # Expect gs:// style path or bucket/object
        path = self.config.get("path")
        if not path:
            bucket = self.config.get("bucket")
            blob = self.config.get("blob") or self.config.get("key")
            if bucket and blob:
                path = f"gs://{bucket}/{blob}"
        if not path:
            raise ValueError("GCSSource requires either 'path' or 'bucket'+'blob' in config.")

        storage_options = {}
        for opt_key in [
            "token",  # path to service account json or dict credentials
            "project",
        ]:
            if opt_key in self.config:
                storage_options[opt_key] = self.config[opt_key]

        fmt = _infer_format_from_path(path, self.config.get("format"))
        return _read_remote_with_pandas(path, fmt, storage_options or None, pack_config)

class AzureBlobSource(DataSource):
    def __init__(self, config):
        self.config = config or {}

    def get_data(self, table_or_query=None, pack_config=None):
        # Accept full abfs(s):// path or account/container/blob components
        path = self.config.get("path")
        if not path:
            account_name = self.config.get("account_name")
            container = self.config.get("container")
            blob = self.config.get("blob") or self.config.get("key")
            if account_name and container and blob:
                path = f"abfs://{container}@{account_name}.dfs.core.windows.net/{blob}"
        if not path:
            raise ValueError("AzureBlobSource requires either 'path' or 'account_name'+'container'+'blob'.")

        storage_options = {}
        # adlfs uses Azure credentials via storage_options
        for opt_key in [
            "account_name",
            "account_key",
            "sas_token",
            "tenant_id",
            "client_id",
            "client_secret",
        ]:
            if opt_key in self.config:
                storage_options[opt_key] = self.config[opt_key]

        fmt = _infer_format_from_path(path, self.config.get("format"))
        return _read_remote_with_pandas(path, fmt, storage_options or None, pack_config)

class HDFSSource(DataSource):
    def __init__(self, config):
        self.config = config or {}

    def get_data(self, table_or_query=None, pack_config=None):
        # Expect hdfs://host:port/path
        path = self.config.get("path")
        if not path:
            host = self.config.get("host")
            port = self.config.get("port") or 8020
            hdfs_path = self.config.get("hdfs_path") or self.config.get("key")
            if host and hdfs_path:
                path = f"hdfs://{host}:{port}/{hdfs_path.lstrip('/')}"
        if not path:
            raise ValueError("HDFSSource requires 'path' or 'host'+'hdfs_path' in config.")

        storage_options = {}
        for opt_key in [
            "host",
            "port",
            "user",
            "kerb_kwargs",  # kerberos parameters if applicable
        ]:
            if opt_key in self.config:
                storage_options[opt_key] = self.config[opt_key]

        fmt = _infer_format_from_path(path, self.config.get("format"))
        return _read_remote_with_pandas(path, fmt, storage_options or None, pack_config)

class SFTPSource(DataSource):
    def __init__(self, config):
        self.config = config or {}

    def get_data(self, table_or_query=None, pack_config=None):
        # Expect sftp://user@host:port/path or individual fields
        path = self.config.get("path")
        if not path:
            host = self.config.get("host")
            port = self.config.get("port") or 22
            username = self.config.get("username") or self.config.get("user")
            remote_path = self.config.get("remote_path") or self.config.get("key")
            if host and username and remote_path:
                path = f"sftp://{username}@{host}:{port}/{remote_path.lstrip('/')}"
        if not path:
            raise ValueError("SFTPSource requires 'path' or 'host'+'username'+'remote_path' in config.")

        storage_options = {}
        for opt_key in [
            "username",
            "password",
            "client_keys",  # path to private key
            "passphrase",
            "port",
        ]:
            if opt_key in self.config:
                storage_options[opt_key] = self.config[opt_key]

        fmt = _infer_format_from_path(path, self.config.get("format"))
        return _read_remote_with_pandas(path, fmt, storage_options or None, pack_config)

class HttpSource(DataSource):
    def __init__(self, config):
        self.config = config or {}

    def get_data(self, table_or_query=None, pack_config=None):
        url = self.config.get("url") or self.config.get("path")
        if not url:
            raise ValueError("HttpSource requires 'url' in config.")

        fmt = (self.config.get("format") or "").lower()
        headers = self.config.get("headers")
        params = self.config.get("params")
        timeout = self.config.get("timeout", 30)

        if fmt in ("", "csv", "json"):
            # Try to be smart: if explicit format provided, handle locally; else let pandas read directly
            if fmt == "csv":
                resp = requests.get(url, headers=headers, params=params, timeout=timeout)
                resp.raise_for_status()
                text = resp.text
                skiprows = 0
                if pack_config:
                    skiprows = pack_config.get("job", {}).get("source", {}).get("skiprows", 0)
                return pd.read_csv(StringIO(text), low_memory=False, memory_map=True, skiprows=int(skiprows), on_bad_lines="warn", encoding="utf-8")
            if fmt == "json":
                resp = requests.get(url, headers=headers, params=params, timeout=timeout)
                resp.raise_for_status()
                data = resp.json()
                return pd.json_normalize(data)
            # No explicit format: let pandas figure it out directly from the URL
            guessed = _infer_format_from_path(url)
            return _read_remote_with_pandas(url, guessed, None, pack_config)

        # Other formats (parquet, excel) — let pandas attempt direct URL read
        return _read_remote_with_pandas(url, fmt, None, pack_config)

class FolderSource(DataSource):
    def __init__(self, config):
        self.config = config
    def get_data(self, table_or_query=None, pack_config=None):
        raise NotImplementedError("FolderSource.get_data Not yet Implemented.")

class MongoDBSource(DataSource):
    def __init__(self, config):
        self.config = config
    def get_data(self, table_or_query=None, pack_config=None):
        raise NotImplementedError("MongoDBSource.get_data Not yet Implemented.")

class SqliteSource(DataSource):
    def __init__(self, config):
        self.config = config
    def get_data(self, table_or_query=None, pack_config=None):
        raise NotImplementedError("SqliteSource.get_data Not yet Implemented.")


def get_data_source(source_config):
    type_ = source_config.get("type")
    if type_ == "file":
        return FileSource(source_config.get("config", {}).get("path"))
    elif type_ == "folder":
        return FolderSource(source_config.get("config", {}))
    elif type_ == "postgresql":
        return DatabaseSource(connection_string=source_config.get("config", {}).get("connection_string"), config=source_config.get("config"))
    elif type_ == "mysql":
        return DatabaseSource(connection_string=source_config.get("config", {}).get("connection_string"), config=source_config.get("config"))
    elif type_ == "oracle":
        return DatabaseSource(connection_string=source_config.get("config", {}).get("connection_string"), config=source_config.get("config"))
    elif type_ == "mssql":
        return DatabaseSource(connection_string=source_config.get("config", {}).get("connection_string"), config=source_config.get("config"))
    elif type_ == "sqlite":
        return DatabaseSource(connection_string=source_config.get("config", {}).get("connection_string"), config=source_config.get("config"))
    elif type_ == "mongodb":
        return DatabaseSource(connection_string=source_config.get("config", {}).get("connection_string"), config=source_config.get("config"))
    elif type_ == "s3":
        return S3Source(source_config.get("config", {}))
    elif type_ == "gcs":
        return GCSSource(source_config.get("config", {}))
    elif type_ == "azure_blob":
        return AzureBlobSource(source_config.get("config", {}))
    elif type_ == "hdfs":
        return HDFSSource(source_config.get("config", {}))
    elif type_ == "sftp":
        return SFTPSource(source_config.get("config", {}))
    elif type_ in ["http", "https"]:
        return HttpSource(source_config.get("config", {}))
    else:
        raise ValueError(f"Type de source non supporté : {type_}")
