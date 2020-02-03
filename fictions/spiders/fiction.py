# -*- coding: utf-8 -*-
from datetime import datetime

from scrapy.http import HtmlResponse

from fictions.items import *
from fictions.models import *
from fictions.settings import FICTION_PRIORITY, CHAPTER_PRIORITY, CONTENT_PRIORITY
from fictions.settings import SITE_RANGE, FICTION_URL, SITE_URL, SITE_DOMAIN


def is_saved(model, *args):
    count = 0
    if len(args) > 1:
        count = model.select().where(model.fiction_id == args[0],
                                     model.chapter_id == args[1]).count()
    elif len(args) == 1:
        count = model.select().where(model.fiction_id == args[0]).count()
    return count > 0


class FictionSpider(scrapy.Spider):
    name = 'fiction'
    allowed_domains = [SITE_DOMAIN]
    conn = None
    cursor = None

    # According to the settings param, yield the top list fictions' urls
    def start_requests(self):
        for i in range(SITE_RANGE):
            url = SITE_URL.format(i + 1)
            self.log(url)
            yield scrapy.Request(url=url, callback=self.parse)

    def parseContentURL(self, response):
        self.log("Response Encoding: %s" % response.encoding)
        item = ContentItem.create(response)
        if item['content'] is not None and item['content'] != "":
            yield item
        # get next page url
        next_page = response.xpath("//td[@class='next']/a/@href").get()
        if next_page is not None:
            yield response.follow(next_page,
                                  callback=self.parseContentURL,
                                  priority=CONTENT_PRIORITY)

    def parseChapterUrl(self, response):
        print("Parsing Chapter Url:" + response.url)
        for c in response.xpath("//ul[@class='chapter']/li"):
            # get chapter content
            item = ChapterItem.create(c)
            if is_saved(ChapterModel, item["fiction_id"], item["chapter_id"]):
                self.log("Fiction %d Chapter %d is saved" %
                         (item['fiction_id'], item["chapter_id"]))
                continue
            else:
                yield item
                yield response.follow(item["url"],
                                        callback=self.parseContentURL,
                                        priority=CONTENT_PRIORITY)
        # get next page url
        pages = response.xpath("//div[@class='page']/a/@href")
        for page in pages:
            next_page = page.get()
            if next_page is not None and next_page.strip() != "":
                yield response.follow(next_page,
                                      callback=self.parseChapterUrl,
                                      priority=CHAPTER_PRIORITY)

    # According to the settings param, get fiction url and parse the chapters' urls
    def parse(self, response):
        self.log(response.request.url)
        for f in response.xpath("//p[@class='line']"):
            item = FictionItem.create(f)
            # Get the chapter information whether the fiction is saved
            url = item["url"]
            if url is not None and url.strip() != "":
                yield scrapy.Request(url,
                                     callback=self.parseChapterUrl,
                                     priority=FICTION_PRIORITY)
            # Don't save the saved fiction
            if is_saved(FictionModel, item['fiction_id']):
                self.log("Fiction %d is saved" % item['fiction_id'])
                continue
            else:
                yield item
            
