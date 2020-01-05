# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from fictions.items import Fictions, Chapters, Contents
from fictions.items import FictionItem, ChapterItem, ContentItem


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
        Contents.create(fiction_id=item['fiction_id'], chapter_id=item['chapter_id'], url=item['url'], name=item['name'], content=item['content'])
    except Exception as e:
        print(e.args[0], e.args[1])

    return item

class MyfictionPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, FictionItem):
            save_fiction(item)
        elif isinstance(item, ContentItem):
            save_content(item)


