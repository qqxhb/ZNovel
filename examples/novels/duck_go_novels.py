#!/usr/bin/env python
"""
 Created by howie.hu at 23/11/2017.
"""
import aiohttp
import asyncio
import async_timeout

from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse

from owllook.fetcher.function import get_random_user_agent
from owllook.config import CONFIG, LOGGER, BLACK_DOMAIN, RULES, LATEST_RULES


async def fetch(client, url, novels_name):
    with async_timeout.timeout(20):
        try:
            headers = {
                'user-agent': await get_random_user_agent(),
                'referer': "https://duckduckgo.com/"
            }
            params = {'q': novels_name}
            # , proxy="http://127.0.0.1:8118"
            async with client.get(url, params=params, headers=headers) as response:
                assert response.status == 200
                LOGGER.info('Task url: {}'.format(response.url))
                try:
                    text = await response.text()
                except:
                    text = await response.read()
                return text
        except Exception as e:
            LOGGER.exception(e)
            return None


async def data_extraction_for_web_duck(client, html):
    with async_timeout.timeout(15):
        try:
            try:
                title = html.select('h2 a')[0].get_text()
                url = html.select('h2 a')[0].get('href', None)
                url = parse_qs(url).get('uddg', ['#'])[0]
                netloc = urlparse(url).netloc
                url = url.replace('index.html', '').replace('Index.html', '')
                if not url or 'baidu' in url or 'baike.so.com' in url or netloc in BLACK_DOMAIN or '.html' in url:
                    return None
                is_parse = 1 if netloc in RULES.keys() else 0
                is_recommend = 1 if netloc in LATEST_RULES.keys() else 0
                # time = html.select('div.b_attribution')[0].get_text()
                # time = re.findall(r'\d+-\d+-\d+', time)
                # time = time[0] if time else ''
                timestamp = 0
                time = ''
                return {'title': title,
                        'url': url,
                        'time': time,
                        'is_parse': is_parse,
                        'is_recommend': is_recommend,
                        'timestamp': timestamp,
                        'netloc': netloc}

            except Exception as e:
                LOGGER.exception(e)
                url, title = None, None
                return None
        except Exception as e:
            LOGGER.exception(e)
            return None


async def duck_search(novels_name):
    url = CONFIG.DUCKGO_URL
    async with aiohttp.ClientSession() as client:
        html = await fetch(client=client, url=url, novels_name=novels_name)
        if html:
            soup = BeautifulSoup(html, 'html5lib')
            result = soup.find_all(class_='result')
            extra_tasks = [data_extraction_for_web_duck(client=client, html=i) for i in result]
            tasks = [asyncio.ensure_future(i) for i in extra_tasks]
            return await asyncio.gather(*tasks)
        else:
            return []


if __name__ == '__main__':
    import uvloop
    import time

    from pprint import pprint

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


    def novel_task(name):
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(duck_search(name))
        loop.run_until_complete(task)
        return task.result()


    start = time.time()
    result = novel_task('圣墟 小说 阅读 最新章节')
    pprint(result)
    print(time.time() - start)
