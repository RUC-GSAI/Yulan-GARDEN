#coding:utf8
from pprint import pprint
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json, jsonlines
import time as t
from tqdm import tqdm, trange
import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument(
#     '--file', type=str, default="",
#     help='file to read'
#     ) # ../es_data/cleaned_data/wanjuan_1_split0.jsonl
# parser.add_argument('--only_count', action='store_true', default=False)
# args = parser.parse_args()

class ElasticObj:
    def __init__(self, index_name, index_type, ip="127.0.0.1", port="19200"):
        self.index_name = index_name
        self.index_type = index_type
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
        # print(self.es)
        # print("ElasticSearch connected successfully!")


    def create_index(self, index_name, index_type, properties):
        #创建映射
        _index_body = {
            "settings": {
                "index": {
                    "number_of_shards": "20",
                    "number_of_replicas": "1",
                },
                # "analysis": {
                    # "analyzer": {
                        # "my_english_analyzer": {
                        #     "type": "standard",
                        #     "max_token_length": 10,
                        #     "stopwords": "_english_"
                        # }
                    # }
                # },
                "similarity": {
                    "my_bm25": {
                        "type": "BM25",
                        "k1": 2.8, # 1.2,
                        "b": 0.3, # 0.75
                    }
                }
            },
            "mappings": {
                "properties": properties
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
                    "text": line['text'].strip(),
                    "source": line['source'], # "wanjuan",
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

if __name__ == '__main__':

    obj = ElasticObj(index_name="chinesewebtext", index_type="corpus")
    obj.count_all()
    if args.only_count:
        print("Only count. Exit.")
        exit()
    print(obj.es)
    
    
    # --------- 创建索引 ---------
    # properties = {
    #     "title": {
    #         "type": "text",
    #         # "analyzer": "whitespace",
    #         "analyzer": "my_english_analyzer",
    #         "similarity": "my_bm25"
    #     },
    #     "authors": {
    #         "type": "text",
    #         "analyzer": "my_english_analyzer",
    #         "similarity": "my_bm25"
    #     },
    #     "submitted_date": {
    #         "type": "text"
    #     },
    #     "abstract": {
    #         "type": "text",
    #         # "analyzer": "whitespace",
    #         "analyzer": "my_english_analyzer",
    #         "similarity": "my_bm25"
    #     },
    #     "pdf_link": {
    #         "type": "text"
    #     }
    # }

    properties = {
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
    # obj.create_index(obj.index_name, obj.index_type, properties=properties)
    

    # --------- 删除索引 ---------
    # obj.delete_index("wanjuan")
    exit()


    ### --------- 读文件 ---------
    
    # N = 19 # 总文件数
    # data = dict()
    # for i in range(10, N+10):
    #     rfile = "../data/data_" + str(i) + ".json"
    #     data = dict(data, **read_data(rfile))

    print(f"Reading file {args.file}...")
    t1 = t.time()
    data = read_data(args.file)
    print("Read time: {:.2f}s".format(t.time()-t1))
    total_num = len(data)
    print("%s items loaded." % total_num)
    # data = data[2600000:]
    # import pdb; pdb.set_trace()
    
    ### --------- 插入 ---------
    ### obj.Insert_Data(data)
    t2 = t.time()
    obj.bulk_Index_Data(data) # 20w/min; 6k-1.44s; 270k-77s
    print("Insert time: {:.2f}s".format(t.time()-t2))

    
    ### --------- 删除 ---------
    # for i in trange(obj.es.count(index=obj.index_name)['count'], ncols=80):
    #     obj.Delete_DocData_By_Id(str(i+1))
    
    
    ### --------- 查询 ---------
    # obj.Get_Data_By_Id(1)

    
    # doc = {
    #     "query": {
    #         "match": {
    #             "text": "你好"
    #         }
    #     },
    #     # "from": 1,
    #     "size": 3 # 默认返回10条
    #  }
    # res = obj.Get_Data_By_Body(doc)
    # print(res)
    




