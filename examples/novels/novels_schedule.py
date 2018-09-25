#!/usr/bin/env python
import asyncio
import os
import uvloop

os.environ['MODE'] = 'PRO'
from owllook.fetcher.cache import update_all_books


def update_all():
    # asyncio.get_event_loop().run_until_complete(update_all_books())
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(update_all_books(loop=loop, timeout=15))
    loop.run_until_complete(task)
    return task.result() or None


if __name__ == '__main__':
    print(update_all())
