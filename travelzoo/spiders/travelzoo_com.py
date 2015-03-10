# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from scrapy import log
from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.contrib.loader import ItemLoader
from travelzoo.items import TravelZooDeal


class TravelZooComSpider(BaseSpider):
    """Spider for regularly updated travelzoo.com site, UK version"""
    name = 'travelzoo.com'
    allowed_domains = ['www.travelzoo.com']
    start_urls = ['http://www.travelzoo.com/uk/']

    def parse(self, response):
        # select all links in the left hand menu which aren't top level ones (don't have li class attribute) and aren't in the Destinations menu
        hrefs = response.xpath("//div[@id='leftNavigationWrapper']/ul/li[a/text()!='Destinations']//ul/li[not(@class)]/a/@href").extract()
        for href in hrefs:
            self.log("Yielding request for url: %s" % href)
            yield Request(url=href, callback=self.parse_section)

    def parse_section(self, response):
        items = response.xpath("//div[contains(@class,'featuredDeal') or contains(@class, 'premiumPlacement') or contains(@class, 'dealItem')]")
        for item in items:
            item_href = item.xpath(".//h2/a/@href").extract()[0]
            pattern = '[-/](\d{6,7})[/0-9A-Za-z-]*$'
            match = re.search(pattern, item_href)
            if match is None:
                self.log("ERROR couldn't parse id from url: %s using regex: %s" % (item_href, pattern), level=log.ERROR)
                return
            item_id = match.group(1)
            self.log("Item id: %s, yielding url: %s" % (item_id, item_href))
            yield Request(url=item_href, callback=self.parse_item, meta={'url': item_href, 'id': item_id})

    def parse_item(self, response):
        self.log("Parsing item url: %s" % response.url)
        self.log("Url of the page is actually %s" % response.url)
        i = TravelZooDeal()
        i['id'] = response.meta['id']
        i['url'] = response.meta['url']
        if len(response.css('.page.noBorder')):
            return self.parse_item_no_border(response, i)
        elif len(response.css('.page.withBorder')):
            return self.parse_item_with_border(response, i)
        else:
            self.log("Parsing unknown page type, this may not give many details...")
            loader = ItemLoader(item=i, response=response)
            loader.add_css('name', 'h1::text')
            loader.add_css('description', '.dealText p:first-child')
            loader.add_css('whats_included', '.dealText ul')
            return loader.load_item()

    def parse_item_with_border(self, response, i):
        self.log("Parsing page with border")
        page = response.css('.innerDealPage')
        loader = ItemLoader(item=i, selector=page)
        loader.add_css('name', 'h1::text')
        loader.add_xpath('description', "//div[contains(@class, 'introDescription')]//text()")
        loader.add_xpath('why_we_love_it', ".//div[contains(@class,'dealDetailsSection') and h2[text()='Why we love it']]/ul//text()")

        loader.add_xpath('whats_included', ".//div[contains(@class,'dealDetailsSection') and h2[contains(text(), 'included')]]/ul//text()")
        loader.add_xpath('small_print', ".//div[contains(@class,'dealDetailsSection') and h2[text()='The small print']]/p//text()")

        div_where = page.xpath(".//div[contains(@class,'dealDetailsSection') and h2[text()='Where']]")
        loader.selector = div_where
        loader.add_xpath('contact_name', "div[contains(@id,'MerchantName')]/text()")
        loader.add_xpath('contact_address', "div[contains(@id,'MerchantAddress')]/text()")
        loader.add_xpath('contact_map', "div[contains(@id,'LinkMap')]/text()")
        loader.add_xpath('contact_phone', "div[contains(@id,'MerchantPhone')]/text()")
        loader.add_xpath('contact_website', "div[contains(@id,'MerchantWebsite')]/text()")

        deal_page_right = response.css('#dealPageRightPart')
        loader.selector = deal_page_right
        loader.add_xpath('price', ".//span[@id='ctl00_Main_OurPrice']/text()")
        loader.add_xpath('value', ".//span[@id='ctl00_Main_PriceValue']/text()")
        loader.add_xpath('discount', ".//span[@id='ctl00_Main_Discount']/text()")
        loader.add_xpath('bought', ".//span[contains(@id,'Bought')]/text()")
        return loader.load_item()

    def parse_item_no_border(self, response, i):
        self.log("Parsing page no border")
        page = response.css('.page.noBorder')
        loader = ItemLoader(item=i, selector=page)
        loader.add_css('name', 'h1::text')
        loader.add_xpath("why_we_love_it", ".//div[contains(@id,'spanWhyLove')]/ul")
        loader.add_xpath("whats_included", ".//div[contains(@id,'DivWhatsIncluded')]/div")
        return loader.load_item()
