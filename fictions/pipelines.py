# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from myfiction.items import Fictions


class MyfictionPipeline(object):
    def process_item(self, item, spider):
        if Fictions.table_exists() == False:
            Fictions.create_table()
        try:
            Fictions.create(fictionid=item['id'], chapterid=item['chapterid'], name=item['name'],
                            content=item['content'])
        except Exception as e:
            if str(e.args[0]) == '1062':
                print('�ظ����ݣ�������')
            else:
                print(e.args[0], e.args[1])
        return item
