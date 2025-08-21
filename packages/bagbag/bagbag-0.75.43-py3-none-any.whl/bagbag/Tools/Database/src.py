from __future__ import annotations

#print("load " + '/'.join(__file__.split('/')[-2:]))

from . import orator
from ..Lock_src import Lock
from ... import Lg
from ... import Base64, Hash
from ... import Time 
from ..Redis_src import redisKey
from ... import Funcs
from ... import Json

import pickle
import typing
import bagbag
import pymysql
import threading
import copy
import multiprocessing

import re

class mySQLSQLiteTable():
    def __init__(self, db: MySQLSQLiteBase, schema: orator.Schema, tbname: str):
        """
        This function initializes the class with the database, schema, and table name
        
        :param db: The database object
        :type db: MySQLSQLiteBase
        :param schema: orator.Schema
        :type schema: orator.Schema
        :param tbname: The name of the table you want to use
        :type tbname: str
        """
        self.db = db
        self.schema = schema
        self.tbname = self.filterTableName(tbname)
        self.table = {}
        self.data = {}
    
    def _id(self) -> str:
        return threading.current_thread().name + multiprocessing.current_process().name

    def filterTableName(self, tbname: str) -> str:
        nl = []
        for t in tbname:
            if t in "_qazwsxedcrfvtgbyhnujmikolopQAZWSXEDCRFVTGBYHNUJMIKOLP0123456789":
                nl.append(t)
            elif bagbag.String(t).HasChinese():
                nl.append(t)
            else:
                nl.append("_")
        
        return ''.join(nl)

    def AddColumn(self, colname: str | list[str], coltype: str, default=None, nullable:bool = True) -> mySQLSQLiteTable:
        """
        添加字段, 如果字段存在就跳过, 不会修改. 
        可以是list也可以是str, 如果是str就添加一个字段, 如果是list就添加多个字段

        :param colname: The name of the column to add
        :type colname: str, list[str]
        :param coltype: int, string, float, text
        :type coltype: str
        :param default: The default value for the column
        :param nullable: Whether the column can be null, defaults to True
        :type nullable: bool (optional)
        """
        if type(colname) == str:
            colnames = [colname]
        else:
            colnames = colname

        for colname in colnames:
            if self.schema.has_table(self.tbname):
                with self.schema.table(self.tbname) as table:
                    exists = self.schema.has_column(self.tbname, colname)

                    if not exists:
                        if coltype in ["int", "integer"]:
                            col = table.big_integer(colname)
                        elif coltype in ["string", "str", "varchar"] :
                            col = table.string(colname, 256)
                        elif coltype in ["float", "double"]:
                            col = table.double(colname)
                        elif coltype in ["text", "longtext"]:
                            col = table.long_text(colname)
                        else:
                            raise Exception("列的类型可选为: int, string, float, text")
                        
                        if default != None:
                            col.default(default)
                        
                        if nullable:
                            col.nullable()
                    
                    # if exists:
                    #     col.change()
            else:
                with self.schema.create(self.tbname) as table:
                    table.increments('id')

                    if coltype in ["int", "integer"]:
                        col = table.big_integer(colname)
                    elif coltype in ["string", "str", "varchar"] :
                        col = table.string(colname, 256)
                    elif coltype in ["float", "double"]:
                        col = table.double(colname)
                    elif coltype in ["text", "longtext"]:
                        col = table.long_text(colname)
                    else:
                        raise Exception("列的类型可选为: int, string, float, text")
                    
                    if default:
                        col.default(default)
                    
                    if nullable:
                        col.nullable()

        return self
    
    def AddIndex(self, *cols: str) -> mySQLSQLiteTable:
        """
        It adds an index to the table
        
        :param : `tbname`: The name of the table
        :type : str
        :return: The table object itself.
        """
        try:
            with self.schema.table(self.tbname) as table:
                cols = list(cols)
                # print(cols)
                table.index(cols, name='idx_' + ('_'.join(cols)))
        except Exception as e:
            # print(e)
            if "Duplicate key name" not in str(e) and "already exists" not in str(e):
                raise e

        return self
    
    # 由于不同的线程使用同一个table的时候, 条件会串, 例如多个线程同时调用where的时候.
    # 所以为每个线程生成一个orator的table对象
    def initTableObj(func): # func是被包装的函数
        def ware(self, *args, **kwargs): # self是类的实例
            # print("initTableObj", self._id(), self.table)
            if self._id() not in self.table:
                # print("初始化:", self._id())
                self.table[self._id()] = self.db.db.table(self.tbname)
            
            res = func(self, *args, **kwargs)
            return res
        
        return ware
    
    def avoidError(func): # func是被包装的函数
        def ware(self, *args, **kwargs): # self是类的实例
            if self.db.driver == "mysql":
                while True:
                    try:
                        res = func(self, *args, **kwargs)
                        break
                    except orator.exceptions.query.QueryException as e:
                        prefix_list = [
                            '(1054, ',
                            '(1406, ',
                            '(1356, ',
                            '(1241, ',
                        ]
                        if any(str(e).startswith(prefix) for prefix in prefix_list):
                            raise e 
                        # MySQL驱动默认不允许一个连接跨多个线程, 重连就行
                        Lg.Trace("重连, 因为:", e)
                        self.db.db.reconnect()
                        Time.Sleep(2)
                    except pymysql.err.OperationalError as e:  
                        if e.args[0] == 2003:
                            Time.Sleep(0.5)
                        else:
                            raise e 

            elif self.db.driver == "sqlite":
                # SQLite驱动默认不允许一个连接跨多个线程
                # 在连接的时候禁止了同线程的检测, 所以自己这里要保证同时只有一个线程在操作数据库
                self.db.lock.Acquire()
                res = func(self, *args, **kwargs)
                self.db.lock.Release()

            return res

        return ware
    
    @initTableObj
    def Fields(self, *cols: str) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].select(*cols)
        return self
    
    @initTableObj
    def Where(self, key:str, opera:str, value:str) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].where(key, opera, value)
        return self
    
    @initTableObj
    def WhereIn(self, key:str, value: list) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].where_in(key, value)
        return self 

    @initTableObj
    def WhereNotIn(self, key:str, value: list) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].where_not_in(key, value)
        return self

    @initTableObj
    def WhereNull(self, key:str) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].where_null(key)
        return self 
    
    @initTableObj
    def WhereNotNull(self, key:str) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].where_not_null(key)
        return self

    @initTableObj
    def WhereBetween(self, key:str, start:int|float|str, end:int|float|str) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].where_between(key, [start, end])
        return self 
    
    @initTableObj
    def WhereNotBetween(self, key:str, start:int|float|str, end:int|float|str) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].where_not_between(key, [start, end])
        return self 

    @initTableObj
    def OrWhere(self, key:str, opera:str, value:str) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].or_where(key, opera, value)
        return self 

    @initTableObj
    def OrWhereIn(self, key:str, value: list) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].or_where_in(key, value)
        return self

    @initTableObj
    def OrderBy(self, key:str, order:str="asc") -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].order_by(key, order)
        return self 

    @initTableObj
    def Limit(self, num:int) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].limit(num)
        return self 

    @initTableObj
    def Paginate(self, size:int, page:int) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].simple_paginate(size, page)
        return self 

    @initTableObj
    def Data(self, value:dict|list[dict]) -> mySQLSQLiteTable:
        """
        在Insert的时候可以是map或者list[map], 在Update的时候只能是map
        
        :param value: The value to be inserted into the table
        :type value: map|list[map]
        :return: The object itself.
        """
        if type(value) == dict:
            for key in value:
                if type(value[key]) == dict:
                    value[key] = Json.Dumps(value[key])

        self.data = value
        return self 

    @initTableObj
    def Distinct(self) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].distinct()
        return self 

    @initTableObj
    def Offset(self, num:int) -> mySQLSQLiteTable:
        self.table[self._id()] = self.table[self._id()].offset(num)
        return self 

    @initTableObj
    @avoidError
    def Insert(self):
        self.table[self._id()].insert(self.data)

        self.data = {}
        del(self.table[self._id()])

    @initTableObj
    @avoidError
    def Update(self):
        self.table[self._id()].update(self.data)
        
        del(self.table[self._id()])

    @initTableObj
    @avoidError
    def Delete(self):
        self.table[self._id()].delete()

        del(self.table[self._id()])

    @initTableObj
    @avoidError
    def InsertGetID(self) -> int:
        id = self.table[self._id()].insert_get_id(self.data)

        self.data = {}
        del(self.table[self._id()])

        return id

    def Exists(self) -> bool: 
        exists = False
        if self.First():
            exists = True

        return exists

    def NotExists(self) -> bool: 
        notexists = True
        if self.First():
            notexists = False

        return notexists

    @initTableObj
    @avoidError
    def Count(self) -> int:
        count = self.table[self._id()].count()

        del(self.table[self._id()])
        return count

    @initTableObj
    @avoidError
    def Find(self, id:int) -> dict | None:
        res = self.db.db.table(self.tbname).where('id', "=", id).first()
        return res 
        
    @initTableObj
    @avoidError
    def First(self) -> dict | None: 
        """
        :return: A map of the first row in the table. Return None if the table is empty. 
        """
        lastqueryiserror = False 
        while True:
            try:
                res = self.table[self._id()].first()
                if lastqueryiserror and res == None:
                    Time.Sleep(0.5)
                else:
                    break 
            except pymysql.err.OperationalError as e:
                if e.args[0] == 2003:
                    lastqueryiserror = True 
                    Time.Sleep(0.5)
                else:
                    raise e 

        del(self.table[self._id()])
        return res

    @initTableObj
    @avoidError
    def Get(self) -> list[dict]:
        """
        It gets the data from the table and then resets the table
        len(result) == 0 if the result set is empty.

        :return: A list of dictionaries.
        """
        lastqueryiserror = False 
        while True:
            try:
                res = [dict(i) for i in self.table[self._id()].get()]
                if lastqueryiserror and len(res) == 0:
                    Time.Sleep(0.5)
                else:
                    break 
            except pymysql.err.OperationalError as e:  
                if e.args[0] == 2003:
                    lastqueryiserror = True 
                    Time.Sleep(1)
                else:
                    raise e 

        del(self.table[self._id()])
        return res

    def Columns(self) -> list[dict]:
        """
        It returns a list of dictionaries, each dictionary containing the name and type of a column in a
        table
        :return: A list of dictionaries.
        """
        res = []
        if self.db.driver == "mysql":
            for i in self.db.Execute("SHOW COLUMNS FROM `"+self.tbname+"`"):
                res.append({'name': i["Field"], 'type': i["Type"]})
        elif self.db.driver == "sqlite":
            for i in self.db.db.select("PRAGMA table_info(`"+self.tbname+"`);"):
                res.append({'name': i["name"], 'type': i["type"]})
        return res
    
    @initTableObj
    @avoidError
    def _get_do_not_clean(self) -> list[dict]:
        lastqueryiserror = False 
        while True:
            try:
                res = [dict(i) for i in self.table[self._id()].get()]
                if lastqueryiserror and len(res) == 0:
                    Time.Sleep(0.5)
                else:
                    break 
            except pymysql.err.OperationalError as e:  
                if e.args[0] == 2003:
                    lastqueryiserror = True 
                    Time.Sleep(1)
                else:
                    raise e 

        return res
    
    @initTableObj
    def Iterate(self, chunksize:int=200, seekobj:mySQLSQLiteKeyValueTableKey|redisKey=None) -> typing.Iterable[dict]:
        """
        迭代小批次的取出大批量的数据, 不是使用offset, 会对id进行where判断来提取, 所以速度会很快.
        因为会对id进行比对来提取数据, 所以其它地方设置的select中的对id的where条件会被清除. 
        seekobj需要实现两个方法, Set和Get, 会用来保存上次提取的进度, 如果为None就不会持久化的保存进度.
        如果有传入seekobj, 每一个批次之后都会调用Set方法, 所以如果这个批次没有处理完程序就退出了, 下次将会继续这个批次.
        由于在当前函数内部会保存链式调用的状态, 所以可以在for循环的迭代和循环体当中使用同一个table对象, 不会扰乱当前迭代的状态. 

        :param chunksize: 每次从数据库select的数据的量
        :type chunksize: int (optional)
        :param seekobj: The object that stores the last idx
        :type seekobj: mySQLSQLiteKeyValueTableKey|redisKey
        :return: A generator object.
        """
        if seekobj == None:
            idx = 0
        else:
            idx = seekobj.Get(0)
        
        if self._id() not in self.table:
            # print("初始化:", self._id())
            self.table[self._id()] = self.db.db.table(self.tbname)

        # 如果有where语句作用id字段里面, 在sql的builder里面, 就删掉它, 和它binding的值
        if len(self.table[self._id()].wheres) != 0:
            widx = 0
            while True:
                if self.table[self._id()].wheres[widx]['column'] == "id":
                    self.table[self._id()].wheres.pop(widx)
                    self.table[self._id()]._bindings['where'].pop(widx)
                else:
                    widx += 1

                # print("widx:", widx, "len:", len(self.table[self._id()].wheres))
                if widx >= len(self.table[self._id()].wheres):
                    break  

        # 保存当前状态
        tobj = copy.deepcopy(self.table[self._id()])

        while True:
            # 恢复之前的链式调用的状态
            self.table[self._id()] = copy.deepcopy(tobj)

            rs = self.Where("id", ">", idx).Limit(chunksize).OrderBy("id")._get_do_not_clean()
            if len(rs) == 0:
                return 

            for r in rs:
                yield dict(r)
                idx = r['id']

            if seekobj != None:
                # print("set to id:", id)
                seekobj.Set(idx)
    
    def Truncate(self):
        self.db.db.table(self.tbname).truncate()
    
    def LatestID(self) -> int | None:
        """
        It returns the last id of the data in the table
        :return: The last id of the data in in the table.
        """
        res = self.OrderBy("id", "desc").First()
        if res == None:
            return 0 
        else:
            return res['id']

class mySQLSQLiteKeyValueTableKey():
    def __init__(self, kv:mySQLSQLiteKeyValueTable|mySQLSQLiteKeyValueTableNamespaced, key:str) -> None:
        self.key = key 
        self.kv = kv
    
    def Set(self, value:typing.Any):
        self.kv.Set(self.key, value)
    
    def Get(self, default:typing.Any=None):
        return self.kv.Get(self.key, default)
    
    def Add(self, num:int|float=1) -> mySQLSQLiteKeyValueTableKey:
        n = self.kv.Get(self.key, 0)
        n += num 
        self.kv.Set(self.key, n)
        return self
    
    def __add__(self, num:int|float) -> mySQLSQLiteKeyValueTableKey:
        return self.Add(num)
    
    def __iadd__(self, num:int|float) -> mySQLSQLiteKeyValueTableKey:
        return self.Add(num)

class mySQLSQLiteKeyValueTable():
    def __init__(self, db:MySQLSQLiteBase, tbname:str) -> None:
        self.db = db 
        if tbname not in self.db.Tables():
            (
                self.db.Table(tbname). 
                    AddColumn("key", "text"). 
                    AddColumn("value", "text"). 
                    AddColumn("md5", "str").
                    AddColumn("updated_at", "int").
                    AddIndex("md5")
            )
        self.tbname = tbname
        self.namespace = []
        self.md5s = {}
    
    def Key(self, key:str) -> mySQLSQLiteKeyValueTableKey:
        return mySQLSQLiteKeyValueTableKey(self, key)
    
    def Namespace(self, namespace:str) -> mySQLSQLiteKeyValueTableNamespaced:
        if len(':'.join(self.namespace)) > 200:
            raise Exception("Namespace too long: " + str(len(':'.join(self.namespace))))
        return mySQLSQLiteKeyValueTableNamespaced(self.db, self.tbname, namespace)
    
    def __key(self, key:str) -> str:
        if len(self.namespace) == 0:
            return key 
        else:
            return ':'.join(self.namespace) + ":" + key
    
    def __md5(self, key:str) -> str:
        key = self.__key(key)
        if key not in self.md5s:
            self.md5s[key] = Hash.Md5sum(key)
        return self.md5s[key]
    
    def Exists(self, key:str) -> bool:
        tb = self.db.Table(self.tbname)
        return tb.Where("md5", "=", self.__md5(key)).Exists()
    
    def Get(self, key:str, default:typing.Any=None) -> typing.Any:
        tb = self.db.Table(self.tbname)
        res = tb.Where("md5", "=", self.__md5(key)).First()

        if res != None:
            value = res["value"]
            if value[:2] == "i ":
                value = int(value[2:])
            elif value[:2] == "s ":
                value = value[2:]
            elif value[:2] == "f ":
                value = float(value[2:])
            elif value[:2] == "p ":
                value = pickle.loads(Base64.Decode(value[2:])) 
            else:
                value = pickle.loads(Base64.Decode(value)) # 为了兼容之前的代码
        else:
            value = default 

        return value
    
    def Set(self, key:str, value:typing.Any):
        tb = self.db.Table(self.tbname)

        if type(value) == int:
            value = "i " + str(value)
        elif type(value) == str:
            value = "s " + str(value)
        elif type(value) == float:
            value = "f " + str(value)
        else:
            value = "p " + Base64.Encode(pickle.dumps(value, protocol=2))

        if tb.Where("md5", "=", self.__md5(key)).Exists():
            tb.Where("md5", "=", self.__md5(key)).Data({
                "value": value,
                "updated_at": Time.Now(),
            }).Update()
        else:
            tb.Data({
                "key": self.__key(key), 
                "md5": self.__md5(key), 
                "value": value,
                "updated_at": Time.Now(),
            }).Insert()
    
    def Del(self, key:str):
        tb = self.db.Table(self.tbname)
        tb.Where("key", "=", self.__key(key)).Delete()

class mySQLSQLiteKeyValueTableNamespaced(mySQLSQLiteKeyValueTable):
    def __init__(self, db: MySQLSQLiteBase, tbname: str, namespace: str|list) -> None:
        super().__init__(db, tbname)
        if type(namespace) == str:
            self.namespace = [namespace]
        elif type(namespace) == list:
            self.namespace = namespace
    
    def Namespace(self, namespace: str) -> mySQLSQLiteKeyValueTableNamespaced:
        return mySQLSQLiteKeyValueTableNamespaced(self.db, self.tbname, self.namespace + [namespace])

class mySQLSQLiteConfirmQueue():
    def __init__(self, db:MySQL|SQLite, name:str, timeout:int, size:int) -> None:
        self.db = db 
        self.name = name 
        self.lock = Lock()
        self.timeout = timeout
        self.size = size
    
    def Size(self) -> int:
        """
        返回未曾开始过的新任务个数
        :return: The number of rows in the table.
        """
        return self.db.Table(self.name).Where("stime", "=", 0).Count()
    
    def SizeStarted(self) -> int:
        """
        返回正在执行的任务个数
        :return: The number of rows in the table where the stime column is not equal to 0.
        """
        return self.db.Table(self.name).Where("stime", "!=", 0).Count()
    
    def SizeTotal(self) -> int:
        """
        返回所有任务总数
        :return: The number of rows in the table.
        """
        return self.db.Table(self.name).Count()
    
    def Get(self, block:bool=True) -> typing.Tuple[int, typing.Any]:
        self.lock.Acquire()
        while True:
            r = self.db.Table(self.name).Where("stime", "<", int(Time.Now()) - self.timeout).OrderBy("id").First()

            if r == None:
                r = self.db.Table(self.name).Where("stime", "=", 0).OrderBy("id").First()

                if r == None:
                    if not block:
                        self.lock.Release()
                        return None, None 
                    else:
                        Time.Sleep(0.1)
                else:
                    break 
            else:
                break
        
        self.db.Table(self.name).Where("id", "=", r["id"]).Data({
            "stime": int(Time.Now()),
        }).Update()

        self.lock.Release()
        return r["id"], pickle.loads(Base64.Decode(r["data"]))
    
    def Put(self, item:typing.Any, block:bool=True, force:bool=False):
        if force == False:
            if block:
                while self.size > 0 and self.Size() >= self.size:
                    Time.Sleep(0.1)
            else:
                if self.size > 0 and self.Size() >= self.size:
                    return False

        self.db.Table(self.name).Data({
            "data": Base64.Encode(pickle.dumps(item, protocol=2)),
            "stime": 0,
        }).Insert()

        return True

    def Done(self, id:int):
        r = self.db.Table(self.name).Where("id", "=", id).First()
        if r == None:
            raise Exception("任务没找到")
        else:
            if r["stime"] == 0:
                raise Exception("任务未开始")
            else:
                self.db.Table(self.name).Where("id", "=", id).Delete()
    
    def __iter__(self):
        while True:
            yield self.Get()

class mySQLSQLiteQueue():
    def __init__(self, db:MySQL|SQLite, name:str, size:int) -> None:
        self.db = db 
        self.name = name 
        self.lock = Lock()
        self.size = size
    
    def Size(self) -> int:
        return self.db.Table(self.name).Count()
    
    def Get(self, wait=True) -> typing.Any:
        self.lock.Acquire()
        r = self.db.Table(self.name).OrderBy("id").First()
        if r == None:
            if not wait:
                self.lock.Release()
                return None 
            else:
                while r == None:
                    Time.Sleep(0.1)
                    r = self.db.Table(self.name).OrderBy("id").First()
        
        self.db.Table(self.name).Where("id", "=", r["id"]).Delete()

        self.lock.Release()
        return pickle.loads(Base64.Decode(r["data"]))
    
    def Put(self, item:typing.Any):
        while self.size > 0 and self.Size() >= self.size:
            Time.Sleep(0.1)

        self.db.Table(self.name).Data({
            "data": Base64.Encode(pickle.dumps(item, protocol=2)),
        }).Insert()
    
    def __iter__(self):
        while True:
            yield self.Get()

# > The class is a base class for MySQL and SQLite
class MySQLSQLiteBase():
    def __init__(self) -> None:
        self.db:orator.DatabaseManager = None

    def Queue(self, tbname:str, size:int=0) -> mySQLSQLiteQueue:
        if tbname not in self.Tables():
            self.Table(tbname).AddColumn("data", "text")
        
        return mySQLSQLiteQueue(self, tbname, size)

    def QueueConfirm(self, tbname:str, size:int=0, timeout:int=300) -> mySQLSQLiteConfirmQueue:
        """
        这是一个需要调用Done方法来确认某个任务完成的队列
        如果不确认某个任务完成, 它就会留在队列当中等待timeout之后重新能被Get到
        优先Get到timeout的任务
        """

        if tbname not in self.Tables():
            (
                self.Table(tbname).
                    AddColumn("data", "text"). 
                    AddColumn("stime", "int"). 
                    AddIndex("stime")
            )
        
        return mySQLSQLiteConfirmQueue(self, tbname, timeout, size)

    def clean_table_name(self, table_name):
        """
        将MySQL表名中的符号替换为下划线，保留中文字符
        
        Args:
            table_name (str): 原始表名字符串
            
        Returns:
            str: 处理后的表名
        """
        if not isinstance(table_name, str):
            raise TypeError("表名必须是字符串类型")
        
        if not hasattr(self, 'TABLE_NAME_PATTERN'):
            self.TABLE_NAME_PATTERN = re.compile(r'[^\u4e00-\u9fff\w]')
            self.MULTIPLE_UNDERSCORES_PATTERN = re.compile(r'_+')
        
        # 使用预编译的正则表达式
        cleaned_name = self.TABLE_NAME_PATTERN.sub('_', table_name)
        
        # 处理连续的下划线
        cleaned_name = self.MULTIPLE_UNDERSCORES_PATTERN.sub('_', cleaned_name)
        
        # 去除开头和结尾的下划线
        # cleaned_name = cleaned_name.strip('_')
        
        return cleaned_name

    def Table(self, tbname: str) -> mySQLSQLiteTable:
        tbname = self.clean_table_name(tbname)
        if not tbname in self.Tables():
            with self.schema.create(tbname) as table:
                table.increments('id')

        return mySQLSQLiteTable(self, self.schema, tbname)

    def Execute(self, sql: str) -> (bool | int | list):
        """
        :param sql: The SQL statement to execute
        :type sql: str
        """
        action = sql.split()[0].lower() 

        sql = sql.replace("%", "%%")

        try:
            if action == "insert":
                res = self.db.insert(sql)
            elif action in ["select", "show"]:
                res = self.db.select(sql)
            elif action == "update":
                res = self.db.update(sql)
            elif action == "delete":
                res = self.db.delete(sql)
            else:
                res = self.db.statement(sql)
        except orator.exceptions.query.QueryException as e:
            if self.driver == "mysql":
                if action == "insert":
                    res = self.db.insert(sql)
                elif action in ["select", "show"]:
                    res = self.db.select(sql)
                elif action == "update":
                    res = self.db.update(sql)
                elif action == "delete":
                    res = self.db.delete(sql)
                else:
                    res = self.db.statement(sql)
            else:
                raise e
                
        return res

    def Tables(self) -> list:
        """
        It returns a list of all the tables in the database
        :return: A list of tables in the database.
        """
        res = []
        if self.driver == "mysql":
            tbs = self.Execute("show tables;")
        elif self.driver == "sqlite":
            tbs = self.Execute("SELECT `name` FROM sqlite_master WHERE type='table';")
        for i in tbs:
            for k in i:
                res.append(i[k])
        return res
    
    def Close(self):
        self.db.disconnect()
    
    def KeyValue(self, tbname:str="kv") -> mySQLSQLiteKeyValueTable:
        return mySQLSQLiteKeyValueTable(self, tbname)
    
    def BeginTransaction(self):
        self.db.begin_transaction()
    
    def Rollback(self):
        self.db.rollback()
    
    def Commit(self):
        self.db.commit()

# > This class is a wrapper for the orator library, which is a wrapper for the mysqlclient library,
# which is a wrapper for the MySQL C API
class MySQL(MySQLSQLiteBase):
    def __init__(self, host:str="mysql", port:int=3306, user:str="root", password:str="r", database:str="others", prefix:str="", charset:str="utf8mb4"):
        """
        This function creates a database connection using the orator library
        
        :param host: The hostname of the database you are connecting to. (localhost)
        :type host: str
        :param port: The port number to connect to the database
        :type port: int
        :param user: The username to connect to the database with
        :type user: str
        :param password: The password for the user you're connecting with
        :type password: str
        :param database: The name of the database you want to connect to
        :type database: str
        :param prefix: The prefix for the table names
        :type prefix: str
        """
        config = {
            'mysql': {
                'driver': 'mysql',
                'host': host,
                'database': database,
                'user': user,
                'password': password,
                'prefix': prefix,
                'port': port,
                'charset': charset,
            }
        }
        self.db = orator.DatabaseManager(config)
        self.schema = orator.Schema(self.db)
        self.driver = "mysql"
    
# > This class is a wrapper for the orator library, which is a wrapper for the sqlite3 library
class SQLite(MySQLSQLiteBase):
    def __init__(self, path:str=":memory:", prefix:str = ""):
        """
        :param path: The path to the database file
        :type path: str
        :param prefix: The prefix to use for the table names
        :type prefix: str
        """
        config = {
            'sqlite': {
                'driver': 'sqlite',
                'database': path,
                'prefix': '',
                'check_same_thread': False, # 会被传入到SQLite的驱动作为参数
            }
        }
        self.db = orator.DatabaseManager(config)
        self.schema = orator.Schema(self.db)
        self.driver = "sqlite"
        self.lock = Lock()


if __name__ == "__main__":
    # db = SQLite("data.db")
    # tbl = db.Table("test_tbl").AddColumn("string", "string").AddColumn("int", "string").AddIndex("int")
    # tbl.Data({"string":"string2", "int": 2}).Insert()
    # c = tbl.Where("string", "=", "string2").Count()
    # print(c)

    # print("exists:", tbl.Where("string", "=", "string555").Exists())

    # db.Close()

    # import os 
    # os.unlink("data.db")

    # print(db.Table("test_tbl").First())

    # db = MySQL("192.168.168.5", 3306, "root", "r", "test")

    # for row in db.Table("__queue__name__name").Get():
    #     print(row)

    # print(db.Table("__queue__name__name").Columns())

    # 执行SQL语句
    # In [4]: db.Execute("select distinct(`Column1`) from `table1`")
    # Out[4]: ({'Column1': '1'}, {'Column1': '2'}, {'Column1': '3'}, {'Column1': '4'})
    # 
    # In [3]: db.Execute("select count(`id`) as `count`, `data` from `table` group by `data`")
    # Out[3]: 
    # ({'count': 2, 'data': '1'},
    # {'count': 1, 'data': '2'},
    # {'count': 1, 'data': '3'},
    # {'count': 1, 'data': '4'})

    # db = MySQL("192.168.1.230")

    # 中文字段
    # (
    #     db.Table("俄罗斯号码段"). 
    #         AddColumn("开始", "int"). 
    #         AddColumn("结束", "int"). 
    #         AddColumn("运营商", "string").
    #         AddColumn("地区", "string")
    # )

    # tb = db.Table("test").AddColumn("col", "string")
    # tb.Data({
    #     "col": "😆😆😆😆😆",
    # }).Insert()

    # Lg.Trace(db.Table("chainabuse").Columns())

    ##############

    # db = MySQL("192.168.1.230")

    # qn = db.Queue("queue_test")
    # qn.Put(b'\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isom')
    # print(qn.Size())
    # print(repr(qn.Get()))

    # print("开启一个需要确认任务完成的队列, 3秒超时")
    # qnc = db.QueueConfirm("queue_confirm_test", timeout=3)
    # qnc.Put(b'\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isom')

    # print("获取任务内容")
    # idx, data = qnc.Get()
    # print(repr(data))

    # print("等待5秒")
    # Time.Sleep(5)

    # print("再次获取任务")
    # idx, data = qnc.Get()
    # print(repr(data))

    # print("确认任务完成")
    # Time.Sleep(1)
    # qnc.Done(idx)

    # print("等待5秒")
    # Time.Sleep(5)

    # print("再次获取任务, 不等待")
    # idx, data = qnc.Get(False)
    # print(repr(data))

    #################

    # db = MySQL("192.168.1.224")

    # kv = db.KeyValue()

    # kv.Set("key", "no_namespace")

    # kvns1 = kv.Namespace("ns1")
    # kvns1.Set("key", "ns1_value")
    # kvns12 = kvns1.Namespace("ns2")
    # kvns12.Set("key", "ns12_value")

    # kvns2 = kv.Namespace("ns2")
    # kvns2.Set("key", "ns2_value")
    # kvns22 = kvns2.Namespace("ns2")
    # kvns22.Set("key", "ns22_value")

    #########3

    db = MySQL("192.168.1.224")
    
    # kv = db.KeyValue()

    # k = kv.Key("key")

    # k.Set(2.5)

    # k += 1

    # print(k.Get())

    # k = k + 19

    # print(k.Get())

    seek = db.KeyValue().Namespace("test").Key("iterateIdx")

    tb = db.Table("websites")

    for i in tb.Where("id", ">", "123").Where("alive", "=", "no").Where("note", "like", "Traceback%").Iterate(2, seek):
        Lg.Trace(i)