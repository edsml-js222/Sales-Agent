from pymongo import MongoClient

def _init_mongo_connect(database_name, port=27017):
    username = 'watsons'
    password = 'watsons123'
    client = MongoClient(host="127.0.0.1", port=port, username=username, password=password)
    # 认证并且获取指定数据库的集合
    db = client[database_name]
    return db