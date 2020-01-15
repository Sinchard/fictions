# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse

from fictions.items import FictionItem, ContentItem
from fictions.settings import FICTION_PRIORITY, CHAPTER_PRIORITY, CONTENT_PRIORITY
from fictions.settings import SITE_RANGE, FICTION_URL, SITE_URL, SITE_DOMAIN


class FictionSpider(scrapy.Spider):
    name = 'fiction'
    allowed_domains = [SITE_DOMAIN]
    conn = None
    cursor = None

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
        content["ifiction_id"] = int(content["fiction_id"])
        content['dchapter_id'] = float(content['chapter_id'].replace('_', '.'))
        title = response.xpath("//title/text()").get().strip()
        content["name"] = title.split("_")[1]
        content["url"] = url
        # item['content'] = item.content.decode("gbk")
        # item['content'] = item.content.encode("utf8")
        content['content'] = response.xpath("//div[@id='nr1']").get().strip()
        return content

    def parseContentURL(self, response):
        self.log("Response Encoding: %s" % response.encoding)
        content = self.getContentItem(response)
        if content['content'] is not None and content['content'] != "":
            yield content

        next_page = response.xpath("//td[@class='next']/a/@href").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parseContentURL, priority=CONTENT_PRIORITY)

    def parseChapterUrl(self, response):
        print("Parsing Chapter Url:" + response.url)
        for c in response.xpath("//ul[@class='chapter']/li"):
            # get chapter content
            url = c.xpath("a/@href").get()
            fiction_id = url.split("/")[-2]
            chapter_id = url.split("/")[-1].split(".")[-2]
            if self.is_content_saved(int(fiction_id), float(chapter_id.replace('_', '.'))):
                continue
            else:
                if url is not None:
                    yield response.follow(url, callback=self.parseContentURL, priority=CONTENT_PRIORITY)
        # get next page url
        pages = response.xpath("//div[@class='page']/a/@href")
        for page in pages:
            next_page = page.get()
            if next_page is not None:
                yield response.follow(next_page, callback=self.parseChapterUrl, priority=CHAPTER_PRIORITY)

    def getFictionItem(self, f):
        fiction = FictionItem()
        url = f.xpath("a/@href").get()
        fiction_id = url.split("/")[-2]
        fiction["fiction_id"] = fiction_id
        fiction["ifiction_id"] = int(fiction["fiction_id"])
        fiction["name"] = f.xpath("a/text()").get()
        url = FICTION_URL.format(fiction_id)
        fiction["url"] = url
        return fiction

    # According to the settings param, get fiction url and parse the chapters' urls
    def parse(self, response):
        for f in response.xpath("//p[@class='line']"):
            item = self.getFictionItem(f)
            # Don't save the saved fiction
            if item.is_saved():
                continue
            else:
                yield item
            # Get the chapter information whether the fiction is saved
            url = item.url
            if url is not None and url.strip() != "":
                yield scrapy.Request(url, callback=self.parseChapterUrl, priority=FICTION_PRIORITY)
