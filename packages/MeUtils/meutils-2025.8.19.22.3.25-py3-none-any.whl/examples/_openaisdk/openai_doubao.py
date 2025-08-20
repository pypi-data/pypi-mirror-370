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

# 404 403 429
client = OpenAI(
    # api_key=os.getenv("OPENAI_API_KEY_GUOCHAN"),
    # api_key="sk-acnBrFLJo3E732FfHN0kf0tcHyjfAiCEomyjKr56AUtPIWso",
    # api_key="31c64288-e87d-4020-9d24-0ae6f4abaa7a",
    base_url="https://ark.cn-beijing.volces.com/api/v3",  # /chat/completions
    # base_url="https://api.ffire.cc/v1",
    api_key="80f33bac-41ac-4ea8-91ff-ef4e61720b23"

    # api_key=os.getenv("OPENAI_API_KEY") +'-3587'

)

try:
    completion = client.chat.completions.create(
        # model="ep-20241225184145-7nf5n",
        model="deepseek-r1-250528",
        # model="doubao-1-5-pro-32k-250115",
        # model="doubao-1-5-thinking-vision-pro-250428",

        # model="doubao-lite-32k-character",
        # model="doubao-pro-32k-character",

        # model="doubao-pro-32k-search",

        messages=[
            {"role": "user", "content": "你是谁"}
        ],
        # top_p=0.7,
        top_p=None,
        temperature=None,
        stream=False,
        stream_options={"include_usage": True},
        max_tokens=1,

        # extra_body={
        #     "thinking": {
        #         "type": "disabled"
        #     }
        # }
    )
except APIStatusError as e:
    print(e.status_code)

    print(e.response)
    print(e.message)
    print(e.code)

print(completion)
for chunk in completion:
    print(chunk)
    print(chunk.choices[0].delta.content)
