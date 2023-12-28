'''
Author: Aman
Date: 2023-11-30 17:36:10
Contact: cq335955781@gmail.com
LastEditors: Aman
LastEditTime: 2023-12-18 23:15:23
'''
from fastapi import FastAPI, Form
import uvicorn as u
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from ElasticSearch import *
import jieba.posseg as pseg
import re
import json
import time as t
import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

obj1 = ElasticObj(index_name="yl_corpus", index_type="corpus")
print(obj1.es)
obj2 = ElasticObj(index_name="chinesewebtext", index_type="corpus")
print(obj2.es)
obj3 = ElasticObj(index_name="wanjuan", index_type="corpus")
print(obj3.es)
obj4 = ElasticObj(index_name="zhihu", index_type="corpus")
print(obj4.es)


def query_arxiv(text, qtype):
    _candidates = []

    _doc = {
        "query": {
            "multi_match": {
                # "default_field": "abstract",
                "query": "",
                "fields": ["text"]
            }
        }
    }
    _doc['query']['multi_match']['query'] = text
    _doc['size'] = 50 # 最多返回50条
    if qtype == "zh_wiki":
        hits = obj1.Get_Data_By_Body(_doc)
    elif qtype == "chinesewebtext":
        hits = obj2.Get_Data_By_Body(_doc)
    elif qtype == "wanjuan":
        hits = obj3.Get_Data_By_Body(_doc)
    elif qtype == "zhihu":
        hits = obj4.Get_Data_By_Body(_doc)
    for hit in hits:
        candidate = {}
        candidate["text"] = hit["_source"]["text"]
        candidate["source"] = hit["_source"]["source"]
        candidate["score"] = hit["_score"]
        _candidates.append(candidate)

    return _candidates


@app.post("/text_search/")
async def read_text(
                    request:       Request,
                    query: str    = Form(...),
                    ):
    qtype = request.query_params.get("qtype")
    print("qtype:", qtype)
    t1 = t.time()
    res = query_arxiv(query, qtype)
    time_cost = round(t.time() - t1, 3)
    n = len(res)
    # 打印当前时间的query
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now_time + " _Query_: " + query)
    
    for item in res:
        item['score'] = round(item['score'], 3)
    if not n:
        return templates.TemplateResponse("no_results.html", {"request": request})
    else:
        return templates.TemplateResponse("results.html", {"request": request,
                                            "query": query,
                                            "N": n,
                                            "cost_time": time_cost,
                                            "res": res
                                        })


@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == '__main__':
    u.run(app, host="0.0.0.0", port=9002)

# uvicorn 1sthelloworld.py:app --reload



