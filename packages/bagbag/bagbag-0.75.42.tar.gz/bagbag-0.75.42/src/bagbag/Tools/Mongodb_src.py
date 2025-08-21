from __future__ import annotations

import threading
import multiprocessing
import pymongo
from urllib.parse import quote_plus
import typing 
from bson import ObjectId
from pymongo.database import Database as pymongodatabase
from pymongo.collection import Collection as pymongocollection

class MongoDBCollection():
    def __init__(self, mongodb:MongoDB, database:str, collection:str) -> None:
        self.collection = collection
        self.mongodb = mongodb 
        self.database = database

        self.query = {}
        self.data = {} 
        self.collections = {}

    def getcollection(self) -> pymongocollection:
        mid = self.getid()
        if mid not in self.collections:
            self.collections[mid] = self.mongodb.getconn().get_database(self.database).get_collection(self.collection)

        return self.collections[mid]

    def getid(self) -> str:
        """
        The function returns a string concatenating the name of the current thread and the name of the
        current process.
        :return: The `getid` method is returning a string that concatenates the name of the current thread
        from the `threading` module and the name of the current process from the `multiprocessing`
        module.
        """
        return threading.current_thread().name + multiprocessing.current_process().name

    def getquery(self, clean:bool=False):
        """
        The function `getquery` initializes a dictionary in the `query` attribute of an object based on a
        given ID if it does not already exist or if the `clean` parameter is set to `True`.
        
        :param clean: The `clean` parameter in the `getquery` method is a boolean parameter with a default
        value of `False`. It is used to determine whether the existing query data should be cleaned or
        not. If `clean` is set to `True`, it will clear the existing query data and initialize it with,
        defaults to False
        :type clean: bool (optional)
        :return: The function `getquery` is returning the query dictionary associated with the `mid` key.
        If the `mid` key does not exist in the `query` dictionary or if the `clean` parameter is set to
        `True`, a new dictionary with initial values for 'opera', 'order', and 'limit' keys is created
        and stored in the `query` dictionary with the `mid`
        """
        mid = self.getid()
        if mid not in self.query or clean == True:
            self.query[mid] = {
                'opera': {},
                'order': [],
                "limit": None,
            }
        
        return self.query[mid]

    def Where(self, key:str, opera:str, value:str) -> MongoDBCollection:
        """
        The function `Where` is used to construct MongoDB queries based on the provided key, comparison
        operator, and value.
        
        :param key: The `key` parameter in the `Where` method represents the field or attribute in the
        MongoDB collection that you want to query against. It is the field you are specifying a
        condition for, such as "_id", "name", "age", etc
        :type key: str
        :param opera: The `opera` parameter in the `Where` method represents the comparison operator to
        be used in the MongoDB query. It can be one of the following values:
        :type opera: str
        :param value: The `value` parameter in the `Where` method represents the value that you want to
        compare the specified key against using the specified operator. Depending on the operator chosen
        (such as "=", ">", ">=", "<", "<="), the method will construct a query to filter MongoDB
        documents based on this comparison
        :type value: str
        :return: The `Where` method is returning the current instance of the class it belongs to
        (presumably a MongoDB query builder class) after setting the query conditions based on the
        provided key, operator, and value.
        """
        if key == '_id' and type(value) == str:
            value = ObjectId(value)

        if opera == "=":
            self.getquery()['opera'][key] = value
        elif opera == '>':
            self.getquery()['opera'][key] = {"$gt": value}
        elif opera == '>=' or opera == '=>':
            self.getquery()['opera'][key] = {"$gte": value}
        elif opera == '<':
            self.getquery()['opera'][key] = {"$lt": value}
        elif opera == '<=' or opera == '=<':
            self.getquery()['opera'][key] = {"$lte": value}

        return self
    
    def OrderBy(self, key:str, order:str="asc") -> MongoDBCollection:
        """
        This Python function sets the ordering criteria for a MongoDB query based on the specified key
        and order direction.
        
        :param key: The `key` parameter in the `OrderBy` method is used to specify the field by which
        the data should be ordered in the MongoDB query. It represents the field name based on which the
        sorting will be applied
        :type key: str
        :param order: The `order` parameter in the `OrderBy` method specifies the order in which the
        results should be sorted. It can have two possible values:, defaults to asc
        :type order: str (optional)
        :return: The `OrderBy` method is returning the current instance of the class (self) after
        setting the order criteria based on the provided key and order direction.
        """
        if order == "asc":
            self.getquery()['order'] = [key, pymongo.ASCENDING]
        elif order == "desc":
            self.getquery()['order'] = [key, pymongo.DESCENDING]
        else:
            raise Exception("未知的排序规则:", order)
    
        return self
    
    def First(self) -> dict | None:
        """
        This Python function retrieves the first document from a MongoDB collection based on a query and
        sorting criteria.
        :return: The `First` method returns a dictionary containing the first document that matches the
        query criteria specified in the method. If no document is found, it returns `None`.
        """
        
        query = self.getquery()
        self.getquery(clean=True)

        cursor = self.getcollection().find(query['opera'])

        if query['order'] != []:
            cursor.sort(*query['order'])

        try:
            res = next(cursor)
            res['_id'] = str(res['_id'])
            return res
        except StopIteration:
            return None 
    
    def Get(self) -> list[dict]:
        """
        The Get function retrieves data from a MongoDB collection based on specified query parameters
        and returns the results as a list of dictionaries.
        :return: A list of dictionaries containing the query results from the database collection after
        applying any specified sorting and limiting conditions. The '_id' field in each dictionary is
        converted to a string before being returned.
        """
        query = self.getquery()
        self.getquery(clean=True)

        cursor = self.getcollection().find(query['opera'])

        if query['order'] != []:
            cursor.sort(*query['order'])

        if query['limit'] != None:
            cursor.limit(query['limit'])

        reses = []
        for res in cursor:
            res['_id'] = str(res['_id'])
            reses.append(res)

        return reses 
    
    def Iterate(self) -> typing.Iterator[dict]:
        """
        This Python function iterates over documents in a MongoDB collection based on specified query
        parameters and yields each document after converting its '_id' field to a string.
        """
        query = self.getquery()
        self.getquery(clean=True)

        cursor = self.getcollection().find(query['opera'])

        if query['order'] != []:
            cursor.sort(*query['order'])

        if query['limit'] != None:
            cursor.limit(query['limit'])

        for res in cursor:
            res['_id'] = str(res['_id'])
            yield res
    
    def Limit(self, number:int) -> MongoDBCollection:
        """
        The `Limit` function sets a limit on the number of results returned in a MongoDB query.
        
        :param number: The `number` parameter in the `Limit` method represents the maximum number of
        documents that should be returned by a MongoDB query. This parameter is used to limit the number
        of results returned by the query to a specific number
        :type number: int
        :return: The method `Limit` is returning the current instance of the class, which allows for
        method chaining.
        """
        self.getquery()['limit'] = number 

        return self
    
    def Data(self, data:dict|list) -> MongoDBCollection:
        """
        This Python function takes a dictionary or list of data, converts string '_id' values to
        ObjectId, and stores the data in a MongoDB instance.
        
        :param data: The `data` parameter in the `Data` method can be either a dictionary or a list. The
        method checks the type of `data` and if it is a dictionary, it converts the `getid` field to an
        `ObjectId` if it is a string. If `data` is a
        :type data: dict|list
        :return: The method `Data` is returning the instance of the class `MongoDB` after processing the
        input data and storing it in the `self.data` dictionary with the generated `mid` as the key.
        """
        mid = self.getid()

        if type(data) == dict:
            if '_id' in data and type(data['_id']) == str:
                data['_id'] = ObjectId(data['_id'])
        elif type(data) == list:
            for idx in range(len(data)):
                if '_id' in data[idx] and type(data[idx]['_id']) == str:
                    data[idx]['_id'] = ObjectId(data[idx]['_id'])
        else:
            raise Exception("不支持的数据类型")

        self.data[mid] = data
        
        return self 
    
    def Insert(self) -> str | list:
        """
        This function inserts data into a MongoDB collection either as a single document or multiple
        documents based on the data type provided.
        :return: The `Insert` method returns either a string representing the ObjectID of a single
        inserted document if the data at the specified index is a dictionary, or a list of strings
        representing the ObjectIDs of multiple inserted documents if the data at the specified index is
        a list.
        """
        mid = self.getid()
        
        if type(self.data[mid]) == dict:
            oid = str(self.getcollection().insert_one(self.data[mid]))
            del(self.data[mid])
            return oid 
        elif type(self.data[mid]) == list:
            oids = self.getcollection().insert_many(self.data[mid])
            del(self.data[mid])
            for idx in range(len(oids)):
                oids[idx] = str(oids[idx])
            return oids
        else:
            raise Exception("不支持的数据类型")
    
    def Update(self):
        """
        The function `Update` updates multiple documents in a MongoDB collection based on a query
        """
        opera = self.getquery()['opera']
        self.getquery(clean=True)

        mid = self.getid()

        self.getcollection().update_many(opera, {'$set': self.data[mid]})

        del(self.data[mid])
    
    def Truncate(self):
        """
        The `Truncate` function calls the `Drop` method.
        """
        self.Drop()
    
    def Drop(self):
        """
        The `Drop` function drops the collection specified in the database connected to the given
        connection.
        """
        self.getcollection().drop()

    def Index(self, *cols:str, order:str="asc"):
        """
        The function creates an index on specified columns in a MongoDB collection with the specified
        order.
        
        :param : The `Index` method takes the following parameters:
        :type : str
        :param order: The `order` parameter in the `Index` method specifies the order in which the index
        should be created. It can have two possible values: "asc" for ascending order and "desc" for
        descending order. If no value is provided, the default order is ascending, defaults to asc
        :type order: str (optional)
        """
        order = 1 if order == 'asc' else -1
        idxs = []
        for col in cols:
            idxs.append((col, order))
        
        self.getcollection().create_index(idxs)
    
    def DropIndex(self, *cols:str, order:str="asc"):
        """
        This Python function drops indexes on specified columns in a specified order.
        
        :param : The `DropIndex` method takes the following parameters:
        :type : str
        :param order: The `order` parameter in the `DropIndex` method specifies the order in which the
        index should be dropped. It can have two possible values: "asc" for ascending order and "desc"
        for descending order. The default value is "asc" if no value is provided, defaults to asc
        :type order: str (optional)
        """
        order = 1 if order == 'asc' else -1
        idxs = []
        for col in cols:
            idxs.append((col, order))
        
        self.getcollection().drop_index(idxs)

    def Delete(self) -> int:
        """
        This Python function deletes multiple documents from a MongoDB collection based on a specified
        query.
        :return: The code snippet is a method named `Delete` that deletes multiple documents from a
        MongoDB collection based on a query. The method first retrieves the collection and query from
        the database, then deletes the documents that match the query using the `delete_many` method.
        Finally, it returns the number of documents that were deleted (`deleted_count`).
        """
        opera = self.getquery()['opera']
        self.getquery(clean=True)

        return self.getcollection().delete_many(opera).deleted_count
    
    def EstimatedDocumentCount(self) -> int:
        return self.getcollection().estimated_document_count()
    
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

class MongoDBDatabase():
    def __init__(self, mongodb:MongoDB, database:str) -> None:
        self.mongodb = mongodb
        self.database = database

        self.mongodb.getconn().get_database(database)

    def Collection(self, name:str) -> MongoDBCollection:
        return MongoDBCollection(self.mongodb, self.database, name)
    
    def Drop(self):
        self.mongodb.getconn().drop_database(self.database)

class MongoDB():
    def __init__(self, host:str, port:int=27017, username:str=None, password:str=None) -> None:
        self.host = host 
        self.port = port 
        self.username = username 
        self.password = password 

        self.conns = {}

        self.getconn()

    def getconn(self) -> pymongo.MongoClient:
        """
        This function establishes a connection to a MongoDB database using the provided credentials and
        configuration.
        :return: The `getconn` method returns a `pymongo.MongoClient` object from the `self.conns`
        dictionary based on the `getid` of the current object. If the MongoClient object for the given
        `getid` does not exist in the `self.conns` dictionary, a new MongoClient object is created based
        on the connection parameters (host, port, username, password) and stored in the
        """
        mid = self.getid()
        if mid not in self.conns:
            if self.username != None:
                client = pymongo.MongoClient(
                    "mongodb://%s:%s@%s:%d" % (quote_plus(self.username), quote_plus(self.password), self.host, self.port)
                )

            else:
                client = pymongo.MongoClient(
                    "mongodb://%s:%d" % (self.host, self.port)
                )

            self.conns[mid] = client 

        return self.conns[mid]
                
    def getid(self) -> str:
        """
        The function returns a string concatenating the name of the current thread and the name of the
        current process.
        :return: The `getid` method is returning a string that concatenates the name of the current thread
        from the `threading` module and the name of the current process from the `multiprocessing`
        module.
        """
        return threading.current_thread().name + multiprocessing.current_process().name
    
    def Database(self, name:str) -> MongoDBDatabase:
        """
        The function `Database` takes a name parameter and returns a MongoDB object with the specified
        database name.
        
        :param name: The `name` parameter in the `Database` method is a string that represents the name
        of the database you want to create or work with
        :type name: str
        :return: The `Database` method is returning the instance of the class itself (`self`) after
        setting the `database` attribute to the provided `name` parameter.
        """
        return MongoDBDatabase(self, name)

if __name__ == "__main__":
    from bagbag import Lg

    db = MongoDB("127.0.0.1", 27017, 'root', 'root')

    co = db.Database("smdb").Collection('mytestdata')

    res = co.Where("username", "=", "user_2").OrderBy("age", "desc").First()

    Lg.Trace(res)

    res = [i for i in co.Limit(3).Get()]

    Lg.Trace(res)

    co1 = db.Database("smdb").Collection('mytestdata1')

    co1.Data({
        "name": "alice"
    }).Insert()

    Lg.Trace(co1.First())

    co1.Data({"name": "bobby"}).Update()

    co1.Data({
        "name": "alice"
    }).Insert()

    Lg.Trace(co1.Get())

    co1.Where("name", "=", "alice").Data({"name": "lily"}).Update()

    Lg.Trace(co1.Get())

    co1.Where("name", "=", "lily").Delete()

    Lg.Trace(co1.Get())

    co1.Data({
        "name": "kate",
        "age": 20
    }).Insert()

    co1.Index("name")

    co1.Index("name", "age", order="desc")

    co1.DropIndex("name", "age", order="desc")