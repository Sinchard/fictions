import re

from fictions.settings import SITE_RANGE
from fictions.spiders.fiction import FictionSpider


# url=http://m.500shuba.com/top/allvisit_1/
def match_list_url(url):
    url_patten = re.compile(r"http://m.500shuba.com/top/allvisit_\d+/")
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
        assert match_list_url(url)
        assert match_list_range(url)


def test_fiction_spider_parse(resource_get):
    pass


def test_fiction_spider_parse_chapter_url(resource_get):
    pass


def test_fiction_spider_parse_content(resource_get):
    pass
