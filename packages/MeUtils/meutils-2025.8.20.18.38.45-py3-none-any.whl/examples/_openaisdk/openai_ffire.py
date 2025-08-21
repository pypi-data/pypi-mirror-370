#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : openai_siliconflow
# @Time         : 2024/6/26 10:42
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import os

from meutils.pipe import *
from openai import OpenAI
from openai import OpenAI, APIStatusError

client = OpenAI(
    # base_url=os.getenv("FFIRE_BASE_URL"),
    # api_key=os.getenv("FFIRE_API_KEY") #+"-29463"

    base_url="http://127.0.0.1:8000/v1",

    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjMxMGNiZGFmLTM3NTQtNDYxYy1hM2ZmLTllYzgwMDUzMjljOSIsImxhc3RfcGFzc3dvcmRfY2hhbmdlIjoxNzUwNjYwODczLCJleHAiOjE3NTgxNTc1Njh9.eihH3NVrzJCg9bdWb9mim9rGKTLKn1a66kW2Cqc0uPM"
)
#
for i in range(1):
    try:
        completion = client.chat.completions.create(
            # model="kimi-k2-0711-preview",
            # model="deepseek-reasoner",
            # model="qwen3-235b-a22b-thinking-2507",
            # model="qwen3-235b-a22b-instruct-2507",
            model="qwen-image",

            messages=[
                {"role": "user", "content": 'a cat'}
            ],
            # top_p=0.7,
            top_p=None,
            temperature=None,
            # stream=True,
            max_tokens=1000,
            extra_body={"xx": "xxxxxxxx"}
        )
        print(completion)
    except Exception as e:
        print(e)

# model = "doubao-embedding-text-240715"
#
# r = client.embeddings.create(
#     input='hi',
#     model=model
# )
# print(r)
