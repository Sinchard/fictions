# -*- coding: utf-8 -*-
import scrapy


class MyItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()


class FictionItem(MyItem):
    fiction_id = scrapy.Field()
    save = scrapy.Field()
    updated = scrapy.Field()


class ChapterItem(MyItem):
    fiction_id = scrapy.Field()
    chapter_id = scrapy.Field()
    updated = scrapy.Field()


class ContentItem(scrapy.Item):
    fiction_id = scrapy.Field()
    chapter_id = scrapy.Field()
    #url = scrapy.Field()
    content = scrapy.Field()
    updated = scrapy.Field()
