#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : generations
# @Time         : 2025/6/11 17:06
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 统一收口

from meutils.pipe import *
from meutils.llm.clients import AsyncClient
from meutils.llm.openai_utils import to_openai_params

from meutils.schemas.image_types import ImageRequest

from meutils.apis.fal.images import generate as fal_generate

from meutils.apis.gitee.image_to_3d import generate as image_to_3d_generate
from meutils.apis.gitee.openai_images import generate as gitee_images_generate


async def generate(
        request: ImageRequest,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
):
    if base_url:  # 优先级最高
        client = AsyncClient(api_key=api_key, base_url=base_url)
        return await client.images.generate(**to_openai_params(request))

    if request.model.startswith("fal-ai"):
        return await fal_generate(request, api_key)

    if request.model in {"Hunyuan3D-2", "Hi3DGen", "Step1X-3D"}:
        return await image_to_3d_generate(request, api_key)

    if request.model in {"Qwen-Image", "FLUX_1-Krea-dev"}:
        return await gitee_images_generate(request, api_key)


# "flux.1-krea-dev"

if __name__ == '__main__':
    # arun(generate(ImageRequest(model="flux", prompt="笑起来")))
    arun(generate(ImageRequest(model="FLUX_1-Krea-dev", prompt="笑起来")))
