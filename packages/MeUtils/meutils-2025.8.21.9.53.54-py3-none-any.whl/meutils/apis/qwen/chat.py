#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : chat
# @Time         : 2025/8/19 13:22
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : qwen-image


from openai import AsyncOpenAI, OpenAI, AsyncStream

from meutils.pipe import *
from meutils.decorators.retry import retrying
from meutils.oss.ali_oss import qwenai_upload
from meutils.io.files_utils import to_bytes, guess_mime_type, to_url
from meutils.caches import rcache
from meutils.apis.images.edits import ImageProcess, edit_image

from meutils.llm.openai_utils import to_openai_params, create_chat_completion_chunk, token_encoder

from meutils.config_utils.lark_utils import get_next_token_for_polling
from meutils.schemas.openai_types import chat_completion, chat_completion_chunk, CompletionRequest, CompletionUsage, \
    ChatCompletion, Choice, ChatCompletionMessage
from meutils.schemas.image_types import ImageRequest, ImagesResponse

FEISHU_URL = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=PP1PGr"

base_url = "https://chat.qwen.ai/api/v2"
DEFAUL_MODEL = "qwen3-235b-a22b"
from fake_useragent import UserAgent

ua = UserAgent()

thinking_budget_mapping = {
    "low": 1000,
    "medium": 8000,
    "high": 24000
}

COOKIE = """
cna=KP9DIEqqyjUCATrw/+LjJV8F; _bl_uid=LXmp28z7dwezpmyejeXL9wh6U1Rb; cnaui=310cbdaf-3754-461c-a3ff-9ec8005329c9; aui=310cbdaf-3754-461c-a3ff-9ec8005329c9; sca=43897cb0; _gcl_au=1.1.106229673.1748312382.56762171.1748482542.1748482541; xlly_s=1; x-ap=ap-southeast-1; acw_tc=0a03e53917509898782217414e520e5edfcdef667dcbd83b767c0ce464fad4; token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjMxMGNiZGFmLTM3NTQtNDYxYy1hM2ZmLTllYzgwMDUzMjljOSIsImxhc3RfcGFzc3dvcmRfY2hhbmdlIjoxNzUwNjYwODczLCJleHAiOjE3NTM1ODE4ODV9.Npy24ubI717JmdSWMrodWSvVRHENgbJ7Knd-Yf158YE; atpsida=705b922fe336ee0d63fcc329_1750989888_2; SERVERID=e8c2af088c314df080fffe7d0976a96b|1750989892|1750910540; tfstk=gGtsWsqG4IKUeosYhNDUAMIBJRIbcvoz6-6vEKEaHGIOG-O2eZBabAYXRIR16hSOMpQpNtDMbtpTlWd2wNEAWA4XAOWy0FJtS6Ef3IDMbiQvps65XZYNg15fcKASLbor4dvGmGlra0WjM37NqSBAMS5d9TSfBJ35KivGmihEsEHyxdAMR0lwBiHCvt6uMiBYDMHC3TXOD1QY9yBR9iIAktIdpOX0DlCYWv9dtOsAMIQtdMChHfD7Ftg1sdMwtHJ00Jm2p6ZYDH6Ki1p6F9XBAwQOwwCQD9-CCN1JBhJB9QBXy3_MwXzN6UTkNTRZvlOWBCTRyhFKOivePI6WXYU5GCvpbwKt3zXhmFLRXnG76ppJBeLJBXzCdepwAw--No_MJCYllnlEqG8yUnbJXcNlTaXXNGLI9lOR4urPNGl0lJ_uc91rdva0oJN5AmdFjVAhW9X18vMQ6EbOK96ndva0oNBhCOMId5Lc.; isg=BNfX7gH7c3OJX_gfCBykQ2rtZk0hHKt-YCofVCkEq6YJWPSaPe8Dz9o-uvjGsIP2; ssxmod_itna=iqGxRDuQqWqxgDUxeKYI5q=xBDeMDWK07DzxC5750CDmxjKidKDUGQq7qdOamuu9XYkRGGm01DBL4qbDnqD80DQeDvYxk0K4MUPhDwpaW8YRw3Mz7GGb48aIzZGzY=0DgSdfOLpmxbD884rDYoDCqDSDxD99OdD4+3Dt4DIDAYDDxDWCeDBBWriDGpdhmbQVqmqvi2dxi3i3mPiDit8xi5bZendVL4zvDDlKPGf3WPt5xGnD0jmxhpdx038aoODzLiDbxEY698DtkHqPOK=MlTiRUXxAkDb9RG=Y2U3iA4G3DhkCXU3QBhxCqM2eeQmkeNzCwkjw/006DDAY2DlqTWweL04MKBeHhY5om5NUwYHuFiieQ0=/R=9iO9xTBhND4KF4dvyqz0/toqlqlzGDD; ssxmod_itna2=iqGxRDuQqWqxgDUxeKYI5q=xBDeMDWK07DzxC5750CDmxjKidKDUGQq7qdOamuu9XYkRGGmibDG85+YNY=exGa3Y64u5DBwiW7r++DxFqCdl=l77NQwckyAaCG64hkCOjO1pkcMRBdqj70N7nk=e94KEQYUxlf+2Dw=ViA+XKDde0uGS+eXgFkQqzYWe0Dd4oGbUj8L4QY4og345X2DjKDNOfQRgfeIKVRFQjqR098dBUrQsXBNQZcG1oBFAp4xkLYHl+W3OQW9ybPF4sML3t1tPX2T4DmCqKL+jN1XX94xpyA6k9+sgyBFY4zXOq7dHOuO3Gd3lidwdrk=8dNrOdrYQo33fobVS=MRF7nNQBC5d3kBbYdwtoxNBKmBiXoTfOTzOp3MT=ODXhxfO16Tta4vSW=ubtkEGgeQ/gKOwsVjmKDEY0NZ+ee7xlitvWmBbtk7ma7x1PinxtbitdadtYQOqG5AFEZbFxiSE6rDky7jiatQ0Fe7z6uDmYx4z5MGxMA5iDY7DtSLfNUYxU44D
""".strip()


class Completions(object):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    async def generate(self, request: ImageRequest, **kwargs):

        if request.image and not request.image.startswith("http"):
            request.image = await to_url(request.image, content_type="image/png")

        _ = CompletionRequest(
            model="qwen-image",
            stream=True,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": request.prompt},

                        {
                            "type": "image_url",
                            "image_url": {
                                "url": request.image
                            }
                        }

                    ],

                }
            ],
            size=request.aspect_ratio
        )

        async for chunk in await self.create(_):
            logger.debug(chunk)
            if chunk.choices and (url := chunk.choices[0].delta.content):
                if request.response_format == "oss_url":
                    request = ImageProcess(model="clarity", image=url)
                    url = await edit_image(request)

                return ImagesResponse(data=[{"url": url}])

        raise Exception("qwen-image 生成失败, 请重试")

    async def create(self, request: CompletionRequest, cookie: Optional[str] = None):
        api_key = self.api_key or await get_next_token_for_polling(feishu_url=FEISHU_URL, from_redis=True)

        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            default_headers={
                'User-Agent': ua.random,
                'Cookie': cookie or COOKIE
            }
        )

        chat_id = await self.create_new_chat()

        # request.last_user_content
        # request.last_urls.get("image_url", [])

        payload = {
            "chat_id": chat_id,
            "stream": request.stream,
            "incremental_output": True,
            "chat_mode": "normal",
            "model": "qwen3-235b-a22b",
            "messages": [
                {
                    "role": "user",
                    "content": request.last_user_content,

                    "user_action": "chat",
                    "files": [],
                    "models": [
                        "qwen3-235b-a22b"
                    ],
                    "chat_type": "t2t",
                    # "chat_type": "t2i",
                    # "chat_type": "image_edit",

                    "feature_config": {
                        "thinking_enabled": request.enable_thinking or False,
                        "output_schema": "phase"
                    },
                    "extra": {
                        "meta": {
                            "subChatType": "t2t"
                        }
                    }
                }
            ],
            "size": request.size if hasattr(request, "size") else "1:1"
        }

        if request.model.startswith("qwen-image"):
            payload["messages"][0]["chat_type"] = "t2i"

            logger.debug(request.last_urls)
            if image_urls := request.last_urls.get("image_url"):
                payload["messages"][0]["chat_type"] = "image_edit"
                payload["messages"][0]["files"] = [
                    {
                        "type": "image",
                        "name": "example.png",
                        "file_type": "image",
                        "showType": "image",
                        "file_class": "vision",
                        "url": image_urls[-1]  # todo 阿里对象存储
                    }
                ]

        data = to_openai_params(payload)
        logger.debug(bjson(data))
        response = await self.client.chat.completions.create(**data, extra_query={"chat_id": chat_id})
        # response = self.do_response(response)

        if isinstance(response, AsyncStream):  # image
            # async def gen():
            #     async for chunk in response:
            #         if url := chunk.choices[0].delta.content:
            #             yield f"[]{url}"

            return response

        else:
            logger.debug(response)

            if hasattr(response, "data") and (choices := response.data.get("choices")):
                response = response.model_construct(choices=choices)
                logger.debug(response)

            prompt_tokens = len(token_encoder.encode(str(request.messages)))
            completion_tokens = len(token_encoder.encode(str(response.choices[0].message.content)))
            usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
            response.usage = usage
            return response

    async def create_new_chat(self):
        payload = {
            "title": "新建对话",
            "models": [DEFAUL_MODEL],
            "chat_mode": "normal",
            "chat_type": "t2i",
            "timestamp": time.time() * 1000 // 1
        }
        resp = await self.client.post('/chats/new', body=payload, cast_to=object)
        logger.debug(resp)
        return resp['data']['id']


if __name__ == '__main__':
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjMxMGNiZGFmLTM3NTQtNDYxYy1hM2ZmLTllYzgwMDUzMjljOSIsImxhc3RfcGFzc3dvcmRfY2hhbmdlIjoxNzUwNjYwODczLCJleHAiOjE3NTgxNTc1Njh9.eihH3NVrzJCg9bdWb9mim9rGKTLKn1a66kW2Cqc0uPM"
    request = CompletionRequest(
        # model="qwen3-235b-a22b",
        model="qwen-image",

        messages=[

            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "带个墨镜"},

                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://oss.ffire.cc/files/kling_watermark.png"
                        }
                    }

                ],

            }
        ],
        stream=True,

        enable_thinking=True,

        size="16:9"

    )

    # arun(Completions(api_key=token).create(request))

    request = ImageRequest(
        model="qwen-image",
        prompt="带个墨镜",
        image="https://oss.ffire.cc/files/kling_watermark.png"
    )
    arun(Completions(api_key=token).generate(request))
