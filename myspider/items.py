# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # 日期
    date = scrapy.Field()
    # 日期链接
    link = scrapy.Field()
    # 天气状况
    situation = scrapy.Field()
    # 气温
    temperature = scrapy.Field()
    # 风力风向
    wind = scrapy.Field()

