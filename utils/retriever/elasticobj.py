from pprint import pprint
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json, jsonlines
import time as t
from tqdm import tqdm, trange
import argparse


class ElasticObj:
    def __init__(self, index_name, ip="127.0.0.1", port="19201"):
        self.index_name = index_name
        # 无用户名密码状态
        self.es = Elasticsearch(
            [{'host':ip, 'port':port}],
            # 在做任何操作之前，先进行嗅探
            sniff_on_start=True,
            # 节点没有响应时，进行刷新，重新连接
            sniff_on_connection_fail=True,
            # 每 60 秒刷新一次
            sniffer_timeout=60,
            # set sniffing request timeout to 10 seconds
            sniff_timeout=30,
            timeout=300,
            max_retries=10,
            retry_on_timeout=True
            )


    def create_index(self, index_name):
        #创建映射
        _index_body = {
            "settings": {
                "index": {
                    "number_of_shards": "20",
                    "number_of_replicas": "1",
                },
                "similarity": {
                    "my_bm25": {
                        "type": "BM25",
                        "k1": 2.8, # 1.2,
                        "b": 0.3, # 0.75
                    }
                }
            },
            "mappings": {
                "properties":  {
                    "text": {
                        "type": "text",
                        "analyzer": "ik_smart",
                        "similarity": "my_bm25",
                        "position_increment_gap": 10
                    },
                    "source": {
                        "type": "text"
                    },
                }
            }
        }
        if self.es.indices.exists(index=index_name) is not True:
            res = self.es.indices.create(index=index_name, body=_index_body)
            print(res)
        else:
            print('Index %s already exists!' % index_name)


    def delete_index(self, index_name=None):
        # 删除索引
        if self.es.indices.exists(index=index_name):
            res = self.es.indices.delete(index_name)
            if res['acknowledged'] == True:
                print('Delete index %s successfully!' % index_name)
            else:
                print(res)
                print('Fail to delete index %s!' % index_name)
        else:
            print('Index %s does not exist!' % index_name)


    def Insert_Data(self, data):
        # 数据存储到es
        total_num = self.es.count(index=self.index_name)['count']
        # res = self.es.index(index=self.index_name, doc_type=self.index_type, body=item) # 自动生成id
        res = self.es.create(index=self.index_name, id=total_num+1, body=item)
        # pprint(res)
        # if res['result'] == 'created': # 插入成功
        #    success += 1


    def bulk_Index_Data(self, data):
        # 用bulk将批量数据存储到es
        ACTIONS = []
        i = 1
        total_num = self.es.count(index=self.index_name)['count']
        for line in tqdm(data, ncols=80):
            action = {
                "_index": self.index_name,
                # "_type": self.index_type,
                "_id": total_num + i, #_id 也可以默认生成，不赋值
                "_source": {
                    "text": line['text'].strip()
                    # "source": line['source'], # "wanjuan",
                 }
            }
            i += 1
            ACTIONS.append(action)
            if len(ACTIONS) == 100000:
                # 批量处理
                success, _ = bulk(self.es, ACTIONS, index=self.index_name, raise_on_error=True, request_timeout=100)
                print('Successfully performed %d / %d actionis.' % (success, len(ACTIONS)))
                ACTIONS = []
        if len(ACTIONS) > 0:
            success, _ = bulk(self.es, ACTIONS, index=self.index_name, raise_on_error=True, request_timeout=100)
            print('Successfully performed %d / %d actionis.' % (success, len(ACTIONS)))

    def count_all(self):
        total_num = self.es.count(index=self.index_name)['count']
        print('Total %d items in ES.' % (total_num))

    def Delete_DocData_By_Id(self, docid):
        # 删除索引中的一条
        res = self.es.delete(index=self.index_name, id=docid)
        # print(res)


    def Get_Data_By_Id(self, qid):
        res = self.es.get(index=self.index_name, id=qid)
        pprint(res['_source'])
        

    def Get_Data_By_Body(self, doc):
        _searched = self.es.search(index=self.index_name, body=doc)
        # pprint(_searched)
        # for hit in _searched['hits']['hits']:
        #     print(hit['_source'], hit['_score'])
        return _searched['hits']['hits']

    
def read_data(rfile):
    if rfile.endswith('.json'):
        with open(rfile, 'r') as f:
            data = json.load(f)
    elif rfile.endswith('.jsonl'):
        with jsonlines.open(rfile) as reader:
            data = []
            for obj in reader:
                data.append(obj)
    return data