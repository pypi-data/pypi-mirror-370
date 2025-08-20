#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : z.py
# @Time         : 2025/8/19 08:32
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 


from meutils.pipe import *
from meutils.caches import rcache
from meutils.db.redis_db import redis_aclient

from openai import AsyncOpenAI
from meutils.llm.openai_utils import to_openai_params, create_chat_completion_chunk

from meutils.schemas.openai_types import CompletionRequest, chat_completion_chunk, chat_completion

from meutils.decorators.retry import retrying
from meutils.config_utils.lark_utils import get_next_token_for_polling

from fake_useragent import UserAgent

ua = UserAgent()

BASE_URL = "https://chat.z.ai/api"
FEISHU_URL = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=9VvErr"


class Completions(object):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    async def create(self, request: CompletionRequest, token: Optional[str] = None):
        token = token or await get_next_token_for_polling(FEISHU_URL)

        chat_id = str(uuid.uuid4())
        payload = {
            "id": chat_id,
            "chat_id": chat_id,
            "model": "0727-360B-API",

            "stream": True,

            "params": {},
            "features": {
                "image_generation": False,
                "web_search": False,
                "auto_web_search": False,
                "preview_mode": False,
                "flags": [],
                "features": [
                    {
                        "type": "mcp",
                        "server": "vibe-coding",
                        "status": "hidden"
                    },
                    {
                        "type": "mcp",
                        "server": "ppt-maker",
                        "status": "hidden"
                    },
                    {
                        "type": "mcp",
                        "server": "image-search",
                        "status": "hidden"
                    }
                ],
                "enable_thinking": request.enable_thinking or False
            },

            "background_tasks": {
                "title_generation": False,
                "tags_generation": False
            }
        }

        payload = {**request.model_dump(), **payload}

        data = to_openai_params(payload)

        # todo 代理
        client = AsyncOpenAI(base_url=BASE_URL, api_key=token, default_headers={"X-FE-Version": "prod-fe-1.0.69"})
        response = await client.chat.completions.create(**data)
        response = self.do_response(response, request.stream)

        # async for i in response:
        #     logger.debug(i)

        return response

    async def do_response(self, response, stream: bool):
        usage = None
        nostream_content = ""
        nostream_reasoning_content = ""
        chat_completion_chunk.model = "glm-4.5"
        async for i in response:
            # print(i)

            delta_content = (
                    i.data.get("delta_content", "").split(' ')[-1]
                    or i.data.get("edit_content", "").split("\n")[-1]
            )
            if i.data.get("phase") == "thinking":
                nostream_reasoning_content += delta_content
                chat_completion_chunk.choices[0].delta.reasoning_content = delta_content

            elif i.data.get("phase") == "answer":
                nostream_content += delta_content
                chat_completion_chunk.choices[0].delta.content = delta_content

            else:
                logger.debug(bjson(i))

            if stream:
                yield chat_completion_chunk

            usage = usage or i.data.get("usage", "")

        if not stream:
            chat_completion.choices[0].message.content = nostream_content
            chat_completion.choices[0].message.reasoning_content = nostream_reasoning_content
            chat_completion.usage = usage
            chat_completion.model = "glm-4.5"
            yield chat_completion


if __name__ == '__main__':
    token = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImI0YThkMTI5LWY2YzgtNDM5Mi1iYzlhLWEyNjM1Nzg0ZDM5MyIsImVtYWlsIjoiemJqZ2NlZ2NsbkB0aXRrLnVrIn0.cME4z8rip8Y6mQ0q_JEoY6ywPk_7ud2BsyFHyPRhFhtzEl_uLcQEMNlop7hM_fTy0S5pS8qdLK5y7iA1it0n7g"

    request = CompletionRequest(
        model="glm-4.5",
        messages=[
            {
                "role": "system",
                "content": "你是gpt",

            },
            {
                "role": "user",
                "content": [{"type": "text", "text": "周杰伦"}],
                # "content": "你是谁",

            }
        ],
        stream=True,

        enable_thinking=True

    )

    arun(Completions().create(request, token))
