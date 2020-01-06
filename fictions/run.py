from scrapy import cmdline

cmdline.execute("scrapy crawl fiction -s JOBDIR=job_info".split())
