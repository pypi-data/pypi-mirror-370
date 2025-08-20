from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
import datetime


def connect_mongodb(mongo_uri, db_name):
    """连接到MongoDB服务器并返回客户端和数据库对象"""
    _mongo_uri = mongo_uri
    _db_name = db_name

    try:
        # 对于MongoDB 3.6，使用兼容的PyMongo版本（3.x）
        _client = MongoClient(_mongo_uri)
        _client.admin.command('ping')  # 验证连接
        print("连接成功")
        # 获取所有集合名称
        collection_names = _client[_db_name].list_collection_names()

        # 打印集合名称
        print("数据库中的所有集合：")
        cols = []
        for name in collection_names:
            cols.append(name)
        print(cols)
        return _client, _client[db_name]  # 返回客户端和数据库对象
    except ConnectionFailure as e:
        print(f"连接失败: {e}")
        return None, None


def basic_queries(db, db_name, query):
    """基本查询操作示例"""
    if db is None:
        return

    # 获取要操作的集合（类似关系数据库中的表）
    collection = db[db_name]  # 替换为你的集合名

    _query = query  # 查询条件
    docs = collection.find(_query)
    return docs


def insert_one_document(db, collection_name, document):
    """插入单个文档"""
    if db is None:
        print("数据库连接为空，无法执行插入操作")
        return None

    try:
        collection = db[collection_name]
        # 添加创建时间
        document['created_at'] = datetime.datetime.now()
        result = collection.insert_one(document)
        print(f"文档插入成功，ID: {result.inserted_id}")
        return result.inserted_id
    except PyMongoError as e:
        print(f"插入文档失败: {e}")
        return None


def insert_many_documents(db, collection_name, documents):
    """插入多个文档"""
    if db is None:
        print("数据库连接为空，无法执行插入操作")
        return None

    try:
        collection = db[collection_name]
        # 为每个文档添加创建时间
        for doc in documents:
            doc['created_at'] = datetime.datetime.now()
        result = collection.insert_many(documents)
        print(f"{len(result.inserted_ids)}个文档插入成功")
        return result.inserted_ids
    except PyMongoError as e:
        print(f"插入多个文档失败: {e}")
        return None


def find_documents(db, collection_name, query=None, projection=None, limit=0):
    """查询文档"""
    if db is None:
        print("数据库连接为空，无法执行查询操作")
        return None

    try:
        collection = db[collection_name]
        query = query or {}
        result = collection.find(query, projection).limit(limit)
        # 转换为列表返回，方便后续处理
        documents = list(result)
        print(f"查询到{len(documents)}个文档")
        return documents
    except PyMongoError as e:
        print(f"查询文档失败: {e}")
        return None


def update_one_document(db, collection_name, query, update_data):
    """更新单个文档"""
    if db is None:
        print("数据库连接为空，无法执行更新操作")
        return None

    try:
        collection = db[collection_name]
        # 添加更新时间
        if '$set' not in update_data:
            update_data['$set'] = {}
        update_data['$set']['updated_at'] = datetime.datetime.now()

        result = collection.update_one(query, update_data)
        print(f"匹配到{result.matched_count}个文档，修改了{result.modified_count}个文档")
        return result.modified_count
    except PyMongoError as e:
        print(f"更新文档失败: {e}")
        return None


def update_many_documents(db, collection_name, query, update_data):
    """更新多个文档"""
    if db is None:
        print("数据库连接为空，无法执行更新操作")
        return None

    try:
        collection = db[collection_name]
        # 添加更新时间
        if '$set' not in update_data:
            update_data['$set'] = {}
        update_data['$set']['updated_at'] = datetime.datetime.now()

        result = collection.update_many(query, update_data)
        print(f"匹配到{result.matched_count}个文档，修改了{result.modified_count}个文档")
        return result.modified_count
    except PyMongoError as e:
        print(f"更新多个文档失败: {e}")
        return None


def delete_one_document(db, collection_name, query):
    """删除单个文档"""
    if db is None:
        print("数据库连接为空，无法执行删除操作")
        return None

    try:
        collection = db[collection_name]
        result = collection.delete_one(query)
        print(f"删除了{result.deleted_count}个文档")
        return result.deleted_count
    except PyMongoError as e:
        print(f"删除文档失败: {e}")
        return None


def delete_many_documents(db, collection_name, query):
    """删除多个文档"""
    if db is None:
        print("数据库连接为空，无法执行删除操作")
        return None

    try:
        collection = db[collection_name]
        result = collection.delete_many(query)
        print(f"删除了{result.deleted_count}个文档")
        return result.deleted_count
    except PyMongoError as e:
        print(f"删除多个文档失败: {e}")
        return None
