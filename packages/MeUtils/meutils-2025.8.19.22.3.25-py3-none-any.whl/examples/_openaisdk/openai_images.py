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
import langchain
from meutils.pipe import *
from openai import OpenAI
from openai import OpenAI, APIStatusError

from openai import OpenAI

# response = OpenAI().images.generate(
#     model="stable-diffusion-3",
#     # model="kling",
#
#     prompt="a white siamese cat",
#     size="1024x1024",
#     quality="standard",
#     style="vividx",
#     n=1,
#     extra_body={
#         "guidance_scale": 4.5,
#         "num_inference_steps": 25,
#         "negative_prompt": ""
#     }
# )
#

# from openai import OpenAI
#
# response = OpenAI().images.generate(
#     # model="stable-diffusion-3",
#     model="kling",
#
#     prompt="漫天的星河，浪漫，神秘。超高清，最好的质量，超高细节的画质，8K分辨率",
#     size="1024x1024",
#     n=1
# )


data = {
    'prompt': '一只可爱的边牧在坐公交车，卡通贴纸。动漫3D风格，超写实油画，超高分辨率，最好的质量，8k',

    # 'model': 'step-1x-medium',
    'model': 'seededit',


    # 'n': 2, 'quality': 'hd', 'response_format': 'url', 'size': '1024x1024', 'style': 'vivid',
    # 'extra_body': {'guidance_scale': 4.5, 'num_inference_steps': 25, 'seed': None, 'negative_prompt': None}
}


from openai import OpenAI

# model = "stable-diffusion-3"
# with timer(model):
#     response = OpenAI(
#         # base_url="http://0.0.0.0:8000/v1"
#         # base_url="https://openai-dev.chatfire.cn/images/v1",
#         # base_url="https://openai.chatfire.cn/images/v1"
#
#         # base_url="http://111.173.117.175:40001/images/v1"
#         # base_url="https://api.stepfun.com/v1",
#         # api_key="4ewbnANQogxIX8DUY3Cz2VAMlB3ij39cwDrgQfkDtuNAoexu3E7CEJbR8USXVa3pA"
#     ).images.generate(
#         model=model,
#         prompt=prompt,
#     )
#     print(response)

# with timer('image'):
#     model = 'flux-schnell'
#
#     response = OpenAI(
#     ).images.generate(
#         model=model,
#         prompt=prompt,
#     )
#     print(response)
#
# with timer('image'):
#     model = 'flux-pro'
#
#     response = OpenAI(
#     ).images.generate(
#         model=model,
#         prompt=prompt,
#     )
#     print(response)

# model = 'step-1x-medium'
# with timer(model):
#     response = OpenAI().images.generate(
#         model=model,
#         prompt=prompt,
#     )
#     print(response)
#
# model = 'kling'
# with timer(model):
#     response = OpenAI().images.generate(
#         model=model,
#         prompt=prompt,
#     )
#     print(response)
#


with timer('image'):
    model = 'flux-pro'
    model = 'flux-dev'
    model = 'flux-schnell'
    # model = "cogview-3"

    # model = "cogview-3-plus"
    # model = "cogview-3-plus"

    # model = "cogview-3-plus"

    # model = 'step-1x-medium'
    # model = 'stable-diffusion-xl-base-1.0'
    # model = "black-forest-labs/flux.1.1-pro"

    # model = "black-forest-labs/FLUX.1-schnell"
    # model = "black-forest-labs/FLUX.1-dev"
    # model = "flux-dev"


    client = OpenAI(
        # api_key=os.getenv("OPENAI_API_KEY") +,
        # api_key=os.getenv("OPENAI_API_KEY") + "-359", # 3083
        # api_key=os.getenv("OPENAI_API_KEY_OPENAI") + "-3083",

        # api_key=os.getenv("SILICONFLOW_API_KEY"),
        # base_url=os.getenv("SILICONFLOW_BASE_URL"),

        # base_url='https://api.stepfun.com/v1',
        # base_url="http://0.0.0.0:8000/v1",
        # base_url='https://api-dev.chatfire.cn/v1',
        # base_url='https://openai-dev.chatfire.cn/api/v1',
        # base_url='https://openai.chatfire.cn/api/v1',
        # base_url="https://openai-dev.chatfire.cn/v1",

        # base_url="http://110.42.51.201:40009/v1"

        # base_url="https://oneapi.chatfire.cn/v1",

        base_url=os.getenv("MODELSCOPE_BASE_URL"),
        api_key=os.getenv("MODELSCOPE_API_KEY")

    )

    # print(client.models.list())
    # model = 'flux1.0-turbo'
    # model = 'flux1.0-schnell'
    model = 'flux-dev'
    model = "flux-schnell"
    model = "gpt-image-1"

    # model = 'flux1.0-dev'
    # model = 'flux1.0-pro'
    # model = 'flux1.1-pro'
    # model = 'kling'
    # model = 'hunyuan'
    # model = 'cogview-3'
    # model = 'stable-diffusion'
    # model = 'flux.1.1-pro'
    # model = 'flux'
    # model = 'stable-diffusion-3-5-large'
    # model = 'flux-schnell'
    # model = 'flux-schnell'
    # model = 'seededit'
    # model = 'dall-e-3'
    # model = 'kolors'
    # model = 'images'

    # model = "deepseek-ai/janus-pro-7b"
    # model="deepseek-ai/Janus-Pro-7B"

    # model = "flux.1.1-pro"
    # model = "ideogram-ai/ideogram-v2-turbo"

    # response = client.images.generate(
    #     model=model,
    #     prompt=prompt,
    #     extra_body={
    #         "num_inference_steps": 1,
    #         "prompt_enhancement": True
    #     },
    #     # size="1700x1275"
    # )

    # model = "recraft-v3"
    # model = "fal-ai/recraft-v3"
    # model = "flux-pro-1.1-ultra"
    prompt = '一只可爱的边牧在坐公交车，卡通贴纸。动漫3D风格，超写实油画，超高分辨率，最好的质量，8k'
    # prompt = "一个小女孩举着横幅，上面写着“新年快乐”"

    model = "doubao-seedream-3-0-t2i-250415"
    model = "black-forest-labs/FLUX.1-Krea-dev"
    model = "Qwen/Qwen-Image"

    response = client.images.generate(
        model=model,
        prompt=prompt,
        # response_format="b64_json",
        # extra_body={
        #     "Style": "True",
        #     "controls": {}, ######### 这个看起来更通用些
        #     "aspect_ratio": "1",
        #
        #     "Width": 1024,
        #     "Height": 1024,
        #     "prompt_enhancement": True,
        # },

        # size="1700x1275",

        extra_body={
            "extra_fields": {

                "watermark": False,

            }
        }
    )

    logger.debug(response)

    logger.debug(bjson(response.model_dump()))

# openai.AuthenticationError: Error code: 401 - {'error': {'message': 'Incorrect API key provided', 'type': 'invalid_api_key'}}
# openai.APIStatusError: Error code: 402 - {'error': {'message': 'You exceeded your current quota, please check your plan and billing details', 'type': 'quota_exceeded'}}



"""
import requests
import time
import json
from PIL import Image
from io import BytesIO

base_url = 'https://api-inference.modelscope.cn/'
api_key = "ms-81ccebd2-1933-4996-8c65-8e170d4f4264"

common_headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

response = requests.post(
    f"{base_url}v1/images/generations",
    headers={**common_headers, "X-ModelScope-Async-Mode": "true"},
    data=json.dumps({
        "model": "Qwen/Qwen-Image",  # ModelScope Model-Id, required
        "prompt": "A golden cat"
    }, ensure_ascii=False).encode('utf-8')
)

response.raise_for_status()
task_id = response.json()["task_id"]

while True:
    result = requests.get(
        f"{base_url}v1/tasks/{task_id}",
        headers={**common_headers, "X-ModelScope-Task-Type": "image_generation"},
    )
    result.raise_for_status()
    data = result.json()

    if data["task_status"] == "SUCCEED":
        image = Image.open(BytesIO(requests.get(data["output_images"][0]).content))
        image.save("result_image.jpg")
        break
    elif data["task_status"] == "FAILED":
        print("Image Generation Failed.")
        break

    time.sleep(5)
"""