# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from travelzoo.items import TravelZooItem


class TravelZooComSpider(CrawlSpider):
    name = "travelzoo.com"
    allowed_domains = ["www.travelzoo.com"]
    start_urls = ["http://www.travelzoo.com/uk/uk-hotels-breaks/"]

    rules = []
    for category in ('london'): #, 'other-cities','southeast', 'southwest', 'midlands', 'wales'):
        rules.append(Rule(LinkExtractor(allow=r'/uk/uk-hotels-breaks/%s/' % category)))
        rules.append(Rule(LinkExtractor(allow=r'/uk/uk-hotels-breaks/%s/[\w-]+/' % category), callback='parse_item', follow=True))

    def parse_item(self, response):
        i = TravelZooItem()
        inner_deal_page = response.css('.innerDealPage')
        i['name'] = inner_deal_page.css('h1').xpath('text()').extract()
        i['url'] = response.url
        i['description'] = inner_deal_page.css('.dealDetailsSection').css('.introDescription').xpath('node()').extract()
        i['why_we_love_it'] = inner_deal_page.xpath(".//div[contains(@class,'dealDetailsSection') and h2[text()='Why we love it']]/ul").extract()

        div_where = inner_deal_page.xpath(".//div[contains(@class,'dealDetailsSection') and h2[text()='Where']]")
        i['contact_name'] = div_where.xpath("div[contains(@id,'MerchantName')]/text()").extract()
        i['contact_address'] = div_where.xpath("div[contains(@id,'MerchantAddress')]/text()").extract()
        i['contact_map'] = div_where.xpath("div[contains(@id,'LinkMap')]/text()").extract()
        i['contact_phone'] = div_where.xpath("div[contains(@id,'MerchantPhone')]/text()").extract()
        i['contact_website'] = div_where.xpath("div[contains(@id,'MerchantWebsite')]/text()").extract()

        i['whats_included'] = inner_deal_page.xpath(".//div[contains(@class,'dealDetailsSection') and h2[contains(text(), 'included')]]/ul").extract()
        i['small_print'] = inner_deal_page.xpath(".//div[contains(@class,'dealDetailsSection') and h2[text()='The small print']]/p").xpath('node()').extract()

        deal_page_right = response.css('#dealPageRightPart')
        i['price'] = deal_page_right.css('.buyNowBox .bigPrice').xpath('text()').extract()
        i['value'] = deal_page_right.css('.buyNowBox .value').xpath('text()').extract()
        i['discount'] = deal_page_right.css('.buyNowBox .discount').xpath('text()').extract()
        i['bought'] = deal_page_right.css('.buyNowBox .discountBox').xpath("span[contains(@id,'Bought')]/text()").extract()
        return i