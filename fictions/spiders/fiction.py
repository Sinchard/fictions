# -*- coding: utf-8 -*-
import scrapy


class FictionSpider(scrapy.Spider):
    name = 'fiction'
    allowed_domains = ['500shu.com']
    start_urls = ['http://500shu.com/']

    def parse(self, response):
        pass
