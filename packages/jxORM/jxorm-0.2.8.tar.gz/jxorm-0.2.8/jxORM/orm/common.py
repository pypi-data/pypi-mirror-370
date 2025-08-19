#!/usr/bin/python
# -*- coding: UTF-8 -*-

import traceback
import datetime
import json

from functools import wraps
from threading import RLock
import datetime
import enum

from jxORM.orm.jxUtils import logger, checkAssert, transValue2Datetime, transValue2Dict, transValue2String, stringAdd, trip_quotes

class DBType(enum.IntEnum):
    No = 0
    SQLite = 1
    MySQL = 2

    @classmethod
    def from_string(cls, s):
        if s == 'mysql':
            return DBType.MySQL
        if s == 'sqlite':
            return DBType.SQLite
        return DBType.No

class ColType(enum.IntEnum):
    PrimaryKey = 0
    Index = 1

class DBDataType(enum.IntEnum):
    No = -1
    Int = 1
    Long = 2
    Float = 3
    Double = 4
    Bool = 5
    Chars = 6
    String = 7
    DateTime = 8
    Json = 9

    @classmethod
    def trans_from_type(cls, tys):
        if isinstance(tys, DBDataType):
            return tys
        if isinstance(tys, str):
            ss = tys.split('.')
            if len(ss) == 2 and ss[0] == 'DBDataType':
                return cls.from_string(ss[1].lower())
        return DBDataType.No

    @classmethod
    def from_string(cls, s):
        if s == 'int':
            return DBDataType.Int
        if s == 'long':
            return DBDataType.Long
        if s == 'float':
            return DBDataType.Float
        if s == 'double':
            return DBDataType.Double
        if s == 'bool':
            return DBDataType.Bool
        if s == 'chars':
            return DBDataType.Chars
        if s == 'string':
            return DBDataType.String
        if s == 'datetime':
            return DBDataType.DateTime
        if s == 'json':
            return DBDataType.Json
        return DBDataType.No


_dbConfig = {}
_db_create_funcs = {}
_dbPool = {}
_db_name = None
def set_default_db(dbName):
    global _db_name
    _db_name = dbName
def get_default_dbname():
    return _db_name
def register_create_db(db_type, func):
    _db_create_funcs[db_type] = func
def get_ty(cl, attr):
    for c in cl:
        dt = c.get_ty_with_field(attr)
        if dt is not None:
            return dt
    return None
def get_db_result(result_list, descriptions, cls_list:list, need_trans=True):
    if result_list is None:
        return None
    if not need_trans or descriptions is None:
        return result_list
    column_names = [description[0] for description in descriptions]
    rs = []
    for r in result_list:
        result = dict(zip(column_names, r))
        d = {}
        rs.append(d)
        for k, v in result.items():
            dt = get_ty(cls_list, k)
            if dt is not None:
                d[k] = transFromDB(dt, v)
                continue
            d[k] = v
    return rs

def transFromDB(dt: DBDataType, dv):
    if dt == DBDataType.Int:
        return int(dv)
    if dt == DBDataType.Long:
        return int(dv)
    if dt == DBDataType.Float:
        return float(dv)
    if dt == DBDataType.Double:
        return float(dv)
    if dt == DBDataType.Bool:
        try:
            return bool(dv)
        except:
            return False
    if dt == DBDataType.String:
        s = str(dv)
        return trip_quotes(s)
    if dt == DBDataType.Chars:
        s = str(dv)
        return trip_quotes(s)
    if dt == DBDataType.DateTime:
        if isinstance(dv, str):
            dv = trip_quotes(dv)
        return transValue2Datetime(dv)
    if dt == DBDataType.Json:
        if isinstance(dv, str) and (dv.startswith('"') or dv.startswith("'")):
            dv = dv[1:-1]
        return transValue2Dict(dv)
    return None

def transToDB(dt: DBDataType, dv):
    if dt == DBDataType.Int:
        return int(dv)
    elif dt == DBDataType.Long:
        return int(dv)
    elif dt == DBDataType.Float:
        return float(dv)
    elif dt == DBDataType.Double:
        return float(dv)
    elif dt == DBDataType.Bool:
        try:
            b = bool(dv)
            if b:
                return 1
            return 0
        except:
            return 0
    elif dt == DBDataType.String:
        return f'\"{str(dv)}\"'
    elif dt == DBDataType.Chars:
        return f'\"{str(dv)}\"'
    elif dt == DBDataType.DateTime:
        if isinstance(dv, datetime.datetime):
            return f'\"{dv.strftime("%Y-%m-%d %H:%M:%S")}\"'
        elif isinstance(dv, str):
            return f'\"{dv}\"'
        else:
            try:
                dv = int(dv)
                dt = datetime.datetime.fromtimestamp(dv)
                return f'\"{dt.strftime("%Y-%m-%d %H:%M:%S")}\"'
            except:
                return ''
    elif dt == DBDataType.Json:
        s = json.dumps(dv)
        return f"'{s}'"
    return None

class jxDB:
    @classmethod
    def set(cls, dbName, type=DBType.MySQL, is_default=True, host='127.0.0.1', port=3306, user='root', password='root', **kwargs):
        dc = jxDB(type=type, host=host, port=port, user=user, password=password)
        dc.attrs = kwargs
        _dbConfig[dbName] = dc
        if is_default:
            set_default_db(dbName)

    def __init__(self, type=DBType.MySQL, host='127.0.0.1', port=3306, user='root', password='root'):
        self.type = type
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.attrs = {}

class DB_interface:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._name = None

    def type(self):
        # 数据库类型
        return None

    def name(self):
        # 数据库类型
        return self._name

    def need_trans(self):
        return False

    def description(self):
        return None

    def _get_create_table_sql(self, table_name, fields, keys, indexs):
        return []
    def create_table(self, table_name, fields, keys, indexs):
        sl = self._get_create_table_sql(table_name, fields, keys, indexs)
        for sql in sl:
            self.execute(sql)

    def commit(self):
        self.conn.commit()

    def trans_result(self, rl):
        if not self.need_trans():
            return rl
        return get_db_result(rl, self.description(), [], need_trans=True)

    def get_db_type(self, ty):
        return ''

    def rollback(self):
        self.conn.rollback()

    def execute(self, sql):
        logger.info(f'execute sql:{sql}')
        return self.cursor.execute(sql)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def trans2String(self, vt, v):
        return transValue2String(vt, v, withQuote=True, to_db=True)

    def transaction(self):
        return DB_interface._transaction(self)

    def __enter__(self):
        if self.conn is not None:
            self.cursor = self.conn.cursor()
            self.conn.begin()
        return self

    def __exit__(self, type, value, trace):
        if self.conn is not None:
            self.cursor.close()
            self.conn.close()

    class _transaction:
        def __init__(self, db):
            self.db = db
        def __enter__(self):
            self.db.__enter__()
            return self
        def __exit__(self, type, value, trace):
            if type is None:
                self.db.commit()
            else:
                self.db.rollback()
            self.db.__exit__(type, value, trace)

class DB_mysql(DB_interface):
    def __init__(self, dbname):
        super().__init__()
        self._name = dbname
        self._pool = _dbPool.get(dbname)
        if self._pool is None:
            dc = _dbConfig.get(dbname)
            import pymysql
            from dbutils.pooled_db import PooledDB
            config = {
                'creator': pymysql,
                'host': dc.host,
                'port': dc.port,
                'user': dc.user,
                'password': dc.password,
                'db': dbname,
                'charset': "utf8",
                'cursorclass': pymysql.cursors.DictCursor
            }
            config.update(dc.attrs)
            self._pool = PooledDB(**config)
            _dbPool[dbname] = self._pool
        self.conn = self._pool.connection()

    def type(self):
        # 数据库类型
        return 'mysql'

    def get_db_type(self, ty):
        if ty == DBDataType.Int:
            return 'int'
        if ty == DBDataType.Long:
            return 'bigint'
        if ty == DBDataType.Float:
            return 'float'
        if ty == DBDataType.Double:
            return 'double'
        if ty == DBDataType.Bool:
            return 'tinyint'
        if ty == DBDataType.Chars:
            return 'varchar(126)'
        if ty == DBDataType.String:
            return 'mediumtext'
        if ty == DBDataType.DateTime:
            return 'datetime'
        if ty == DBDataType.Json:
            return 'mediumtext'
        return 'mediumtext'

    def _get_create_table_sql(self, table_name, fields, keys, indexs):
        rs = []
        fl = {}
        pk = None
        il = []
        for k, dt in fields.items():
            fs = f'`{k}` {self.get_db_type(dt)} NOT NULL'
            fl[k] = fs
        if len(keys) > 0:
            ks = None
            for k in keys:
                ks = stringAdd(ks, f'`{k}`', ',')
            pk = f'PRIMARY KEY ({ks})'
        if len(indexs) > 0:
            for i, ins in indexs.items():
                ifs = None
                for ikn in ins:
                    ifs = stringAdd(ifs, f'`{ikn}`', ',')
                tis = f'KEY `{table_name}_index_{i}` ({ifs})'
                il.append(tis)
        fs = ','.join(fl.values())
        fs = stringAdd(fs, pk, ',')
        ils = ','.join(il)
        fs = stringAdd(fs, ils, ',')
        cs = f'CREATE TABLE `{table_name}` ({fs}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;'
        rs.append(cs)
        return rs

class DB_sqlite(DB_interface):
    def __init__(self, dbname):
        super().__init__()
        self._name = dbname
        self._pool = _dbPool.get(dbname)
        if self._pool is None:
            import sqlite3
            from dbutils.pooled_db import PooledDB
            config = {
                'creator': sqlite3,
                'mincached': 5,
                'maxcached': 30,
                'check_same_thread': False,
                'database': f'{dbname}.db',
            }
            self._pool = PooledDB(**config)
            _dbPool[dbname] = self._pool
        self.conn = self._pool.connection()

    def type(self):
        # 数据库类型
        return 'sqlite'

    def need_trans(self):
        return True

    def description(self):
        return self.cursor.description

    def get_db_type(self, ty):
        if ty in [DBDataType.Int, DBDataType.Long, DBDataType.Float, DBDataType.Double,DBDataType.Bool]:
            return 'INTEGER'
        return 'TEXT'

    def _get_create_table_sql(self, table_name, fields, keys, indexs):
        rs = []
        fl = {}
        for k, dt in fields.items():
            fs = f'`{k}` {self.get_db_type(dt)} NOT NULL'
            fl[k] = fs

        pk = None
        if len(keys) > 1:
            ks = None
            for k in keys:
                ks = stringAdd(ks, f'`{k}`', ',')
            pk = f'PRIMARY KEY ({ks})'
        else:
            for k in keys:
                fs = fl.get(k, None)
                fs += ' PRIMARY KEY'
                fl[k] = fs
        fls = ','.join(fl.values())
        if pk is not None:
            fls = stringAdd(fls, pk, ',')
        cs = f'CREATE TABLE `{table_name}` ({fls});'
        rs.append(cs)

        for i, il in indexs.items():
            fs = None
            for ikn in il:
                fs = stringAdd(fs, f'`{ikn}`', ',')
            cis = f'CREATE INDEX {table_name}_index_{i} ON {table_name} ({fs});'
            rs.append(cis)
        return rs

def get_default_db():
    return get_db(_db_name)

def get_db(dbname=None):
    if dbname is None:
        dbname = _db_name
    if dbname is not None:
        dc = _dbConfig.get(dbname)
        if dc is not None:
            func = _db_create_funcs.get(dc.type, None)
            if func is not None:
                return func(dbname)
    return None

def dual_with_db(db, dual, *args):
    if db is None:
        db = get_db()
        with db.transaction():
            return dual(db, *args)
    else:
        return dual(db, *args)

def DB(func):
    @wraps(func)
    def wrapper(obj, dbname, *args, **kw):
        db = get_db(dbname)
        checkAssert(not db is None, '数据库未配置:{}', dbname)
        with db:
            try:
                result = func(obj, db, *args, **kw)
                db.commit()
                return result
            except Exception as e:
                db.rollback()
                raise e
    return wrapper

register_create_db(DBType.MySQL, lambda dbname:DB_mysql(dbname))
register_create_db(DBType.SQLite, lambda dbname:DB_sqlite(dbname))
