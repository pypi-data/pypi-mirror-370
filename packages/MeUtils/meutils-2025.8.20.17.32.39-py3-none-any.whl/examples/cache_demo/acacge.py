#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : acacge
# @Time         : 2024/9/30 15:19
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *

from aiocache import cached, Cache

# cache = Cache.from_url(os.getenv('REDIS_URL'))


@cached(ttl=10, cache=Cache.REDIS, key="key")
async def cached_call():
    print("Sleeping for three seconds zzzz.....")
    await asyncio.sleep(3)
    return time.time()


if __name__ == '__main__':
    arun(cached_call())
