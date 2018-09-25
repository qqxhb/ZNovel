# !/usr/bin/env python
import os
import sys
import time
from owllook.database.es import ElasticObj
from owllook.spiders import DdSpider
# from owllook.spiders import QidianNovelSpider
os.environ['MODE'] = 'PRO'
sys.path.append('../../')


def start_spider():
    obj = ElasticObj("bupt", "novel")
    # obj.create_index()
    spider = DdSpider('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0')
    spider1 = DdSpider('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36')
    page = 0
    while page >= 0:
        if page % 2 == 0:
            result = spider.get_index_result("", page)
        else:
            result = spider1.get_index_result("", page)
        for data in result:
            if data:
                obj.Index_Item(data)
            else:
                page = -10
                break
        page = page+1
        print('page:'+str(page))
        time.sleep(1)


# def qidian_spider():
#     obj = ElasticObj("bupt", "novel")
#     obj.create_index()
#     spider = QidianNovelSpider('qidian_novel')
#     for data in spider.parse():
#         if data:
#             obj.Index_Item(data)
#         else:
#             break

def main():
    print("start============")
    start_spider()
    #qidian_spider()


if __name__ == '__main__':
    main()
# python novels_schedule.py

