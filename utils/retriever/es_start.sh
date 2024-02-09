#!/bin/bash

# 后台运行
ZHEM/utils/retriever/elasticsearch-7.13.2/bin/elasticsearch > ZHEM/utils/retriever/es_log.txt

# 检查是否成功启动
if [ $? -eq 0 ]; then
  echo "Elasticsearch started"
else
  echo "Elasticsearch failed"
fi
