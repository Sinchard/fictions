# -*- coding: utf-8 -*-
import scrapy

from fictions.items import FictionURLItem
from fictions.settings import CONTENT_XPATH_IN_CHAPTER, NEXT_PAGE_XPATH_IN_CONTENT, NEXT_PAGE_XPATH_IN_CHAPTER, \
    FICTION_XPATH_IN_LIST
from fictions.settings import FICTION_PRIORITY, CHAPTER_PRIORITY, CONTENT_PRIORITY
from fictions.settings import SITE_RANGE, FICTION_URL, SITE_URL, SITE_DOMAIN


class FictionSpider(scrapy.Spider):
    name = 'fiction'
    allowed_domains = [SITE_DOMAIN]

    # According to the settings param, yield the top list fictions' urls
    def start_requests(self):
        for i in range(SITE_RANGE):
            yield scrapy.Request(url=SITE_URL.format(i + 1), callback=self.parse)

    def parseContentURL(self, response):
        item = FictionURLItem()
        item['content'] = response.xpath(CONTENT_XPATH_IN_CHAPTER).get().strip()
        # item['content'] = item.content.decode("gbk")
        # item['content'] = item.content.encode("utf8")
        if item['content'] != None and item['content'] != "":
            item['name'] = response.xpath("//title/text()")[0].get().split("_")[0]
            # url = http://m.500shuba.com/html/32199/8964193.html
            url = response.url
            item['id'] = url.split("/")[-2]
            item['chapterid'] = url.split("/")[-1].split(".")[-2]
            yield item

        next = response.xpath(NEXT_PAGE_XPATH_IN_CONTENT).get()
        if next is not None:
            contenturl = response.urljoin(url)
            yield scrapy.Request(contenturl, callback=self.parseContentURL, priority=CONTENT_PRIORITY)

    def parseChapterUrl(self, response):
        for c in response.xpath(NEXT_PAGE_XPATH_IN_CHAPTER):
            # get chapter content
            url = c.xpath("a/@href").get()
            if url is not None:
                contenturl = response.urljoin(url)
                yield scrapy.Request(contenturl, callback=self.parseContentURL, priority=CONTENT_PRIORITY)
        # get next page url
        next_page = response.xpath(NEXT_PAGE_XPATH_IN_CHAPTER)[0].get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parseChapterUrl, priority=CHAPTER_PRIORITY)

    # According to the settings param, get fiction url and parse the chapters' urls
    def parse(self, response):
        for f in response.xpath(FICTION_XPATH_IN_LIST):
            url = f.xpath("a/@href").get()
            url = FICTION_URL.format(url.split("/")[-2])
            if url is not None and url.strip() != "":
                yield scrapy.Request(url, callback=self.parseChapterUrl, priority=FICTION_PRIORITY)
