import atexit
import pickle
import signal
import sqlite3
import time
from contextlib import contextmanager
from datetime import date, datetime
from functools import cached_property
from pathlib import Path
from types import SimpleNamespace, MethodType
from typing import Type, Any, List, Dict, Generator

import pandas as pd
from fastj2 import FastJ2
from loguru import logger as log
from pandas import DataFrame
from toomanyconfigs import CWD, TOMLConfig

@property
def row_count(self):
    return len(self)

def empty_dataframe_from_type(typ: Type, defvals: list = None) -> tuple[DataFrame, list]:
    a = typ.__annotations__
    if not defvals: defvals = ["id", "created_on", "created_by", "modified_on", "modified_by"]

    # Check for conflicts with default columns
    for col in a:
        for name in defvals:
            if col == name:
                raise KeyError(f"Your database class cannot contain default values: {defvals}")

    # Create basic DataFrame
    df = pd.DataFrame(columns=a.keys()).astype(a)  # type: ignore

    # Set up uniqueness constraints
    unique_keys = getattr(typ, '_unique_keys', [])
    if unique_keys:
        log.debug(f"[p2d2]: Found unique keys for {typ.__name__}: {unique_keys}")

    return df, unique_keys

def get_title(self, index):
    return self.at[index, self.title]

def get_subtitle(self, index):
    return self.at[index, self.subtitle]

class Config(TOMLConfig):
    password: str = None

class PickleChangelog:
    def __init__(self, database: 'Database'):
        self.database = database
        self.path = self.database._cwd.file_structure[1]
        self.changelog: dict = {}
        self.fetch()

    def __repr__(self):
        return f"[{self.path.name}]"

    def fetch(self):
        try:
            with open(self.path, 'rb') as f:
                self.changelog = pickle.load(f)
            log.debug(f"{self}: Loaded changelog.")
        except (FileNotFoundError, EOFError):
            log.debug("No existing changelog found or empty file, starting fresh")

    def commit(self):
        with open(self.path, 'wb') as f:
            pickle.dump(self.changelog, f)

    def log_change(self, signature: str, table_name: str, change_type: str):
        if not (sig := self.changelog.get(signature)):
            self.changelog[signature] = sig = {}
        if not (tbl := sig.get(table_name)):
            sig[table_name] = tbl = {}
        if not (chg := tbl.get(change_type)):
            tbl[change_type] = chg = 0
        tbl[change_type] = chg + 1

class TableIndex(dict):
    list: list = []
    def __init__(self):
        super().__init__()

# class TableProxy:
#     def __init__(self, df, database, name, signature="system"):
#         self.df = df
#         self.db = database
#         self.name = name
#         self.signature = signature
#
#     def create(self, signature = None, **kwargs):
#         signature = signature or self.signature
#         self.df = self.db.create(self.df, signature=signature, **kwargs)
#         return self
#
#     def update(self, updates: dict, signature = None, **conditions):
#         signature = signature or self.signature
#         self.df = self.db.update(self.df, updates, signature=signature, **conditions)
#         return self
#
#     def delete(self, **conditions):
#         self.df = self.db.delete(self.df, **conditions)
#         return self
#
#     def read(self, **conditions):
#         return self.db.read(self.df, **conditions)

# @contextmanager
# def table(self, table: str | DataFrame | Any, signature: str = "system") -> Generator[TableProxy]:
#     if isinstance(table, str):
#         table_name = table
#         if table in self._tables.keys():
#             table = self._tables[table]
#     elif isinstance(table, DataFrame):
#         table_name = None
#         for name, df in self._tables.items():
#             if df.equals(table):
#                 table_name = name
#                 break
#         if table_name is None: raise ValueError("DataFrame content doesn't match any database table")
#     else:
#         raise TypeError
#
#     proxy = TableProxy(table, self, table_name, signature)
#     try:
#         yield proxy
#     finally:
#         setattr(self, table_name, proxy.df)

class Database:
    def __init__(
            self,
            db_name = None,
        ):
        try:
            _ = self._tables
        except KeyError:
            pass
        if db_name is None: db_name = "my_database"
        if not isinstance(db_name, str): raise RuntimeError
        self._name = db_name
        db = f"{self._name}.db"
        backups = "backups"
        self._cwd = CWD({
            f"{self._name}": {
                db: None,
                "changes.pkl": None,
                "config.toml": None,
                backups: {}
            }
        })
        self._path: Path = self._cwd.file_structure[0]
        self._backups: Path = self._cwd.cwd / self._name / backups
        self._default_columns = ["created_at", "created_by" "modified_at", "modified_by"]
        self._unique_keys = {}

        #initialize schema
        for item in self.__annotations__.items():
            a, t = item
            if a.startswith("_"): continue
            if hasattr(self, a): continue
            df, unique_keys = empty_dataframe_from_type(t, self._default_columns)
            df.insert(0, 'created_at', pd.Series(dtype='datetime64[ns]'))
            df.insert(1, 'created_by', pd.Series(dtype='str'))
            df.insert(2, 'modified_at', pd.Series(dtype='datetime64[ns]'))
            df.insert(3, 'modified_by', pd.Series(dtype='str'))
            setattr(self, a, df)
            self._unique_keys[a] = unique_keys

        self._fetch()
        _ = self._pkl
        #_ = self._cfg

        signal.signal(signal.SIGTERM, self._signal_handler)  # Graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)  # Ctrl+C
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, self._signal_handler)  # Terminal close

    def _signal_handler(self, signum, frame):
        log.debug(f"Received signal {signum}, committing database")
        self._commit()
        self._pkl.commit()
        exit(0)

    def __repr__(self):
        return f"[{self._name}.db]"

    # @cached_property
    # def _cfg(self) -> Config:
    #     cfg = Config.create(self._cwd.file_structure[2])
    #     return cfg

    @cached_property
    def _pkl(self) -> PickleChangelog:
        return PickleChangelog(self)

    @cached_property
    def _analytics(self):
        metadata = {}
        for item in self._tables.list:
            metadata["row_count"] = len(item)
            metadata["column_count"] = len(item.columns)
            bytes_value = int(item.memory_usage(deep=False).sum())
            metadata["size_bytes"] = bytes_value
            metadata["size_kilobytes"] = round(bytes_value / 1024, 2)
            metadata["size_megabytes"] = round(bytes_value / (1024**2), 2)
            metadata["size_gigabytes"] = round(bytes_value / (1024**3), 6)

        return SimpleNamespace(
            **metadata, as_dict=metadata
        )

    @property
    def _tables(self) -> TableIndex:
        index = TableIndex() #table index is a subclass of dict with a list attribute
        for attr_name, attr_type in self.__annotations__.items():
            if attr_name.startswith("_"): continue
            index[attr_name] = getattr(self, attr_name, None)
            if index[attr_name] is None: raise KeyError
        if index == {}: raise RuntimeError("Cannot initialize a database with no _tables!")
        for item in index.keys():
            index.list.append(getattr(self, item))
        return index

    def _backup(self):
        today = date.today()
        folder = self._backups / str(today)

        if not any(self._backups.glob(f"{today}*")):
            log.warning(f"{self}: Backup not found for today! Creating...")
            folder.mkdir(exist_ok=True)
            if folder.exists():
                log.success(f"{self}: Successfully created backup folder at {folder}")
            else:
                raise FileNotFoundError

            for table_name, table_df in self._tables.items():
                backup_path = folder / f"{table_name}.parquet"
                table_df.to_parquet(backup_path)

    def _fetch(self):
        with sqlite3.connect(self._path) as conn:
            successes = 0
            for table_name in self._tables.keys():
                try:
                    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                    try:
                        setattr(df, "title", df.columns[4])
                        setattr(df, "get_title", MethodType(get_title, df))
                    except IndexError:
                        pass
                    try:
                        setattr(df, "subtitle", df.columns[5])
                        setattr(df, "get_subtitle", MethodType(get_subtitle, df))
                    except IndexError:
                        pass

                    setattr(self, table_name, df)
                    successes = successes + 1
                    log.debug(f"{self}: Read {table_name} from database")
                except pd.errors.DatabaseError:
                    log.debug(f"{self}: Table {table_name} doesn't exist, keeping empty DataFrame")

            if successes == 0:
                log.warning(f"{self}: No _tables were successfully registered. "
                            f"This probably means the database is empty. Attempting to write...")
                self._commit()
            else: log.success(f"{self}: Successfully loaded {successes} _tables from {self._path}")

    def _commit(self):
        self._backup()
        with sqlite3.connect(self._path) as conn:
            for table_name, table_df in self._tables.items():
                table_df.to_sql(table_name, conn, if_exists='replace', index=False)
                log.debug(f"{self}: Wrote {table_name} to database")

    def create(self, table_name: str, signature: str = "system", **kwargs):
        start_time = time.time()
        try:
            table = getattr(self, table_name)
            unique_keys = self._unique_keys[table_name]

            if unique_keys:
                for key in unique_keys:
                    if key in kwargs and not table.empty and kwargs[key] in table[key].values:
                        return self.update(table_name, kwargs, signature, **{key: kwargs[key]})

            new_idx = len(table)

            # Set audit columns
            table.loc[new_idx, 'created_at'] = pd.Timestamp.now()
            table.loc[new_idx, 'created_by'] = signature
            table.loc[new_idx, 'modified_at'] = pd.Timestamp.now()
            table.loc[new_idx, 'modified_by'] = signature

            for col, value in kwargs.items():
                table.loc[new_idx, col] = value
            self._pkl.log_change(signature, table_name, "create")
            elapsed = time.time() - start_time
            log.debug(f"Created row in {table_name}: {kwargs} (took {elapsed:.4f}s)")
            return table
        except Exception:
            raise

    def read(self, table_name: str, **conditions):
        start_time = time.time()
        try:
            table = getattr(self, table_name)

            if not conditions:
                elapsed = time.time() - start_time
                log.debug(f"Read all {len(table)} rows from {table_name} (took {elapsed:.4f}s)")
                return table

            mask = pd.Series([True] * len(table))
            for col, value in conditions.items():
                mask &= (table[col] == value)

            result = table[mask]
            elapsed = time.time() - start_time
            log.debug(f"Read {len(result)} rows from {table_name} (took {elapsed:.4f}s)")
            return result
        except Exception:
            raise

    def update(self, table_name: str, updates: dict, signature: str = "system", **conditions):
        start_time = time.time()
        try:
            table = getattr(self, table_name).copy()

            mask = pd.Series([True] * len(table))
            for col, value in conditions.items():
                mask &= (table[col] == value)

            # Set audit columns
            table.loc[mask, 'modified_at'] = pd.Timestamp.now()
            table.loc[mask, 'modified_by'] = signature

            for col, value in updates.items():
                table.loc[mask, col] = value

            setattr(self, table_name, table)
            updated_count = mask.sum()
            self._pkl.log_change(signature, table_name, "update")
            elapsed = time.time() - start_time
            log.debug(f"Updated {updated_count} rows in {table_name} by {signature} (took {elapsed:.4f}s)")
            return table
        except Exception:
            raise

    def delete(self, table_name: str, signature: str = "system", **conditions):
        start_time = time.time()
        try:
            table = getattr(self, table_name)

            mask = pd.Series([True] * len(table))
            for col, value in conditions.items():
                mask &= (table[col] == value)

            result = table[~mask].reset_index(drop=True)
            setattr(self, table_name, result)
            deleted_count = len(table) - len(result)
            self._pkl.log_change(signature, table_name, "delete")
            elapsed = time.time() - start_time
            log.debug(f"Deleted {deleted_count} rows from {table_name} by {signature} (took {elapsed:.4f}s)")
            return result
        except Exception:
            raise

    # @cached_property
    # def _api(self):
    #     from toomanysessions import SessionedServer
    #
    #     class API(SessionedServer):
    #         def __init__(self, db: Database):
    #             super().__init__(
    #                 authentication_model="pass",
    #                 user_model=None
    #             )
    #             self.db = db
    #             self.templater = FastJ2(error_method=self.renderer_error, cwd=Path(__file__).parent)
    #             self.include_router(self.admin_routes)
    #             self.include_router(self.json_routes)
    #
    #         @cached_property
    #         def json_routes(self):
    #             from .routers import JSON
    #             return JSON(self)
    #
    #         @cached_property
    #         def admin_routes(self):
    #             from .routers import Admin
    #             return Admin(self)
    #
    #     return API

Database.c = Database.create
Database.r = Database.read
Database.u = Database.update
Database.d = Database.delete

# def _compare(self, table_name: str, old: DataFrame, new: DataFrame, signature: str):
#     """Compare old vs new DataFrame and log changes"""
#     if old.equals(new):
#         log.debug(f"{self}: No changes in {table_name}")
#         self._pkl.log_change(table_name, "no_change", signature)
#         return
#
#     # Changes detected
#     if old.shape == new.shape and (old.columns == new.columns).all():
#         # Same structure, show detailed diff
#         diff = old.compare(new)
#         if not diff.empty:
#             log.info(f"{self}: Changes in {table_name}:")
#             print(diff)
#             self._pkl.log_change(table_name, "updated", signature, f"Cell changes: {len(diff)} rows")
#     else:
#         # Structure changed
#         row_diff = new.shape[0] - old.shape[0]
#         if row_diff > 0:
#             change_type = "rows_added"
#         elif row_diff < 0:
#             change_type = "rows_deleted"
#         else:
#             change_type = "structure_changed"
#
#         log.info(f"{self}: Shape/structure changed in {table_name}: {old.shape} -> {new.shape}")
#         self._pkl.log_change(table_name, change_type, signature, f"{old.shape} -> {new.shape}")