from pymilvus import (
    connections,
    Collection,
    utility,
    FieldSchema,
    db
)
import time


class Milvus:
    def __init__(self,
                 alias_name = 'default',
                 threshold = 0.8,
                 host = "localhost",
                 port = "19530",
                 # user: str = "root",
                 # password: str = "Milvus2_2Milvus",
                 index_params=None,
                 search_params=None,) -> None:
        self.alias = alias_name
        self.host = host
        self.port = port
        # user=user,
        # password=password
        
        connections.connect(alias=self.alias, host=self.host, port=self.port) # connect to the milvus server
        if self.alias != 'default':
            db_name = self.alias + "DB"
            if db_name not in db.list_database(using=self.alias):
                db.create_database(db_name=db_name, using=self.alias)
            db.using_database(db_name=db_name, using=self.alias)
        
        self.index_params = {
            "metric_type":"L2",
            "index_type":"IVF_FLAT",
            "params":{"nlist":1024}
        } if not index_params else index_params
        
        self.search_params = {
            "metric_type": "L2",
            "offset": 0,
            "ignore_growing": False,
            "params": {"nprobe": 10}
        } if not search_params else search_params

    
    def list_database(self):
        db_list = db.list_database(using=self.alias)
        return db_list
    
    def using_database(self, db_name):
        db.using_database(db_name=db_name, using=self.alias)
        return f"Database {db_name} will be used."
    
    def create_collection(self, collection_name, schema, consistency_level="Strong"):
        collection_using = Collection(name=collection_name, schema=schema, using=self.alias, consistency_level=consistency_level)
        return collection_using
    
    def link_collection(self, collection_name):
        collection_using = Collection(name=collection_name, using=self.alias)
        return collection_using
    
    def list_collections(self):
        return utility.list_collections(using=self.alias)
    
    def drop_collection(self, collection_name):
        utility.drop_collection(collection_name=collection_name, using=self.alias)
        return f"Collection:{collection_name} has been dropped!"
    
    def check_collection(self, collection_name):
        return utility.has_collection(collection_name=collection_name, using=self.alias)
    
    def create_index(self, collection_using, field_name):
        collection_using.create_index(
            field_name=field_name,
            index_params=self.index_params
        )
        return "Indexes are created successfully"
        
    def insert(self, collection_using, data):

        insert_res = collection_using.insert(data)

        return insert_res      
        
    def search(self, collection_using, query, topk, anns_field, output_fields, search_params=None, expr=None):
        search_params_temp = self.search_params if search_params is None else search_params
        collection_using.load()

        results = collection_using.search(
            data=[query],
            anns_field=anns_field,
            param=search_params_temp,
            limit=topk,
            expr=expr,
            output_fields=output_fields,
            consistency_level="Strong"
        )

        return results

    def list_connections(self):
        connections_list = connections.list_connections()
        return connections_list
    
    def disconnect_connection(self, alias_name):
        connections.disconnect(alias_name)
        return f"connection {alias_name} has been disconnected."
    
    def remove_connection(self, alias_name):
        connections.remove_connection(alias_name)
        return f"connection {alias_name} has been removed."
    