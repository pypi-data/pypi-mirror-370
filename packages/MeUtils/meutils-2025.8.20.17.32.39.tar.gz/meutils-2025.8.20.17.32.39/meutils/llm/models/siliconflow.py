#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : siliconflow
# @Time         : 2025/8/15 20:29
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *
from meutils.llm.clients import OpenAI

models_mapping = {
    "glm-4.5": "zai-org/GLM-4.5",
    "glm-4.5v": "zai-org/GLM-4.5V",

    "deepseek-v3": "deepseek-ai/DeepSeek-V3",
    "deepseek-v3-0324": "deepseek-ai/DeepSeek-V3",
    "deepseek-v3-250324": "deepseek-ai/DeepSeek-V3",
    "deepseek-chat": "deepseek-ai/DeepSeek-V3",
    "qwen3-32b": "Qwen/Qwen3-32B",
    "deepseek-r1": "deepseek-ai/DeepSeek-R1",
    "deepseek-r1-250528": "deepseek-ai/DeepSeek-R1",
    "deepseek-reasoner": "deepseek-ai/DeepSeek-R1",
    "qwen2.5-72b-instruct": "Qwen/Qwen2.5-72B-Instruct-128K",
    "kimi-k2-0711-preview": "moonshotai/Kimi-K2-Instruct",
    "moonshotai/kimi-k2-instruct": "moonshotai/Kimi-K2-Instruct",
    "qwen2.5-vl-32b-instruct": "Qwen/Qwen2.5-VL-32B-Instruct",
    "qwen2.5-vl-72b-instruct": "Qwen/Qwen2.5-VL-72B-Instruct",
    "qwen2.5-vl-7b-instruct": "Qwen/Qwen2.5-VL-7B-Instruct",
    "minimax-m1-80k": "MiniMaxAI/MiniMax-M1-80k",
    "qvq-72b-preview": "Qwen/QVQ-72B-Preview",
    "qwen2.5-7b-instruct": "Qwen/Qwen2.5-7B-Instruct",
    "deepseek-r1:1.5b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    "deepseek-r1-distill-qwen-1.5b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    "deepseek-r1:7b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    "deepseek-r1-distill-qwen-7b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    "deepseek-r1:8b": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
    "deepseek-r1-distill-llama-8b": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
    "qwen2.5-32b-instruct": "Qwen/Qwen2.5-32B-Instruct"
}


def get_models_mapping():
    client = OpenAI(
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        base_url=os.getenv("SILICONFLOW_BASE_URL"),
    )

    models = client.models.list().data
    models = {
        m.id.removeprefix("Pro/").split('/', maxsplit=1)[-1].lower(): m.id.removeprefix("Pro/") for m in models
    }
    return {**models, **models_mapping}


if __name__ == '__main__':
    data = get_models_mapping()
    print(bjson(data))
    print(','.join(data))
