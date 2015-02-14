# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from scrapy.spider import BaseSpider

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
            yield Request(url=href, callback=self.parse_section)

    def parse_section(self, response):
        self.log("Parsing section url: %s" % response.url)
        featured_deals = response.xpath("//div[contains(@class,'featuredDeal')]")
        for featured_deal in featured_deals:
            featured_deal_href = featured_deal.xpath(".//h2/a/@href").extract()[0]
            featured_deal_id = re.search('-(\d+)/$', featured_deal_href).group(1)
            yield Request(url=featured_deal_href, callback=self.parse_item, meta={'url': featured_deal_href, 'id': featured_deal_id})
        premium_placements = response.xpath("//div[contains(@class,'premiumPlacement')]")
        for premium_placement in premium_placements:
            premium_placement_href = premium_placement.xpath(".//h2/a/@href").extract()[0]
            premium_placement_id = re.search('-(\d+)/$', premium_placement_href).group(1)
            yield Request(url=premium_placement_href, callback=self.parse_item, meta={'url': premium_placement_href, 'id': premium_placement_id})

    def parse_item(self, response):
        self.log("Parsing item url: %s" % response.url)
        if len(response.css('.page.noBorder')):
            return self.parse_item_no_border(response)
        elif len(response.css('.page.withBorder')):
            return self.parse_item_with_border(response)
        else:
            self.log("Parsing unknown page type, this may not give many details...")
            i = TravelZooItem()
            i['id'] = response.meta['id']
            i['url'] = response.meta['url']
            i['name'] = response.css('h1::text').extract()
            i['description'] = response.css('.dealText p:first-child').xpath('node()').extract()
            i['whats_included'] = response.css('.dealText ul').extract()
            return i

    def parse_item_with_border(self, response):
        self.log("Parsing page with border")
        i = TravelZooItem()
        i['id'] = response.meta['id']
        i['url'] = response.meta['url']
        page = response.css('.innerDealPage')
        i['name'] = page.css('h1::text').extract()
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
        return i

    def parse_item_no_border(self, response):
        self.log("Parsing page no border")
        i = TravelZooItem()
        i['id'] = response.meta['id']
        i['url'] = response.meta['url']
        page = response.css('.page.noBorder')
        i['name'] = page.css('h1').xpath('text()').extract()
        i['why_we_love_it'] = page.xpath(".//div[contains(@id,'spanWhyLove')]/ul").extract()
        i['whats_included'] = page.xpath(".//div[contains(@id,'DivWhatsIncluded')]/div").xpath('node()').extract()
        return i
