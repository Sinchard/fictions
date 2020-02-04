from peewee import *
from playhouse.pool import PooledMySQLDatabase
from playhouse.db_url import connect

# database = PooledMySQLDatabase('test',
#                                max_connections=32,
#                                stale_timeout=300,
#                                **{
#                                    'charset': 'utf8',
#                                    'sql_mode': 'PIPES_AS_CONCAT',
#                                    'use_unicode': True,
#                                    'user': 'root',
#                                    'password': '123456'
#                                })
database = connect(
    "mysql+pool://root:123456@localhost:3306/test?max_connections=32&stale_timeout=300",
    **{
        'charset': 'utf8',
        'sql_mode': 'PIPES_AS_CONCAT',
        'use_unicode': True,
    })


class BaseModel(Model):
    id = AutoField()

    class Meta:
        database = database


class FictionModel(BaseModel):
    fiction_id = IntegerField(index=True)
    name = CharField()
    save = IntegerField()
    updated = DateTimeField()
    url = CharField()

    class Meta:
        table_name = 'reader_fiction'


class ChapterModel(BaseModel):
    chapter_id = DecimalField(index=True)
    fiction_id = IntegerField(index=True)
    name = CharField()
    updated = DateTimeField()
    url = CharField()

    class Meta:
        table_name = 'reader_chapter'


class ContentModel(BaseModel):
    chapter_id = DecimalField(index=True)
    content = TextField()
    fiction_id = IntegerField(index=True)
    updated = DateTimeField()

    class Meta:
        table_name = 'reader_content'
