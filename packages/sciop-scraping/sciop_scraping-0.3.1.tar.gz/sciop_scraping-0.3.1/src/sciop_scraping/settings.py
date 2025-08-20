import multiprocessing

BOT_NAME = "sciop_scrape"

SPIDER_MODULES = ["sciop_scraping.spiders"]
NEWSPIDER_MODULE = "rescue.spiders"

CONCURRENT_REQUESTS = multiprocessing.cpu_count() * 2

RETRY_ENABLED = True

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
