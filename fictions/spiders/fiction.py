# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse

from fictions.items import FictionItem, ContentItem
from fictions.settings import FICTION_PRIORITY, CHAPTER_PRIORITY, CONTENT_PRIORITY
from fictions.settings import SITE_RANGE, FICTION_URL, SITE_URL, SITE_DOMAIN
from fictions.pipelines import pool


class FictionSpider(scrapy.Spider):
    name = 'fiction'
    allowed_domains = [SITE_DOMAIN]
    conn = None
    cursor = None

    def __init__(self):
        self.conn = pool.connection()
        self.cursor = self.conn.cursor()

    # According to the settings param, yield the top list fictions' urls
    def start_requests(self):
        for i in range(SITE_RANGE):
            yield scrapy.Request(url=SITE_URL.format(i + 1), callback=self.parse)

    def getContentItem(self, response):
        if response is None or not isinstance(response, HtmlResponse):
            return
        content = ContentItem()
        url = response.url
        content["fiction_id"] = url.split("/")[-2]
        content['chapter_id'] = url.split("/")[-1].split(".")[-2]
        content["ifiction_id"] = int(content["fiction_id"])
        content['dchapter_id'] = float(content['chapter_id'].replace('_', '.'))
        title = response.xpath("//title/text()").get().strip()
        content["name"] = title.split("_")[1]
        content["url"] = url
        # item['content'] = item.content.decode("gbk")
        # item['content'] = item.content.encode("utf8")
        content['content'] = response.xpath("//div[@id='nr1']").get().strip()
        return content

    def parseContentURL(self, response):
        self.log("Response Encoding: %s" % response.encoding)
        content = self.getContentItem(response)
        if content['content'] is not None and content['content'] != "":
            yield content

        next_page = response.xpath("//td[@class='next']/a/@href").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parseContentURL, priority=CONTENT_PRIORITY)

    def is_content_saved(self, fiction_id, chapter_id):
        #sql = """SELECT * from contents where ifiction_id=%d and dchapter_id=%f"""
        sql = """SELECT * from contents where ifiction_id={0:d} and dchapter_id={1:f}"""
        sql = sql.format(fiction_id, chapter_id)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return rows is not None and len(rows) > 0

    def parseChapterUrl(self, response):
        print("Parsing Chapter Url:" + response.url)
        for c in response.xpath("//ul[@class='chapter']/li"):
            # get chapter content
            url = c.xpath("a/@href").get()
            fiction_id = url.split("/")[-2]
            chapter_id = url.split("/")[-1].split(".")[-2]
            if self.is_content_saved(int(fiction_id), float(chapter_id.replace('_', '.'))):
                continue
            else:
                if url is not None:
                    yield response.follow(url, callback=self.parseContentURL, priority=CONTENT_PRIORITY)
        # get next page url
        pages = response.xpath("//div[@class='page']/a/@href")
        for page in pages:
            next_page = page.get()
            if next_page is not None:
                yield response.follow(next_page, callback=self.parseChapterUrl, priority=CHAPTER_PRIORITY)

    def is_fiction_saved(self, fiction_id):
        sql = """SELECT * from fictions where ifiction_id={0:d}"""
        sql = sql.format(fiction_id)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return rows is not None and len(rows) > 0

    # According to the settings param, get fiction url and parse the chapters' urls
    def parse(self, response):
        for f in response.xpath("//p[@class='line']"):
            url = f.xpath("a/@href").get()
            fiction_id = url.split("/")[-2]
            # Don't save the saved fiction
            if self.is_fiction_saved(int(fiction_id)):
                continue
            else:
                fiction = FictionItem()
                fiction["fiction_id"] = fiction_id
                fiction["ifiction_id"] = int(fiction["fiction_id"])
                fiction["name"] = f.xpath("a/text()").get()
                url = FICTION_URL.format(fiction_id)
                fiction["url"] = url
                yield fiction
            # Get the chapter information whether the fiction is saved
            if url is not None and url.strip() != "":
                yield scrapy.Request(url, callback=self.parseChapterUrl, priority=FICTION_PRIORITY)
