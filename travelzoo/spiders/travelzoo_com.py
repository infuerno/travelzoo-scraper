# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.contrib.loader import ItemLoader
from travelzoo.items import TravelZooItem


class TravelZooComSpider(BaseSpider):
    name = 'travelzoo.com'
    allowed_domains = ['www.travelzoo.com']
    start_urls = ['http://www.travelzoo.com/uk/']

    def parse(self, response):
        # select all links in the left hand menu which aren't top level ones (don't have li class attribute) and aren't in the Destinations menu
        hrefs = response.xpath("//div[@id='leftNavigationWrapper']/ul/li[a/text()!='Destinations']//ul/li[not(@class)]/a/@href").extract()
        for href in hrefs:
            self.log("Yielding request for url: %s" % href)
            yield Request(url=href, callback=self.parse_section_items)

    def parse_section(self, response):
        self.log("Parsing section url: %s" % response.url)
        # These functions don't get called - why
        self.parse_section_items(response, 'featuredDeal')
        self.parse_section_items(response, 'premiumPlacement')
        self.parse_section_items(response, 'dealItem')

    def parse_section_items(self, response, class_name_contains):
        self.log("Parsing section item for css class: %s" % class_name_contains)
        items = response.xpath("//div[contains(@class,'%s')]" % class_name_contains)
        self.log("Found %d item(s) in section, getting item urls of items found" % len(items))
        for item in items:
            item_href = item.xpath(".//h2/a/@href").extract()[0]
            self.log("Extracted url: %s" % item_href)
            # TODO check out the redirection setting which may be able to disable this
            if "Interstitial.aspx" in item_href:
                self.log("Filtering redirection url: %s" % item_href)
                return
            self.log("Extracting item id from url using regex")
            re.search('[-/](\d+)[/A-Za-z-]*$', item_href)
            if match is None:
                self.log("ERROR couldn't parse id from url, check regex", level=self.log.ERROR)
                return
            item_id = match.group(1)
            self.log("Item id is %s, yielding url" % item_id)
            yield Request(url=item_href, callback=self.parse_item, meta={'url': item_href, 'id': item_id})

    def parse_item(self, response):
        self.log("Parsing item url: %s" % response.url)
        i = TravelZooItem()
        i['id'] = response.meta['id']
        i['url'] = response.meta['url']
        i['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        i['updated_at'] = i['created_at']
        if len(response.css('.page.noBorder')):
            return self.parse_item_no_border(response, i)
        elif len(response.css('.page.withBorder')):
            return self.parse_item_with_border(response, i)
        else:
            self.log("Parsing unknown page type, this may not give many details...")
            l = ItemLoader(item=i, response=response)
            l.add_css('name', 'h1::text')
            i['description'] = response.css('.dealText p:first-child').xpath('node()').extract()
            i['whats_included'] = response.css('.dealText ul').extract()
            return l.load_item()

    def parse_item_with_border(self, response, i):
        self.log("Parsing page with border")
        page = response.css('.innerDealPage')
        l = ItemLoader(item=i, response=response)
        l.add_css('name', 'h1::text')
        i['description'] = page.css('.dealDetailsSection').css('.introDescription').xpath('node()').extract()
        i['why_we_love_it'] = page.xpath(".//div[contains(@class,'dealDetailsSection') and h2[text()='Why we love it']]/ul").extract()

        div_where = page.xpath(".//div[contains(@class,'dealDetailsSection') and h2[text()='Where']]")
        i['contact_name'] = div_where.xpath("div[contains(@id,'MerchantName')]/text()").extract()
        i['contact_address'] = div_where.xpath("div[contains(@id,'MerchantAddress')]/text()").extract()
        i['contact_map'] = div_where.xpath("div[contains(@id,'LinkMap')]/text()").extract()
        i['contact_phone'] = div_where.xpath("div[contains(@id,'MerchantPhone')]/text()").extract()
        i['contact_website'] = div_where.xpath("div[contains(@id,'MerchantWebsite')]/text()").extract()

        i['whats_included'] = page.xpath(".//div[contains(@class,'dealDetailsSection') and h2[contains(text(), 'included')]]/ul").extract()
        i['small_print'] = page.xpath(".//div[contains(@class,'dealDetailsSection') and h2[text()='The small print']]/p").xpath('node()').extract()

        deal_page_right = response.css('#dealPageRightPart')
        i['price'] = deal_page_right.css('.buyNowBox .bigPrice').xpath('text()').extract()
        i['value'] = deal_page_right.css('.buyNowBox .value').xpath('text()').extract()
        i['discount'] = deal_page_right.css('.buyNowBox .discount').xpath('text()').extract()
        i['bought'] = deal_page_right.css('.buyNowBox .discountBox').xpath("span[contains(@id,'Bought')]/text()").extract()
        return l.load_item()

    def parse_item_no_border(self, response, i):
        self.log("Parsing page no border")
        page = response.css('.page.noBorder')
        l = ItemLoader(item=i, response=response)
        l.add_css('name', 'h1::text')
        i['why_we_love_it'] = page.xpath(".//div[contains(@id,'spanWhyLove')]/ul").extract()
        i['whats_included'] = page.xpath(".//div[contains(@id,'DivWhatsIncluded')]/div").xpath('node()').extract()
        return l.load_item()
