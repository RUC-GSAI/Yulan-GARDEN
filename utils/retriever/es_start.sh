#!/bin/bash

# 前台运行，Ctrl + C 则程序终止
# elasticsearch

# 后台运行
elasticsearch -d

# 检查是否成功启动
if [ $? -eq 0 ]; then
  echo "Elasticsearch启动成功"
else
  echo "Elasticsearch启动失败"
fi


# 关闭ES服务
# kill pid
