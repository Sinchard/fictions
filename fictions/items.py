# -*- coding: utf-8 -*-
import scrapy
from peewee import *

db = SqliteDatabase('fictions.db')


class MyItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()


class BaseModel(Model):
    id = AutoField()
    name = CharField(verbose_name="name", max_length=200, null=False)
    url = CharField(verbose_name="url", max_length=200, null=False)

    class Meta:
        database = db


class FictionItem(MyItem):
    fiction_id = scrapy.Field()


class Fictions(BaseModel):
    fiction_id = CharField(verbose_name="fiction_id", max_length=200, null=False)


class ChapterItem(MyItem):
    fiction_id = scrapy.Field()
    chapter_id = scrapy.Field()


class Chapters(BaseModel):
    fiction_id = CharField(verbose_name="fiction_id", max_length=200, null=False)
    chapter_id = CharField(verbose_name="chapter_id", max_length=100, null=False)


# get the fiction name and url
class ContentItem(MyItem):
    chapter_id = scrapy.Field()
    content = scrapy.Field()


class Contents(BaseModel):
    chapter_id = CharField(verbose_name="chapter_id", max_length=100, null=False)
    content = TextField(verbose_name="content")

