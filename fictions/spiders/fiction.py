# -*- coding: utf-8 -*-
import scrapy

#from myfiction.items import FictionURLItem
from myfiction.settings import FICTION_PRIORITY, CHAPTER_PRIORITY, CONTENT_PRIORITY, FICTION_URL, SITE_RANGE, SITE_URL, SITE_DOMAIN


class FictionSpider(scrapy.Spider):
    name = 'fiction'
    allowed_domains = [SITE_DOMAIN]

    # According to the settings param, yield the top list fictions' urls
    def start_requests(self):
        for i in range(SITE_RANGE):
            yield scrapy.Request(url=SITE_URL.format(i + 1), callback=self.parse)    

    def parseChapterUrl(self, response):
        pass

    # According to the settings param, get fiction url and parse the chapters' urls
    def parse(self, response):
        for f in response.xpath(FICTION_XPATH_IN_LIST):
            url = f.xpath("a/@href").get()
            url=FICTION_URL.format(url.split("/")[-2])
            if url is not None and url.strip() != "":
                yield scrapy.Request(url, callback=self.parseChapterUrl, priority=FICTION_PRIORITY)
