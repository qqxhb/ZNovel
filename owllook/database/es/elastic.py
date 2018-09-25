#coding:utf8
from elasticsearch import Elasticsearch

class ElasticObj:
    def __init__(self, index_name, index_type, ip="47.93.60.158"):
        self.index_name = index_name
        self.index_type = index_type
        # 无用户名密码状态
        self.es = Elasticsearch([ip])

    def create_index(self):
        '''
        创建索引
        :param ex: Elasticsearch对象
        :return:
        '''
        #创建映射
        _index_mappings = {
            "mappings": {
                self.index_type: {
                    "properties": {
                        "title": {
                            "type": "text",
                            "index": True,
                            "analyzer": "ik_max_word",
                            "search_analyzer": "ik_max_word"
                        },
                        "author": {
                            "type": "text",
                            "index": True,
                            "analyzer": "ik_max_word",
                            "search_analyzer": "ik_max_word"
                        },
                        "profile": {
                            "type": "text",
                            "analyzer": "ik_max_word",
                            "search_analyzer": "ik_max_word"
                        },
                        "image": {
                            "type": "text"
                        },
                        "type": {
                            "type": "text"
                        },
                        "time": {
                            "type": "date"
                        },
                        "url": {
                            "type": "text"
                        }
                    }
                }

            }
        }
        if self.es.indices.exists(index=self.index_name) is not True:
            res = self.es.indices.create(index=self.index_name, body=_index_mappings)
            print(res)

    def Index_List(self,list):
        '''
        数据存储到es
        :return:
        '''
        for item in list:
            res = self.es.index(index=self.index_name, doc_type=self.index_type, body=item)
            print('created')

    def Index_Item(self, item):
        res = self.es.index(index=self.index_name, doc_type=self.index_type, body=item)
        print('created')

    def Delete_Index(self, id):
        '''
        删除索引中的一条
        :param id:
        :return:
        '''
        res = self.es.delete(index=self.index_name, doc_type=self.index_type, id=id)
        print (res)

    def Get_Data_By_Body(self, doc, param):
        # doc = {'query': {'match_all': {}}}
        _searched = self.es.search(index=self.index_name, doc_type=self.index_type, body=doc,params=param)
        return _searched['hits']



# obj.bulk_Index_Data()
# obj.IndexData()
# obj.Delete_Index_Data(1)
# csvfile = 'D:/work/ElasticSearch/exportExcels/2017-08-31_info.csv'
# obj.Index_Data_FromCSV(csvfile)
# obj.GetData(es)