#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import threading
import types
import time
import random
import datetime
import json
import traceback
from threading import RLock
from decimal import *
from enum import Enum

import base64
import pytz

import logging
from logging.handlers import RotatingFileHandler

class ValueType(Enum):
    none = 'none'
    string = 'string'
    int = 'int'
    float = 'float'
    datetime = 'datetime'
    bool = 'bool'
    json = 'json'

    @classmethod
    def to_string(cls, tys):
        if not isinstance(tys, str):
            s = str(tys)
        else:
            s = tys
        ss = s.split('.')
        if len(ss) == 2 and ss[0] == 'ValueType':
            return ss[1]
        return s

    @staticmethod
    def from_string(s:str):
        try:
            return ValueType[s.lower()]
        except:
            return ValueType.none

'''
_func_get_user：
    传入参数：
        user：用户名
        pwd：密码
    返回值：
        用户
用户类要求具有如下的方法：
    #用户名
    def name(self):
        return self.name
    #用户名可能会重复，所以起一个本公司唯一的简称名
    def abbr(self):
        return self.abbr
    #用户所有的角色【包括一级角色，如技术部经理；二级角色，如经理】
    def roles(self):
        return self.roles
'''

class User:
    def __init__(self, name):
        self._name = name
        self._abbr = name
        self._roles = [ ]

    def name(self):
        return self._name
    def abbr(self):
        return self._abbr
    def roles(self):
        return self._roles

_func_get_user = None
def set_func_get_user(func):
    global _func_get_user
    _func_get_user = func
def get_user(user, pwd):
    if _func_get_user is not None:
        return _func_get_user(user, pwd)
    return User(user)


int_Max = 0x7ffffff
tz = pytz.timezone('Asia/Shanghai')

hostID = 1
def set_host_id(id):
    global hostID
    hostID = id

hostName = 'JingXi'
mask_hostID = (hostID & 0xFFFF) << 48
mask_ts = 0xFFFFFFFF
myID = 0

_LOG_FORMAT = "%(asctime)s [%(filename)s %(lineno)s] - %(levelname)s - %(message)s"
_LOG_maxBytes = 512 * 1024 * 1024
#rolling日志文件的备份数
_LOG_backupCount = 30

private_key_path = '../../secure/privateKey.pem'
_log_name = 'web.log'

_rsa_decryptor = None
def get_rsa_decryptor():
    global _rsa_decryptor
    if _rsa_decryptor is None:
        _rsa_decryptor = RSA_Decryptor(private_key_path)
    return _rsa_decryptor

_allObjCanClear = {}


def _asyncExec(func):
    try:
        func()
    except:
        pr = traceback.format_exc()
        logger.error(pr)
def asyncExec(func):
    threading.Thread(target=_asyncExec, args=[func]).start()

def list_methods(obj):
    return [m for m in dir(obj) if not m.startswith("__")]

def list_methods_cls(cls, mothod_type='instance'):
    import inspect
    all_methods = inspect.getmembers(cls, predicate=inspect.isfunction)
    if mothod_type is None:
        return all_methods
    elif mothod_type == 'instance':
        return {
            name: method
            for name, method in all_methods
            if isinstance(method, types.FunctionType)
            and not name.startswith("__")  # 排除特殊方法
        }
    elif mothod_type == 'classmethod':
        return {
            name: method
            for name, method in all_methods
            if isinstance(method, classmethod)
            and not name.startswith("__")  # 排除特殊方法
        }
    return {
        name: method
        for name, method in all_methods
        if isinstance(method, staticmethod)
        and not name.startswith("__")  # 排除特殊方法
    }
def trip_quotes(s):
    ins = extract_str_from_quotes(s, '"')
    if len(ins) == 0:
        ins = extract_str_from_quotes(s, "'")
    if len(ins) > 0:
        s = ''.join(ins)
    return s
def extract_str_from_quotes(s, quote):
    result = []
    inside = False

    for char in s:
        if char == quote and not inside:
            inside = True
        elif char == quote and inside:
            break
        elif inside:
            result.append(char)

    return result

def is_none(v):
    if v is None:
        return True
    if isinstance(v, str) and len(v) > 0:
        if v[0] == '"' or v[0] == "'":
            v = v[1:-1]
        if v == 'None':
            return True
    return False


def stringAdd(str, want, split=','):
    if str is None:
        return want
    if want is None:
        return str
    return str + split + want
def defaultValue(ty):
    from jxORM.orm.common import DBDataType
    if ty == 'int' or ty == DBDataType.Int:
        return 0
    if ty == 'long' or ty == DBDataType.Long:
        return 0
    if ty == 'float' or ty == DBDataType.Float:
        return 0.0
    if ty == 'double' or ty == DBDataType.Double:
        return 0.0
    if ty == 'chars' or ty == DBDataType.Chars:
        return ''
    if ty == 'string' or ty == DBDataType.String:
        return ''
    if ty == 'bool' or ty == DBDataType.Bool:
        return False
    if ty == 'decimal':
        return Decimal.from_float(0.0)
    if ty == 'datetime' or ty == DBDataType.DateTime:
        return '1970-01-01 00:00:00'
    if ty == 'json' or ty == DBDataType.Json:
        return {}
    return None
def base64_decode(msg):
    # 将Base64编码的字符串转换为字节形式
    # 将字符串转换为字节格式
    msg_bytes = msg.encode('utf-8')
    encoded_bytes = base64.b64decode(msg_bytes)
    # 将编码的字节形式转换为字符串并返回
    return encoded_bytes.decode('utf-8')

def base64_encode(msg):
    # 将字符串转换为字节格式
    msg_bytes = msg.encode('utf-8')
    # 执行Base64编码
    encoded_bytes = base64.b64encode(msg_bytes)
    # 将编码的字节形式转换为字符串并返回
    return encoded_bytes.decode('utf-8')

def GetClsName(cls):
    cn = cls.__name__
    cs = cn.split('.')
    return cs[-1]
def StringIsEmpty(str):
    if str is None:
        return True
    if str == '':
        return True
    return False
def CID():
    global myID
    if myID > int_Max:
        myID = 1
    else:
        myID = myID + 1
    t = time.time()
    ts = int(round(t * 1000))
    return mask_hostID | (((ts >> 10) & mask_ts) << 16) | (myID & 0x0000FFFF)
def Now():
    dt = datetime.datetime.now(tz)
    return dt
def checkAssert(b,msg,*vs):
    if not b:
        if len(vs) == 0:
            raise Exception(msg)
        else:
            raise Exception(msg.format(*vs))
def getLogger(loggerName):
    logger = logging.getLogger(loggerName)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(_LOG_FORMAT)
    fh = RotatingFileHandler(f"logs/{loggerName}", maxBytes=_LOG_maxBytes, backupCount=_LOG_backupCount)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    return logger

def waitClear(name, objCanClear):
    logger.info(f'添加可清理对象：{name}')
    co = _allObjCanClear.get(name, None)
    checkAssert(co is None, f'已经添加过可清理对象【{name}')
    _allObjCanClear[name] = objCanClear
def getClearObj(name):
    return _allObjCanClear.get(name, None)
def clearObj(name):
    logger.info(f'清理对象：{name}')
    co = _allObjCanClear.pop(name, None)
    if co is not None:
        co.clear()
def transValue2Number(str):
    try:
        s = str.index('.')
        return float(str)
    except:
        return transValue2Int(str)
def transValue2Int(v):
    if v is None:
        return 0
    try:
        return int(v)
    except:
        return 0
#
#目前只用于sql条件添加，所以送入的值都应该是字符串类型
#
def transValue2String(vt, v, withQuote=False, to_db=False):
    if v is None:
        return None
    vt = ValueType.to_string(vt)
    if vt == 'bool' or vt == ValueType.bool:
        v = bool(v)
        if to_db:
            if v:
                return '1'
            return '0'
        return '{}'.format(v).lower()
    if vt == 'int' or vt == ValueType.int:
        v = int(v)
        return '{}'.format(v)
    if vt == 'float' or vt == ValueType.float:
        v = float(v)
        return '{}'.format(v)
    if vt == 'string' or vt == 'datetime' or vt == ValueType.string or vt == ValueType.datetime:
        v = str(v)
        if withQuote:
            return '\'{}\''.format(v)
        else:
            return v
    return ''
def transValue2DB(v):
    if v is None:
        return None
    if isinstance(v,bool):
        if v:
            return '1'
        return '0'
    if isinstance(v,int):
        return '{}'.format(v)
    if isinstance(v,float):
        return '{}'.format(v)
    if isinstance(v,dict):
        try:
            jvs = json.dumps(v)
        except:
            jvs = ''
        return '\'{}\''.format(jvs)
    if isinstance(v,str):
        return '\'{}\''.format(v)
    if isinstance(v,Decimal):
        return str(v)
    if isinstance(v,datetime.datetime):
        return '\'{}\''.format(v.timestamp())
    return None
#32位系统中最大的秒数，如果用datetime.max，由于太大，会报错：ValueError: year 10000 is out of range
_DataTime_max_second = 2147483647
def transValue2Datetime(v):
    if v is None:
        return None
    if isinstance(v,datetime.datetime):
        return v
    if isinstance(v, float) or isinstance(v, int):
        #v = int(v)
        if v > _DataTime_max_second:
            v = v / 1000
        dt = datetime.datetime.fromtimestamp(v).replace(tzinfo=tz)
        return dt
    if isinstance(v,str):
        dt = datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return dt.astimezone(tz)
    return None
def transValue2Dict(v):
    if v is None:
        return {}
    if isinstance(v,dict):
        return v
    if isinstance(v,str):
        try:
            return json.loads(v)
        except:
            return {}
    return {}
def judgeTimeIsCurrent(dtCurrent, dt, renameType='day'):
    if renameType == 'day':
        return dtCurrent.year == dt.year and dtCurrent.month == dt.month and dtCurrent.day == dt.day
    elif renameType == 'month':
        dtfrom = transValue2Datetime(f'{dtCurrent.year}-{dtCurrent.month}-1 00:00:00')
        if dtCurrent.month == 12:
            dtto = transValue2Datetime(f'{dtCurrent.year+1}-1-1 00:00:00')
        else:
            dtto = transValue2Datetime(f'{dtCurrent.year}-{dtCurrent.month+1}-1 00:00:00')
    else:
        dtfrom = transValue2Datetime(f'{dtCurrent.year}-1-1 00:00:00')
        dtto = transValue2Datetime(f'{dtCurrent.year+1}-1-1 00:00:00')
    return dtfrom<=dt and dt<dtto
def getRenameTableName(tableName, dt, renameType='day'):
    if renameType == 'day':
        return f'{tableName}_{dt.year}_{dt.month}_{dt.day}'
    if renameType == 'month':
        return f'{tableName}_{dt.year}_{dt.month}'
    if renameType == 'year':
        return f'{tableName}_{dt.year}'
    return None
def getDateTime_from(dt, renameType='day'):
    if renameType == 'day':
        dtfrom = transValue2Datetime(f'{dt.year}-{dt.month}-{dt.day} 00:00:00')
    elif renameType == 'month':
        dtfrom = transValue2Datetime(f'{dt.year}-{dt.month}-{1} 00:00:00')
    else:
        dtfrom = transValue2Datetime(f'{dt.year}-{1}-{1} 00:00:00')
    return dtfrom
def getDateTime_to(dt, renameType='day'):
    if renameType == 'day':
        one = datetime.timedelta(days=1)
        dtfrom = getDateTime_from(dt,renameType='day')
        dtto = dtfrom + one
    elif renameType == 'month':
        if dt.month == 12:
            dtto = transValue2Datetime(f'{dt.year+1}-1-1 00:00:00')
        else:
            dtto = transValue2Datetime(f'{dt.year}-{dt.month+1}-1 00:00:00')
    else:
        dtto = transValue2Datetime(f'{dt.year+1}-1-1 00:00:00')
    return dtto

logger = getLogger('jxORM.log')
