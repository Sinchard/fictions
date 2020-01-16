# -*- coding: utf-8 -*-
import scrapy
from peewee import *


class MyItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()


class FictionItem(MyItem):
    fiction_id = scrapy.Field()
    ifiction_id = scrapy.Field()


# get the fiction name and url
class ChapterItem(MyItem):
    fiction_id = scrapy.Field()
    chapter_id = scrapy.Field()


# get the fiction name and url
class ContentItem(scrapy.Item):
    fiction_id = scrapy.Field()
    chapter_id = scrapy.Field()
    content = scrapy.Field()
