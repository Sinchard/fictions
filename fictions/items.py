# -*- coding: utf-8 -*-
import sqlite3
from peewee import *
import scrapy

from myfiction.settings import FICTION_URL, CHAPTER_URL

db = SqliteDatabase('fictions.db')


# get the fiction name and url
class FictionURLItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    chapterid = scrapy.Field()
    content = scrapy.Field()


class Fictions(Model):
    id = PrimaryKeyField()
    fictionid= CharField(verbose_name="fictionid", max_length=100, null=False)
    chapterid = CharField(verbose_name="chapterid", max_length=100, null=False)
    name = CharField(verbose_name="name", max_length=200, null=False)
    content = TextField(verbose_name="content")

    class Meta:
        database = db