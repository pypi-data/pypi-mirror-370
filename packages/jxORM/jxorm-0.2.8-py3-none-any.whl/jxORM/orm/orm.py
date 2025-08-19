#!/usr/bin/python
# -*- coding: UTF-8 -*-

import traceback
import datetime
import enum
import re
from functools import wraps

from jxORM.orm.jxUtils import logger, checkAssert, extract_str_from_quotes, GetClsName, CID, Now, is_none, transValue2DB, transValue2Datetime, judgeTimeIsCurrent, getRenameTableName, getDateTime_to, stringAdd, defaultValue
from jxORM.orm.common import DB, DBType, DBDataType, transFromDB, transToDB, get_db_result, ColType


reg_expression = re.compile('\s*(\w+)\s+(==|>|<|<>|>=|<=)\s+(.+)')
def parse_expression(exp):
    ss = exp.split('&')
    rs = []
    for s in ss:
        m = reg_expression.match(s)
        if m:
            sv = m.group(3)
            ins = extract_str_from_quotes(sv, '"')
            if len(ins) == 0:
                ins = extract_str_from_quotes(sv, "'")
            if len(ins) > 0:
                sv = ''.join(ins)
            rs.append((m.group(1), m.group(2), sv))
    return rs
def trans_op(op):
    if op == '==':
        return '='
    return op

_orm_cls_list = {}
_orm_son_cls_list = {}
_orm_parent_cls_list = {}

def get_by_type_id(db, cls_name, id):
    c = _orm_cls_list.get(cls_name, None)
    if c is None:
        return None
    return c.GetByID(db, id)

def get_by_type_name(db, cls_name, name):
    c = _orm_cls_list.get(cls_name, None)
    if c is None:
        return None
    return c.GetByName(db, name)

def list_ancestors(my_name):
    c = _orm_parent_cls_list.get(my_name, None)
    d = []
    while c is not None:
        d.append(c)
        c = _orm_parent_cls_list.get(c.Name(), None)
    return d

def list_descendant(my_name):
    c = _orm_son_cls_list.get(my_name, None)
    d = []
    while c is not None:
        d.append(c)
        c = _orm_son_cls_list.get(c.Name(), None)
    return d
def get_parent_Name(cls):
    pc = cls.__bases__[0]
    pn = GetClsName(pc)
    if pn == 'object':
        return None
    return pn
def get_parent(cls):
    pn = get_parent_Name(cls)
    if pn is None:
        return None
    return _orm_cls_list.get(pn, None)

def get_index(type_hints, dict_list):
    rs = {}
    for k in type_hints:
        v = dict_list.get(k, None)
        if v is None:
            continue
        if isinstance(v, ColType):
            continue
        elif isinstance(v, int):
            l = rs.get(v, None)
            if l is None:
                l = []
                rs[v] = l
            l.append(k)
    return rs


def trans_type_hints_type(type_hints):
    rs = {}
    for k, v in type_hints.items():
        rs[k] = DBDataType.trans_from_type(v)
    return rs

def ORM(cls):
    '''
    @ORM
    class Test:
        #id是主键
        id:DBDataType.Int = ColType.PrimaryKey
        name:DBDataType.String
    '''
    clsName = cls.__name__
    table_alias = f't_{clsName}'
    parent = get_parent(cls)
    parent_list = list_ancestors(clsName)
    type_hints = cls.__annotations__
    type_hints = trans_type_hints_type(type_hints)
    keys = [k for k in type_hints if k in cls.__dict__ and cls.__dict__[k] == ColType.PrimaryKey]
    indexes = get_index(type_hints, cls.__dict__)
    @wraps(cls, updated=())
    class Wrapper(cls):  # 继承原类
        @classmethod
        def Alias(cls):
            return table_alias
        @classmethod
        def Name(cls):
            return clsName
        @classmethod
        def Parent(cls):
            return parent
        @classmethod
        def Fields(cls):
            return type_hints
        @classmethod
        def is_attr(cls, name):
            return name in type_hints
        @classmethod
        def is_key(cls, name):
            return name in keys

        @classmethod
        def get_type(cls, name):
            return type_hints.get(name, None)

        @classmethod
        def get_type_python(cls, name):
            dt = type_hints.get(name, None)
            if dt == DBDataType.Int:
                return int
            elif dt == DBDataType.Float:
                return float
            elif dt == DBDataType.Bool:
                return bool
            elif dt == DBDataType.String:
                return str
            elif dt == DBDataType.DataTime:
                return datetime.datetime
            elif dt == DBDataType.Json:
                return dict
            return None

        @classmethod
        def create(cls, db):
            try:
                db.create_table(clsName, type_hints, keys, indexes)
            except:
                pr = traceback.format_exc()
                logger.error(pr)

        @classmethod
        def get_cls_with_field(cls, scl, field):
            if cls.is_attr(field):
                return cls
            for sc in scl:
                if sc.is_attr(field):
                    return sc
            return None

        @classmethod
        def get_ty_with_field(cls, field):
            dt = cls.get_type(field)
            if dt is not None:
                return dt
            for sc in parent_list:
                dt = sc.get_type(field)
                if dt is not None:
                    return dt
            return None

        @classmethod
        def get_where(cls, expression_list):
            s = None
            for attr, op, v in expression_list:
                dt = type_hints.get(attr, None)
                if dt is None:
                    continue
                if isinstance(v, str):
                    if v[0] == '\'' or v[0] == '"':
                        v = v[1:-1]
                op = trans_op(op)
                if op == 'like':
                    v = f'{v}%'
                ov = transToDB(dt, v)
                s = stringAdd(s, '{}{}{}'.format(f'{table_alias}.{attr}', op, ov), ' AND ')
            return s
        @classmethod
        def get_from(cls):
            s = f'{clsName} as {table_alias}'
            return s
        @classmethod
        def get_select(cls):
            s = f'{table_alias}.*'
            return s

        @classmethod
        def searchBy_expression_list(cls, db, expression_list, offset=0, limit=100):
            fl = type_hints.copy()
            ss = cls.get_select()
            fs = cls.get_from()
            ws = cls.get_where(expression_list)
            for sc in parent_list:
                fl.update(sc.Fields())
                ss = stringAdd(ss, sc.get_select(), ',')
                fs = stringAdd(fs, sc.get_from(), ',')
                ws = stringAdd(ws, f'{table_alias}.ID={sc.Alias()}.ID', ' AND ')
                ws = stringAdd(ws, sc.get_where(expression_list), ' AND ')
            sql1 = f'SELECT {ss} FROM {fs} WHERE {ws}'
            if limit > 0:
                sql = sql1 +f' LIMIT {limit} OFFSET {offset}'
            else:
                sql = sql1
            db.execute(sql)
            rl = db.fetchall()
            return get_db_result(rl, db.description(), [cls], need_trans=db.need_trans())

        @classmethod
        def searchBy(cls, db, expression, offset:int=0, limit:int=100):
            '''
            以等式搜索数据
            '''
            expression_list = parse_expression(expression)
            return cls.searchBy_expression_list(db, expression_list, offset=offset, limit=limit)

        @classmethod
        def getBy(cls, db, expression):
            expression_list = parse_expression(expression)
            return cls._getBy(db, expression_list)

        @classmethod
        def _getBy(cls, db, expression_list):
            rl = cls.searchBy_expression_list(db, expression_list, offset=0, limit=2)
            if len(rl) == 0:
                return None
            checkAssert(len(rl) == 1, f'{clsName}::_getBy[{expression_list}] 查询结果数量不为1')
            return rl[0]

        @classmethod
        def GetByID(cls, db, id):
            expression_list = [('ID', '=', id)]
            return cls._Get(db, expression_list)

        @classmethod
        def GetByName(cls, db, name):
            expression_list = [('Name', '=', name)]
            return cls._Get(db, expression_list)

        @classmethod
        def Get(cls, db, expression):
            expression_list = parse_expression(expression)
            return cls._Get(db, expression_list)

        @classmethod
        def _Get(cls, db, expression_list):
            data = cls._getBy(db, expression_list)
            if data is None:
                return None
            return Wrapper(**data)

        def __init__(self, **kwargs):
            self._data = {}
            self._changed = {}
            self._myInit()
            if len(kwargs) > 0:
                self.set(init=True, **kwargs)

        def _myInit(self):
            #自动设置ID
            self._set(init=True, ID=CID())
            #自动设置创建时间
            self._set(init=True, CreateTime=Now())
            #自动设置创建时间
            self._set(init=True, Timestamp=Now())

        def update(self, db):
            if len(self._changed) == 0:
                return
            Wrapper.my_update_transaction(db, self._data, self._changed)
            for sc in parent_list:
                sc.my_update_transaction(db, self._data, self._changed)
            self._changed = {}

        @classmethod
        def my_update_transaction(cls, db, data, changed):
            checkAssert(len(keys) > 0, '数据对象update必须设置key！！！')
            sql1 = 'UPDATE {} SET '.format(clsName)
            sql2 = ' WHERE '
            s1 = None
            s2 = None
            for attr in changed:
                dt = type_hints.get(attr, None)
                if dt is None:
                    continue
                v = data.get(attr, None)
                if v is None:
                    v = defaultValue(dt)
                s1 = stringAdd(s1, '{}={}'.format(attr, v), ',')
            for attr in keys:
                v = data.get(attr, None)
                checkAssert(not v is None, '键【{}】未设置值', attr)
                s2 = stringAdd(s2, '{}={}'.format(attr, v), ' AND ')
            sql = sql1 + s1 + sql2 + s2

            db.execute(sql)

        def insert(self, db):
            Wrapper.my_insert_transaction(db, self._data)
            for sc in parent_list:
                sc.my_insert_transaction(db, self._data)

        @classmethod
        def my_insert_transaction(cls, db, data):
            sql1 = 'INSERT INTO {}('.format(clsName)
            sql2 = ' VALUES('
            s1 = None
            s2 = None
            for attr, dt in type_hints.items():
                v = data.get(attr, None)
                if is_none(v):
                    v = transToDB(dt, defaultValue(dt))
                s1 = stringAdd(s1, attr, ',')
                s2 = stringAdd(s2, str(v), ',')
            sql1 = sql1 + s1 + ')'
            sql2 = sql2 + s2 + ')'
            sql = sql1 + sql2

            db.execute(sql)

        def data(self):
            rs = {}
            for key, v in self._data.items():
                c = Wrapper.get_cls_with_field(parent_list, key)
                if c is None:
                    continue
                dt = c.get_type(key)
                rs[key] = transFromDB(dt, v)
            return rs

        def _set(self, init=False, **kwargs):
            for key, value in kwargs.items():
                c = Wrapper.get_cls_with_field(parent_list, key)
                if c is None:
                    continue
                if not init:
                    checkAssert(not c.is_key(key), f'{clsName}::_set[{key}] 不支持设置主键')
                dt = c.get_type(key)
                if dt is not None:
                    self._data[key] = transToDB(dt, value)
                    if not init:
                        self._changed[key] = True

        def set(self, **kwargs):
            self._set(**kwargs)

        def get(self, name):
            c = Wrapper.get_cls_with_field(parent_list, name)
            if c is not None:
                d = super().__getattribute__('_data')
                dv = d.get(name)
                dt = c.get_type(name)
                return transFromDB(dt, dv)
            return None

        def __getattribute__(self, name):
            c = Wrapper.get_cls_with_field(parent_list, name)
            if c is not None:
                d = super().__getattribute__('_data')
                dv = d.get(name)
                dt = c.get_type(name)
                return transFromDB(dt, dv)
            f = super().__getattribute__(name)
            if f is not None:
                return f
            return None

        def __setattr__(self, name, value):
            c = Wrapper.get_cls_with_field(parent_list, name)
            if c is None:
                super().__setattr__(name, value)
                return
            checkAssert(not c.is_key(name), f'{clsName}::_setattr[{name}] 不支持设置主键')
            dt = c.get_type(name)
            self._data[name] = transToDB(dt, value)
            self._changed[name] = True

    _orm_cls_list[clsName] = Wrapper
    if parent is not None:
        _orm_son_cls_list[parent.Name()] = Wrapper
        _orm_parent_cls_list[clsName] = parent
    return Wrapper

reg_from = re.compile('\s*(\w+)(\s+[as|AS]\s+(\w+))?')
def extract_from_simple(sql):
    rs = []
    bsql = sql.upper()
    from_index = bsql.find("FROM")
    where_index = bsql.find("WHERE")
    fs = sql[from_index+5:where_index]
    ss = fs.split(',')
    for s in ss:
        s = s.strip()
        m = reg_expression.match(s)
        if m:
            rs.append(m.group(1))
    return rs

def select(db, sql:str, need_trans=True):
    bsql = sql.upper().strip()
    bss = bsql.split(' ')
    checkAssert(bss[0] == 'SELECT', 'select只支持SELECT语句')
    cls_list = []
    if need_trans:
        fl = extract_from_simple(sql)
        for f in fl:
            c = _orm_cls_list.get(f, None)
            if c is not None:
                cls_list.append(c)
    db.execute(sql)
    rl = db.fetchall()
    return get_db_result(rl, db.description(), cls_list, need_trans=need_trans and db.need_trans())


