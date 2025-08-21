# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
"""
【question】
Dockerfile中wget总是报443
【solution】
在Dockerfile中增加：
RUN apt-get update && apt-get install -y ca-certificates wget
RUN update-ca-certificates

【question】
Docker中的bash文件运行报错：bash \r；该错误由于在windows运行环境下自动追加\r结尾符导致的
【solution】
在Dockerfile中增加：
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        dos2unix \
RUN dos2unix /[your_bash].sh
"""