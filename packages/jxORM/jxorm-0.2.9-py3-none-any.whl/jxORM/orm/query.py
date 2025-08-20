#!/usr/bin/python
# -*- coding: UTF-8 -*-


from jxORM.orm.jxUtils import checkAssert, Now, transValue2DB, transValue2Datetime, judgeTimeIsCurrent, getRenameTableName, getDateTime_to
#from jxORM.orm.common import DB, DBType, #get_db_type
from jxORM.orm.common import DB, DBType
from jxORM.orm.orm import ORM

# 支持分表【不支持按周】的、for循环查表【单表】
# 使用方法：
# s = query(dbname)
#
# 设置分表信息，如果其中有的表是分表的话
# s.setRename
#
# 添加要查询的表
# s.addTable(table1,fieldPrefix='user')
# s.addTable(table2,fieldPrefix='demo')
#
# 添加查询条件
# s.addTableJoin
# s.Equal
# s.GreatEqual
# 如果使用到了分表，则一定要有其分表字段上的GreatEqual、Great
# 否则无法判断要从哪开始查询
#
# 准备查询
# s.start()
#
# 开始查询
# for d in s:
#
class query:
    def __init__(self, dbname, limit=15):
        self._dbname = dbname
        self._dbtype = None #get_db_type(dbname)
        self._tables = {}
        # 当前表查询结束
        self._queryCurrentTable = False

        self._limit = limit
        self._offset = 0
        self._data = []
        # 比较的条件
        self._conditionCompare = None
        self._conditionCompare_join = None
        self._sql = None
        self._sqlTemple = None
        self._sql_exec = None

        # 是否需要分表
        self._renameType = None
        self._currentTable = None
        # 需要分表的表名
        self._renameTalbeName = None
        # 需要分表的表别名
        self._renameTalbeAlias = None
        # 判断分表的时间字段
        self._renameJudgeByField = None
        # 分表时，查询顺序是按时间的升序、还是降序，默认升序
        self._renameDec = False
        self._renameMin = None
        self._renameMax = None
        # 所有涉及到的分表
        self._renameTalbe = []

        self._orderBy = ''

    def set_limit(self, limit):
        self._limit = limit

    def set_sql(self, sql):
        self._sql_exec = sql

    def setRename(self, renameTalbeName, renameType='day', renameJudgeByField='CreateTime', renameDec=False):
        self._renameType = renameType
        self._renameTalbeName = renameTalbeName
        self._renameJudgeByField = renameJudgeByField
        self._renameDec = renameDec

    # fieldPrefix:本表各列查出的数据添加什么样的前缀，fieldPrefix='user'，ID则为userID
    # wantSelectFields:希望查询哪些列，没有则全部查询
    def addTable(self, clsName, fieldPrefix=None, wantSelectFields=[]):
        tc = ORM.getCls(clsName)
        checkAssert(not tc is None, '需searchBy查询的数据类【{}】应先注册', clsName)
        t = {}
        t['clsName'] = clsName
        t['cls'] = tc
        if fieldPrefix is None:
            fieldPrefix = f't{len(self._tables)}'
        t['fieldPrefix'] = fieldPrefix
        al = tc.__dict__['_ormAttr']
        fl = []
        if not wantSelectFields is None:
            if len(wantSelectFields) == 0:
                for attr in al:
                    fa = {'col': attr, 'alias': f'{fieldPrefix}{attr}'}
                    fl.append(fa)
            else:
                for attr in wantSelectFields:
                    checkAssert(attr in al, '条件键名【{}】不在数据类【{}】属性列表中', attr, clsName)
                    fa = {'col': attr, 'alias': f'{fieldPrefix}{attr}'}
                    fl.append(fa)

        t['fields'] = fl
        self._tables[fieldPrefix] = t

        if not self._renameTalbeName is None and self._renameTalbeName == clsName:
            self._renameTalbeAlias = fieldPrefix

        return fieldPrefix

    def set_order_by(self, tableAlias1, field, desc=False):
        self._orderBy = f' ORDER BY {tableAlias1}.{field} '
        if desc:
            self._orderBy += 'DESC '

    def _getSelect_count(self):
        return 'Select Count(1) totalCount '

    def _getSelect(self):
        ss = None
        for ta in self._tables:
            t = self._tables[ta]
            fl = t['fields']
            for f in fl:
                if ss is None:
                    ss = f'{ta}.{f["col"]} AS {f["alias"]}'
                else:
                    ss = ss + f', {ta}.{f["col"]} AS {f["alias"]}'
        return ss

    def _getFrom(self):
        sf = None
        for ta in self._tables:
            if not self._renameTalbeAlias is None and self._renameTalbeAlias == ta:
                tn = '--renameTalbeName--'
            else:
                t = self._tables[ta]
                tn = t['clsName']
            if sf is None:
                sf = f'{tn} AS {ta}'
            else:
                sf = sf + f', {tn} AS {ta}'
        return sf

    # 多表时两个表的连接条件
    def addTableJoin(self, tableAlias1, field1, tableAlias2, field2):
        co1 = self._tables.get(tableAlias1, None)
        checkAssert(not co1 is None, '表别名尚未定义：{}', tableAlias1)
        fty1 = co1['cls'].__dict__['_ormAttr'].get(field1)
        cn1 = co1['clsName']
        checkAssert(not fty1 is None, '【{}】不在数据类【{}】属性列表中', field1, cn1)
        co2 = self._tables.get(tableAlias2, None)
        checkAssert(not co2 is None, '表别名尚未定义：{}', tableAlias2)
        fty2 = co2['cls'].__dict__['_ormAttr'].get(field2)
        cn2 = co2['clsName']
        checkAssert(not fty2 is None, '【{}】不在数据类【{}】属性列表中', field2, cn2)
        checkAssert(fty1 == fty2, '【{}.{}】的类型【{}】和【{}.{}】的类型【{}】不同',
                            cn1, field1, fty1, cn2, field2, fty2)

        if self._conditionCompare_join is None:
            self._conditionCompare_join = f'{tableAlias1}.{field1}={tableAlias2}.{field2}'
        else:
            self._conditionCompare_join = self._conditionCompare_join + f' AND {tableAlias1}.{field1}={tableAlias2}.{field2}'

        self._conditionCompare = self._conditionCompare_join

        return self

    def ClearCondition(self):
        self._conditionCompare = self._conditionCompare_join

    def Equal(self, clsAlias, field, value):
        self._addCompare(clsAlias, field, '=', value)
        return self

    def NoEqual(self, clsAlias, field, value):
        self._addCompare(clsAlias, field, '<>', value)
        return self

    def GreatEqual(self, clsAlias, field, value):
        self._addCompare(clsAlias, field, '>=', value)
        return self

    def Great(self, clsAlias, field, value):
        self._addCompare(clsAlias, field, '>', value)
        return self

    def LessEqual(self, clsAlias, field, value):
        self._addCompare(clsAlias, field, '<=', value)
        return self

    def Less(self, clsAlias, field, value):
        self._addCompare(clsAlias, field, '<', value)
        return self

    # 全文匹配
    def Match(self, clsAlias, field, value):
        self._addCompare(clsAlias, field, 'match', value)
        return self

    def _addCompare(self, clsAlias, field, op, value):
        co = self._tables.get(clsAlias, None)
        checkAssert(not co is None, '表别名尚未定义：{}', clsAlias)
        tan = co.get('claName', None)
        tc = co.get('cls', None)
        al = tc.__dict__['_ormAttr']
        ft = al.get(field, None)
        checkAssert(not ft is None, '条件属性【{}】不在数据类【{}】属性列表中', field, tan)

        if ft == 'datetime':
            value = transValue2Datetime(value)
            if field == self._renameJudgeByField:
                if op == '<' or op == '<=':
                    self._renameMax = value
                elif op == '>' or op == '>=':
                    self._renameMin = value
                else:
                    raise Exception('时间字段的比较应该是：<、<=、>、>=')

        fvs = transValue2DB(value)

        if op == 'match':
            ct = f'MATCH ({clsAlias}.{field}) AGAINST ("{fvs}")'
        else:
            ct = f'{clsAlias}.{field}{op}{fvs}'

        if self._conditionCompare is None:
            self._conditionCompare = ct
        else:
            self._conditionCompare = f'{self._conditionCompare} AND {ct}'

    def start(self):
        self._offset = 0
        self._sql = None
        self._sqlTemple = None
        self._queryCurrentTable = True
        if self._renameTalbeName is None:
            return
        checkAssert(not self._renameMin is None, '【{}】分表，必须指定查询开始时间', self._renameTalbeName)
        current = Now()
        if self._renameMax is None:
            max = current
        else:
            max = self._renameMax

        dt = self._renameMin
        while dt < max:
            b = judgeTimeIsCurrent(current, dt, renameType=self._renameType)
            if b:
                tn = self._renameTalbeName
            else:
                tn = getRenameTableName(self._renameTalbeName, dt, renameType=self._renameType)
            self._renameTalbe.append(tn)
            dt = getDateTime_to(dt, renameType=self._renameType)

        if self._renameDec:
            # 要求降序
            self._renameTalbe.reverse()

    def _doSearch(self):
        while True:
            if not self._renameTalbeAlias is None:
                if self._currentTable is None:
                    if len(self._renameTalbe) == 0:
                        return False
                    self._currentTable = self._renameTalbe.pop(0)
                    self._queryCurrentTable = True
                    # 开始新表
                    self._offset = 0
                    self._sql = None
            b, rc = self._search(self._dbname)
            if b:
                return True
            # 当前表已经查完了，这时有两种可能：self._data中有数据或没有
            if not self._renameTalbeAlias is None:
                if len(self._renameTalbe) == 0:
                    self._currentTable = None
                else:
                    self._currentTable = self._renameTalbe.pop(0)
                self._queryCurrentTable = True
                # 开始新表
                self._offset = 0
                self._sql = None
            if len(self._data) > 0:
                # 有数据
                return True
            if self._renameTalbeAlias is None:
                # 单表就直接结束，带分表则还需要检查是否还有其它分表
                return False

    def totalCount(self):
        total = 0
        self.start()
        if len(self._renameTalbe) > 0:
            for tn in self._renameTalbe:
                n = self._getCount(self._dbname, tn)
                total = total + n[0]
        else:
            total = self._getCount(self._dbname, None)[0]
        return total

    @DB
    def _getCount(self, db, tn):
        sf = self._getFrom()
        if self._conditionCompare is None:
            st = f'Select Count(1) totalCount FROM {sf}'
        else:
            st = f'Select Count(1) totalCount FROM {sf} WHERE {self._conditionCompare}'
        if not self._renameTalbeAlias is None:
            sql = st.replace('--renameTalbeName--', tn)
        else:
            sql = st

        try:
            db.cursor.execute(sql)
        except Exception as e:
            errMsg = str(e)
            if 'Table ' in errMsg and " doesn't exist" in errMsg:
                return 0
        rs = db.cursor.fetchone()
        return rs.get('totalCount', 0)

    def list(self, offset=None, remove_prefix=False):
        self._data = []
        if offset is not None:
            self._offset = offset
        self._list(self._dbname)
        if remove_prefix:
            rs = []
            for rd in self._data:
                d = {}
                for k, v in rd:
                    ks = k.split('__')
                    if len(ks) == 2:
                        k = ks[1]
                    d[k] = v
                rs.append(d)
            self._data = rs
        return self._data

    def get(self, remove_prefix=False):
        self._data = []
        self._offset = 0
        rs = self.list(self._dbname, remove_prefix=remove_prefix)
        if len(rs) == 0:
            return None
        return rs[0]

    def list2(self, offset=None):
        self._data = []
        if offset is not None:
            self._offset = offset
        self._list(self._dbname)
        return self._data

    def count(self):
        return self._getCount(self._dbname, None)[0]

    @DB
    def _list(self, db):
        if self._sql is None:
            if self._sql_exec is not None:
                self._sql = f'{self._sql_exec} {self._orderBy}LIMIT {self._limit}'
            else:
                if self._sqlTemple is None:
                    ss = self._getSelect()
                    sf = self._getFrom()
                    if self._conditionCompare is None:
                        self._sqlTemple = f'SELECT {ss} FROM {sf} {self._orderBy}LIMIT {self._limit}'
                    else:
                        self._sqlTemple = f'SELECT {ss} FROM {sf} WHERE {self._conditionCompare} {self._orderBy}LIMIT {self._limit}'
                if not self._renameTalbeAlias is None:
                    self._sql = self._sqlTemple.replace('--renameTalbeName--', self._currentTable)
                else:
                    self._sql = self._sqlTemple

        sql = self._sql + f' OFFSET {self._offset}'

        try:
            db.cursor.execute(sql)
            self._data = db.cursor.fetchall()
        except Exception as e:
            errMsg = str(e)
            if 'Table ' in errMsg and " doesn't exist" in errMsg:
                self._queryCurrentTable = False
                self._currentTable = None
                self._offset = 0
                self._sql = None
                return False
            raise e

    @DB
    def _search(self, db):
        if not self._queryCurrentTable:
            # 当前表已经失效了
            return False
        if self._sql is None:
            if self._sql_exec is not None:
                self._sql = f'{self._sql_exec} {self._orderBy}LIMIT {self._limit}'
            else:
                if self._sqlTemple is None:
                    ss = self._getSelect()
                    sf = self._getFrom()
                    if self._conditionCompare is None:
                        self._sqlTemple = f'SELECT {ss} FROM {sf} {self._orderBy}LIMIT {self._limit}'
                    else:
                        self._sqlTemple = f'SELECT {ss} FROM {sf} WHERE {self._conditionCompare} {self._orderBy}LIMIT {self._limit}'
                if not self._renameTalbeAlias is None:
                    self._sql = self._sqlTemple.replace('--renameTalbeName--', self._currentTable)
                else:
                    self._sql = self._sqlTemple

        sql = self._sql + f' OFFSET {self._offset}'

        try:
            db.cursor.execute(sql)
        except Exception as e:
            errMsg = str(e)
            if 'Table ' in errMsg and " doesn't exist" in errMsg:
                self._queryCurrentTable = False
                self._currentTable = None
                self._offset = 0
                self._sql = None
                return False
            raise e

        self._data = db.cursor.fetchall()
        ds = len(self._data)
        if ds < self._limit:
            # 本表结束
            self._queryCurrentTable = False
            self._currentTable = None
        else:
            self._offset = self._offset + self._limit
        return self._queryCurrentTable

    def _get(self):
        if len(self._data) == 0:
            b = self._doSearch()
            if not b:
                return None
        if len(self._data) == 0:
            return None
        return self._data.pop(0)

    def __next__(self):
        rs = self._get()
        if rs is None:
            self._sql = None
            self._sqlTemple = None
            self._currentTable = None
            self._data = []
            self._renameTalbe = []
            self._offset = 0
            raise StopIteration("遍历完了")
        return rs

    def __iter__(self):
        return self
