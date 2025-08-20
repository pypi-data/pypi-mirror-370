import logging

import pymongo
import pytz


def db_save_dict_to_mongodb(
        mongo_db_client_link: str,
        mongo_db_name: str,
        col_name: str,
        target_dict: dict
):
    c = pymongo.MongoClient(mongo_db_client_link)
    db = c[mongo_db_name]
    db_col = db[col_name]
    if not isinstance(target_dict, list):
        target_dict = [target_dict]
    if len(target_dict) == 0:
        logging.error('准备存入db的数据为空，不能保存！')
        return
    item = db_col.insert_many(target_dict)
    return item.inserted_ids


def db_update_dict_to_mongodb(
        mongo_db_client_link: str,
        mongo_db_name: str,
        col_name: str,
        query_dict: dict,
        target_dict: dict,
        upsert: bool = False
):
    c = pymongo.MongoClient(mongo_db_client_link)
    db = c[mongo_db_name]
    db_col = db[col_name]
    update_result = db_col.update_one(
        query_dict, {"$set": target_dict}, upsert=upsert)
    return update_result


def db_get_dict_from_mongodb(
        mongo_db_client_link: str,
        mongo_db_name: str,
        col_name: str,
        query_dict: dict = {},
        field_dict: dict = {},
        inc_id: bool = False
):
    '''

    :param mongo_db_name:
    :param col_name:
    :param query_dict:
    :param field_dict: {'column1':1, 'column2':1}
    :return:
    '''
    c = pymongo.MongoClient(
        host=mongo_db_client_link,
        tz_aware=True,
        tzinfo=pytz.timezone('Asia/Chongqing')
    )
    db = c[mongo_db_name]
    db_col = db[col_name]
    if not inc_id:
        field_dict['_id'] = 0
    result_dict_list = [x for x in db_col.find(query_dict, field_dict)]
    return result_dict_list


def db_get_distinct_from_mongodb(
        mongo_db_client_link: str,
        mongo_db_name: str,
        col_name: str,
        field: str,
        query_dict: dict = {}
):
    c = pymongo.MongoClient(
        host=mongo_db_client_link,
        tz_aware=True,
        tzinfo=pytz.timezone('Asia/Chongqing')
    )
    db = c[mongo_db_name]
    db_col = db[col_name]
    result_list = db_col.distinct(field, query=query_dict)
    return result_list


def db_del_dict_from_mongodb(
        mongo_db_client_link: str,
        mongo_db_name: str,
        col_name: str,
        query_dict: dict
):
    c = pymongo.MongoClient(mongo_db_client_link)
    db = c[mongo_db_name]
    db_col = db[col_name]
    x = db_col.delete_many(query_dict)
    return x.deleted_count
