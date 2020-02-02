# -*- coding: utf-8 -*-
import pymysql
from DBUtils.PooledDB import PooledDB
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from fictions.items import FictionItem, ContentItem
from .models import FictionModel, ChapterModel, ContentModel

'''
from fictions.items import Fictions, Contents
def save_fiction(item):
    if not Fictions.table_exists():
        Fictions.create_table()
    try:
        Fictions.create(fiction_id=item['fiction_id'], url=item['url'], name=item['name'])
    except Exception as e:
        print(e.args[0], e.args[1])

    return item


def save_content(item):
    if not Contents.table_exists():
        Contents.create_table()
    try:
        Contents.create(fiction_id=item['fiction_id'], chapter_id=item['chapter_id'], url=item['url'],
                        name=item['name'], content=item['content'])
    except Exception as e:
        print(e.args[0], e.args[1])

    return item


class MyfictionPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, FictionItem):
            save_fiction(item)
        elif isinstance(item, ContentItem):
            save_content(item)

        return item
'''

BUCK_FICTION_LENGTH = 2000
BUCK_CONTENT_LENGTH = 100

mypool = PooledDB(creator=pymysql, maxcached=10, maxshared=10, host='localhost', user='root', passwd='123456',
                  db='fictions', port=3306, charset="utf8", setsession=['SET AUTOCOMMIT = 1'])


class SQLStorePipeline(object):
    fiction_list = []
    content_list = []
    pool = None
    conn = None
    cursor = None

    def __init__(self,pool):
        self.pool=pool

    def open_spider(self, spider):
        pool=mypool

    # 批量插入
    def bulk_insert_fictions(self, fictions):
        self.conn = self.pool.connection()
        self.cursor = self.conn.cursor()
        try:
            print("inserting fictions in batch--->>>>>", len(fictions))
            sql = """INSERT INTO fictions(name, fiction_id, ifiction_id, url) VALUES (%s, %s, %s, %s)"""
            self.cursor.executemany(sql, fictions)
            self.conn.commit()
        except Exception as e:
            print("执行MySQL: % s时出错： % s" % (sql, e))
            self.conn.rollback()

    def bulk_insert_contents(self, contents):
        self.conn = self.mypool.connection()
        self.cursor = self.conn.cursor()
        try:
            print("inserting contents in batch--->>>>>", len(contents))
            sql = """INSERT INTO contents(name, fiction_id, ifiction_id, chapter_id, dchapter_id, url, content) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            self.cursor.executemany(sql, contents)
            self.conn.commit()
        except Exception as e:
            print("执行MySQL: % s时出错： % s" % (sql, e))
            self.conn.rollback()

    def process_item(self, item, spider):
        if isinstance(item, FictionItem):
            self.fiction_list.append((item['name'], item['fiction_id'], item['ifiction_id'], item['url']))
            if len(self.fiction_list) >= BUCK_FICTION_LENGTH:
                self.bulk_insert_fictions(self.fiction_list)
                del self.fiction_list[:]
        elif isinstance(item, ContentItem):
            self.content_list.append(
                (item['name'], item['fiction_id'], item['ifiction_id'], item['chapter_id'], item['dchapter_id'], item['url'], item['content']))
            if len(self.content_list) >= BUCK_CONTENT_LENGTH:
                self.bulk_insert_contents(self.content_list)
                del self.content_list[:]
            item['content'] = None

        return item

    # spider结束
    def close_spider(self, spider):
        print("closing spider,last commit")
        self.bulk_insert_fictions(self.fiction_list)
        self.bulk_insert_contents(self.content_list)
        self.conn.commit()
        self.cursor.close()
        self.conn.close()


class ModelStorePipeline(object):
    fiction_list = []
    chapter_list = []
    content_list = []

    # 批量插入
    def bulk_insert_fictions(self, fictions):
        FictionModel.insert_many(fictions).execute()


    def bulk_insert_chapters(self, chapters):
        ChapterModel.insert_many(chapters).execute()


    def bulk_insert_contents(self, contents):
        ContentModel.insert_many(contents).execute()

    def process_item(self, item, spider):
        if isinstance(item, FictionItem):
            self.fiction_list.append(dict(item))
            if len(self.fiction_list) >= BUCK_FICTION_LENGTH:
                self.bulk_insert_fictions(self.fiction_list)
                del self.fiction_list[:]
        elif isinstance(item, ContentItem):
            self.content_list.append(
                (item['name'], item['fiction_id'], item['ifiction_id'], item['chapter_id'], item['dchapter_id'], item['url'], item['content']))
            if len(self.content_list) >= BUCK_CONTENT_LENGTH:
                self.bulk_insert_contents(self.content_list)
                del self.content_list[:]
            item['content'] = None

        return item

    # spider结束
    def close_spider(self, spider):
        print("closing spider,last commit")
        self.bulk_insert_fictions(self.fiction_list)
        self.bulk_insert_contents(self.content_list)
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
'''
# 数据库pymysql的commit()和execute()在提交数据时，都是同步提交至数据库，由于scrapy框架数据的解析是异步多线程的，所以scrapy的数据解析速度，要远高于数据的写入数据库的速度。如果数据写入过慢，会造成数据库写入的阻塞，影响数据库写入的效率。
# 通过多线程异步的形式对数据进行写入，可以提高数据的写入速度。
from pymysql import cursors
# 使用twsited异步IO框架，实现数据的异步写入。
from twisted.enterprise import adbapi

class MySQLTwistedPipeline(object):
    """
        MYSQL_HOST = 'localhost'
        MYSQL_DB = 'fictions'
        MYSQL_USER = 'root'
        MYSQL_PASSWD = '123456'
        MYSQL_CHARSET = 'utf8'
        MYSQL_PORT = 3306
    """

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        params = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DB'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset=settings['MYSQL_CHARSET'],
            port=settings['MYSQL_PORT'],
            cursorclass=cursors.DictCursor,
        )
        # 初始化数据库连接池(线程池)
        # 参数一：mysql的驱动
        # 参数二：连接mysql的配置信息
        dbpool = adbapi.ConnectionPool('pymysql', **params)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 在该函数内，利用连接池对象，开始操作数据，将数据写入到数据库中。
        # pool.map(self.insert_db, [1,2,3])
        # 同步阻塞的方式： cursor.execute() commit()
        # 异步非阻塞的方式
        # 参数1：在异步任务中要执行的函数insert_db；
        # 参数2：给该函数insert_db传递的参数
        # query = self.dbpool.runInteraction(self.insert_db, item)

        if isinstance(item, FictionItem):
            query = self.dbpool.runInteraction(self.insert_fiction, item)
        elif isinstance(item, ContentItem):
            query = self.dbpool.runInteraction(self.insert_content, item)
        # 如果异步任务执行失败的话，可以通过ErrBack()进行监听, 给insert_db添加一个执行失败的回调事件
        query.addErrback(self.handle_error)
        return item

    def handle_error(self, field):
        print('-----数据库写入失败：', field)

    def insert_fiction(self, cursor, item):
        insert_sql = "INSERT INTO fictions(name, fiction_id, url) VALUES (%s, %s, %s)"
        cursor.execute(insert_sql, (item['name'], item['fiction_id'], item['url']))

    def insert_content(self, cursor, item):
        insert_sql = "INSERT INTO contents(name, fiction_id, chapter_id, url, content) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_sql, (item['name'], item['fiction_id'], item['chapter_id'], item['url'], item['content']))
'''