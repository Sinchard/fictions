import re
import unittest

from betamax import Betamax
from requests import Session
from scrapy.http import HtmlResponse

from fictions.items import FictionItem, ContentItem
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


class Test_Fiction_Spider(unittest.TestCase):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
    }

    def setup_method(self):
        self.spider = FictionSpider()
        self.session = Session()

    def teardown_method(self):
        print('teardown_class()')

    def test_fiction_spider_start_requests(self):
        for request in self.spider.start_requests():
            url = request.url
            # print(url)
            assert match_url(url, LIST_URL_PATTEN)
            assert match_list_range(url)

    def test_fiction_spider_parse(self):
        request = next(self.spider.start_requests())
        with Betamax(self.session) as vcr:
            vcr.use_cassette('parse')
            resp = self.session.get(request.url, headers=self.headers)
            selector = HtmlResponse(body=resp.content, url=request.url, request=request)
            for request in self.spider.parse(selector):
                if isinstance(request, FictionItem):
                    assert request.check()
                else:
                    assert match_url(request.url, FICTION_URL_PATTEN)
                    assert request.priority == FICTION_PRIORITY

    def test_fiction_spider_parse_chapter_url(self):
        request = next(self.spider.start_requests())
        with Betamax(self.session) as vcr:
            vcr.use_cassette('parse_chapter')
            resp = self.session.get(request.url, headers=self.headers)
            selector = HtmlResponse(body=resp.content, url=request.url, request=request)
            chapter_request = next(self.spider.parse(selector))
            chapter_resp = self.session.get(chapter_request.url, headers=self.headers)
            chapter_selector = HtmlResponse(body=chapter_resp.content, url=request.url, request=chapter_request)
            for request in self.spider.parseChapterUrl(chapter_selector):
                if isinstance(request, ContentItem):
                    assert request.check()
                else:
                    assert match_url(request.url, FICTION_URL_PATTEN)
                    assert request.priority == FICTION_PRIORITY

    def test_fiction_spider_parse_content(self):
        pass
