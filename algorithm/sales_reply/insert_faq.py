import os
import sys
import json
import requests
import numpy as np
from tqdm import tqdm
from pymilvus import FieldSchema, DataType, CollectionSchema
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)

from utils.MilvusDB import Milvus
from utils.m3e_embedding import m3e_embedding

def insert_faq(industry_id, brand_id, template_id, faq_content):
    industry_dict = {"医美": "medical"}
    brand_dict = {"美丽人生": "beauty"}
    template_dict = {"美丽人生经典模版1": "classic_template1"}
    alias_name = "smart_salesman"
    milvus_instance = Milvus(alias_name)
    collection_name = industry_dict[industry_id] + "_" + brand_dict[brand_id] + "_" + template_id[template_id]

    faq_id = FieldSchema(name='faq_id', dtype=DataType.INT8, is_primary=True)
    faq_query = FieldSchema(name='faq_query', dtype=DataType.FLOAT_VECTOR, dim=768)
    faq_answer = FieldSchema(name='faq_answer', dtype=DataType.VARCHAR, max_length=1024)
    schema = CollectionSchema(fields=[faq_id, faq_query, faq_answer], description="faq知识库")

    collection_identify = milvus_instance.create_collection(collection_name, schema)
    milvus_instance.create_index(collection_using=collection_identify, field_name='faq_query')
    faq_base = [json.loads(line) for line in faq_content.strip().split('\n')]
    faq_id_list = []
    faq_query_list = []
    faq_answer_list = []
    for idx, faq in tqdm(enumerate(faq_base)):
        faq_id_list.append(idx)
        faq_query_list.append(m3e_embedding(faq['query']))
        faq_answer_list.append(faq['answer'])
    insert_data = [faq_id_list, faq_query_list, faq_answer_list]
    insert_res = milvus_instance.insert(collection_using=collection_identify, data=insert_data)

    milvus_instance.disconnect(alias_name=alias_name)
    return f"FAQ insert to {collection_name} collection successfully!"

if __name__ == '__main__':
    industry_id = "医美"
    brand_id = "美丽人生"
    template_id = "美丽人生经典模版1"
    faq_content = """
        {"query": "有什么瘦脸项目", "answer": "有我们自己的丽人瘦脸针、丽人瘦脸吸脂、丽人瘦脸手术等项目"}
        {"query": "瘦脸针是什么", "answer": "瘦脸针是一种注射瘦脸针，通过注射瘦脸针来达到瘦脸的效果"}
        {"query": "瘦脸吸脂是什么", "answer": "瘦脸吸脂是一种通过吸脂来达到瘦脸的效果"}
        {"query": "瘦脸手术是什么", "answer": "瘦脸手术是一种通过手术来达到瘦脸的效果"}
        {"query": "瘦脸针有什么副作用", "answer": "瘦脸针的副作用包括面部肿胀、疼痛、红肿、淤血等，但这些副作用通常是暂时的，并且会在几天内自行消失。如果出现严重的副作用，应立即就医。"}
    """
    insert_faq(industry_id, brand_id, template_id, faq_content)



