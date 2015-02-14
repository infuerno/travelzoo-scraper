# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TravelZooItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    why_we_love_it = scrapy.Field()
    contact_name = scrapy.Field()
    contact_address = scrapy.Field()
    contact_map = scrapy.Field()
    contact_phone = scrapy.Field()
    contact_website = scrapy.Field()
    whats_included = scrapy.Field()
    small_print = scrapy.Field()
    price = scrapy.Field()
    value = scrapy.Field()
    discount = scrapy.Field()
    bought = scrapy.Field()
