#!/usr/bin/env python
import asyncio
import os
import uvloop

os.environ['MODE'] = 'PRO'

from pprint import pprint
from copy import deepcopy
from owllook.database.mongodb import MotorBase
from owllook.recommend.cosinesimilarity import CosineSimilarity
from owllook.fetcher.function import get_time


async def get_user_tag():
    motor_db = MotorBase().get_db()
    user_tag_cursor = motor_db.user_tag.find({}, {'data.user_tag': 1, 'user': 1, '_id': 0})
    result = {}
    async for document in user_tag_cursor:
        if document['data']['user_tag']:
            result[document['user'].replace('.', '&#183;')] = document['data']['user_tag']

    for key, value in result.items():
        result_copy = deepcopy(result)
        del result_copy[key]
        cos = CosineSimilarity(value, result_copy)
        vector = cos.create_vector()
        resultDic = cos.calculate(vector)
        pprint(resultDic)
        # pprint(type(resultList[1]))
        await motor_db.user_recommend.update_one(
            {"user": key},
            {'$set': {'similar_user': resultDic, 'user_tag': result[key], "updated_at": get_time()}}, upsert=True)


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def get_user_tag_test():
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(get_user_tag())
    loop.run_until_complete(task)
    return task.result()


if __name__ == '__main__':
    get_user_tag_test()
