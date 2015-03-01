# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.contrib.loader.processor import MapCompose, Join, TakeFirst


class TravelZooItem(scrapy.Item):
    """TravelZoo container (dictionary-like object) for scraped data"""
    id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field()
    category = scrapy.Field()
    sub_category = scrapy.Field()
    description = scrapy.Field(output_processor=Join(""))
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
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
