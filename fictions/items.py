# -*- coding: utf-8 -*-
from datetime import datetime
import scrapy

from .settings import FICTION_URL


def get_chapter_id(url):
    return float(url.split("/")[-1].split(".")[-2].replace('_', '.'))


def get_fiction_id(url):
    return int(url.split("/")[-2])


class MyItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()


class FictionItem(MyItem):
    fiction_id = scrapy.Field()
    save = scrapy.Field()
    updated = scrapy.Field()

    @classmethod
    def create(cls, fiction_a):
        item = FictionItem()
        url = fiction_a.xpath("a/@href").get()
        item["fiction_id"] = get_fiction_id(url)
        item["name"] = fiction_a.xpath("a/text()").get()
        item["url"] = FICTION_URL.format(item["fiction_id"])
        item["save"] = 1
        item["updated"] = datetime.now()
        return item


class ChapterItem(MyItem):
    fiction_id = scrapy.Field()
    chapter_id = scrapy.Field()
    updated = scrapy.Field()

    @classmethod
    def create(cls, chapter_a):
        item = ChapterItem()
        url = chapter_a.xpath("a/@href").get()
        item["url"] = url
        item["name"] = chapter_a.xpath("a/text()").get()
        item["fiction_id"] = get_fiction_id(url)
        item["chapter_id"] = get_chapter_id(url)
        item["updated"] = datetime.now()
        return item


class ContentItem(scrapy.Item):
    fiction_id = scrapy.Field()
    chapter_id = scrapy.Field()
    content = scrapy.Field()
    updated = scrapy.Field()

    @classmethod
    def create(cls, response):
        item = ContentItem()
        url = response.url
        item["fiction_id"] = get_fiction_id(url)
        item["chapter_id"] = get_chapter_id(url)
        item["content"] = response.xpath("//div[@id='nr1']").get().strip()
        item["updated"] = datetime.now()
        return item
