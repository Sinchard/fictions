# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse

from fictions.items import FictionItem, ChapterItem, ContentItem
from fictions.settings import FICTION_PRIORITY, CHAPTER_PRIORITY, CONTENT_PRIORITY
from fictions.settings import SITE_RANGE, FICTION_URL, SITE_URL, SITE_DOMAIN


class FictionSpider(scrapy.Spider):
    name = 'fiction'
    allowed_domains = [SITE_DOMAIN]

    # According to the settings param, yield the top list fictions' urls
    def start_requests(self):
        for i in range(SITE_RANGE):
            yield scrapy.Request(url=SITE_URL.format(i + 1), callback=self.parse)

    def getContentItem(self, response):
        if response is None or not isinstance(response, HtmlResponse):
            return
        content = ContentItem()
        url = response.url
        content["fiction_id"] = url.split("/")[-2]
        content['chapter_id'] = url.split("/")[-1].split(".")[-2]
        title = response.xpath("//title/text()").get().strip()
        content["name"] = title.split("_")[1]
        # item['content'] = item.content.decode("gbk")
        # item['content'] = item.content.encode("utf8")
        content['content'] = response.xpath("//div[@id='nr1']").get().strip()
        return content

    def parseContentURL(self, response):
        content = self.getContentItem(response)
        if content['content'] is not None and content['content'] != "":
            yield content

        next_page = response.xpath("//td[@class='next']/@href").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parseContentURL, priority=CONTENT_PRIORITY)

    def getFictionItem(self, response):
        fiction = FictionItem()
        url = response.url
        fiction["fiction_id"] = url.split("/")[-2]
        title = response.xpath("//title/text()").get().strip()
        fiction["name"] = title.split(",")[0].split("最新")[0]
        fiction["url"] = url
        return fiction

    def parseChapterUrl(self, response):
        yield self.getFictionItem(response)

        for c in response.xpath("//ul[@class='chapter']/li"):
            # get chapter content
            url = c.xpath("a/@href").get()
            if url is not None:
                yield response.follow(url, callback=self.parseContentURL, priority=CONTENT_PRIORITY)
        # get next page url
        next_page = response.xpath("//div[@class='page']/a/@href")[0].get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parseChapterUrl, priority=CHAPTER_PRIORITY)

    # According to the settings param, get fiction url and parse the chapters' urls
    def parse(self, response):
        for f in response.xpath("//p[@class='line']"):
            url = f.xpath("a/@href").get()
            url = FICTION_URL.format(url.split("/")[-2])
            if url is not None and url.strip() != "":
                yield scrapy.Request(url, callback=self.parseChapterUrl, priority=FICTION_PRIORITY)
