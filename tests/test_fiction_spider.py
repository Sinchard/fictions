import re

from betamax import Betamax
from requests import Session
from scrapy.http import HtmlResponse

from fictions.settings import FICTION_PRIORITY
from fictions.settings import SITE_RANGE, LIST_URL_PATTEN, FICTION_URL_PATTEN
from fictions.spiders.fiction import FictionSpider


# url=http://m.500shuba.com/top/allvisit_1/
def match_url(url, patten):
    url_patten = re.compile(patten)
    if url_patten.match(url):
        return True
    else:
        return False


# url="http://m.500shuba.com/top/allvisit_1/"
def match_list_range(url):
    pattern = re.compile(r'\d+')
    list = pattern.findall(url)
    if len(list) == 2:
        page = int(list[1])
        return page > 0 and page <= SITE_RANGE
    else:
        return False


def test_fiction_spider_start_requests():
    spider = FictionSpider()
    for request in spider.start_requests():
        url = request.url
        # print(url)
        assert match_url(url, LIST_URL_PATTEN)
        assert match_list_range(url)


def test_fiction_spider_parse(resource_get):
    spider = FictionSpider()
    request = next(spider.start_requests())
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
    }
    session = Session()
    with Betamax(session) as vcr:
        vcr.use_cassette('parse')
        resp = session.get(request.url, headers=headers)
        selector = HtmlResponse(body=resp.content, url=request.url, request=request)
        for request in spider.parse(selector):
            assert match_url(request.url, FICTION_URL_PATTEN)
            assert request.priority == FICTION_PRIORITY


def test_fiction_spider_parse_chapter_url(resource_get):
    pass


def test_fiction_spider_parse_content(resource_get):
    pass
