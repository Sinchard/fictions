# -*- coding: utf-8 -*-
import scrapy
from peewee import *

from fictions.pipelines import pool

db = MySQLDatabase('fictions', host='127.0.0.1', user='root', passwd='123456')


class MyItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()

    def __init__(self):
        self.conn = pool.connection()
        self.cursor = self.conn.cursor()

    def check(self):
        return self.name is not None and self.url is not None

    def is_saved(self):
        pass


class BaseModel(Model):
    id = AutoField()
    name = CharField(verbose_name="name", max_length=200, null=False)
    url = CharField(verbose_name="url", max_length=200, null=False)

    class Meta:
        database = db


class FictionItem(MyItem):
    fiction_id = scrapy.Field()
    ifiction_id = scrapy.Field()

    def check(self):
        if super.check() and self.fiction_id is not None and self.ifiction_id>0:
            return self.fiction_id in self.url and int(self.fiction_id)==self.fiction_id
        else:
            return False

    def is_saved(self):
        sql = """SELECT * from fictions where ifiction_id={0:d}"""
        sql = sql.format(self.ifiction_id)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return rows is not None and len(rows) > 0



class Fictions(BaseModel):
    fiction_id = CharField(verbose_name="fiction_id", max_length=200, null=False)


# get the fiction name and url
class ContentItem(MyItem):
    fiction_id = scrapy.Field()
    chapter_id = scrapy.Field()
    ifiction_id = scrapy.Field()
    dchapter_id = scrapy.Field()
    content = scrapy.Field()

    def check(self):
        if super.check() and self.fiction_id is not None and self.chapter_id is not None and self.ifiction_id>0 and self.dchapter_id>0:
            return self.fiction_id in self.url and self.chapter_id in self.url and int(self.fiction_id)==self.fiction_id and float(self.chapter_id)==self.dchapter_id
        else:
            return False

    def is_saved(self):
        sql = """SELECT * from contents where ifiction_id={0:d} and dchapter_id={1:f}"""
        sql = sql.format(self.ifiction_id, self.dchapter_id)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return rows is not None and len(rows) > 0


class Contents(BaseModel):
    fiction_id = CharField(verbose_name="fiction_id", max_length=200, null=False)
    chapter_id = CharField(verbose_name="chapter_id", max_length=100, null=False)
    content = TextField(verbose_name="content")
