import unittest
from datetime import datetime

import pymysql
from DBUtils.PooledDB import PooledDB
from peewee import *

from fictions.items import FictionItem, ChapterItem, ContentItem
from fictions.models import FictionModel, ChapterModel, ContentModel
from fictions.pipelines import SQLStorePipeline, ModelStorePipeline
from fictions.settings import FICTION_URL
from fictions.spiders.fiction import FictionSpider


def create_fiction_item(i):
    item = FictionItem()
    item['fiction_id'] = i
    item['name'] = 'fiction' + str(i)
    item['url'] = 'fiction' + str(i)
    item['save'] = 1
    item['updated'] = datetime.now()
    return item


def create_chapter_item(i):
    item = ChapterItem()
    item['fiction_id'] = i
    item['name'] = 'chapter' + str(i)
    item['url'] = 'chapter' + str(i)
    item['chapter_id'] = i
    item['updated'] = datetime.now()
    return item


def create_content_item(i):
    item = ContentItem()
    item['fiction_id'] = i
    item['content'] = 'content' + str(i)
    # item['name'] = 'test' + str(i)
    # item['url'] = 'test' + str(i)
    item['chapter_id'] = i
    item['updated'] = datetime.now()
    return item


class Test_Model_Store_Pipeline(unittest.TestCase):
    def setUp(self):
        self.original_db = FictionModel._meta.database
        self.sqlite_db = SqliteDatabase('my_app.db')
        self.sqlite_db.bind([FictionModel, ChapterModel, ContentModel])
        self.sqlite_db.create_tables([FictionModel, ChapterModel, ContentModel])
        self.pipeline = ModelStorePipeline()
        self.spider = FictionSpider()

    def tearDown(self):
        self.original_db.bind([FictionModel, ChapterModel, ContentModel])

    def process_item(self):
        for i in range(23):
            self.pipeline.process_item(create_fiction_item(i), self.spider)
            self.pipeline.process_item(create_chapter_item(i), self.spider)
            self.pipeline.process_item(create_content_item(i), self.spider)
        self.assertEqual(20, FictionModel.select().count())
        self.assertEqual(20, ChapterModel.select().count())
        self.assertEqual(20, ContentModel.select().count())

    def test_process_fiction_item(self):
        with self.sqlite_db.bind_ctx([FictionModel, ChapterModel, ContentModel]):
            for i in range(23):
                self.pipeline.process_item(create_fiction_item(i), self.spider)
        self.assertEqual(20, FictionModel.select().count())

    def test_process_chapter_item(self):
        with self.sqlite_db.bind_ctx([FictionModel, ChapterModel, ContentModel]):
            for i in range(23):
                self.pipeline.process_item(create_chapter_item(i), self.spider)
        self.assertEqual(20, ChapterModel.select().count())

    def test_process_content_item(self):
        with self.sqlite_db.bind_ctx([FictionModel, ChapterModel, ContentModel]):
            for i in range(23):
                self.pipeline.process_item(create_content_item(i), self.spider)
        self.assertEqual(20, ContentModel.select().count())


class Test_SQLStorePipeline(unittest.TestCase):
    pipe = None
    pool = None

    def setUp(self):
        self.pool = PooledDB(creator=pymysql, maxcached=10, maxshared=10, host='localhost', user='root',
                             passwd='123456',
                             db='test', port=3306, charset="utf8", setsession=['SET AUTOCOMMIT = 1'])
        self.pipe = SQLStorePipeline(self.pool)

    def tearDown(self):
        self.pool.close()

    def truncateFictions(self):
        cursor = self.pool.connection().cursor()
        cursor.execute("truncate table fictions")

    def countFictions(self):
        cursor = self.pool.connection().cursor()
        cursor.execute("select count(*) from fictions")

    def bulk_insert_fictions(self):
        self.truncateFictions()
        fictions = []
        for i in range(30):
            f = FictionItem()
            f["fiction_id"] = i
            f["name"] = "test" + str(i)
            f["url"] = FICTION_URL.format(i)
            fictions.append(f)
        self.pipe.bulk_insert_fictions(fictions)
