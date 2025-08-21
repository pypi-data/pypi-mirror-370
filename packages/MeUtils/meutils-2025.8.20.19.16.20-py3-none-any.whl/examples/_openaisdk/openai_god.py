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
from openai import OpenAI, APIStatusError

client = OpenAI(
    api_key=os.getenv("GOD_API_KEY"),
    base_url=os.getenv("GOD_BASE_URL"),
)

try:
    completion = client.chat.completions.create(
        # model="net-gpt-3.5-turbo",
        # model="net-gpt-3.5-turbo-16k",
        # model="net-gpt-4o-mini",
        # model="net-gpt-4o",
        model="net-claude-1.3-100k",
        messages=[
            {"role": "user", "content": "南京天气如何"}
        ],
        # top_p=0.7,
        top_p=None,
        temperature=None,
        stream=True,
        max_tokens=6000
    )
except APIStatusError as e:
    print(e.status_code)

    print(e.response)
    print(e.message)
    print(e.code)

for chunk in completion:
    print(chunk.choices[0].delta.content)

