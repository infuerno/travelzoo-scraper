# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from travelzoo.items import TravelZooItem


class TravelZooComSpider(CrawlSpider):
    name = 'travelzoo.com'
    allowed_domains = ['www.travelzoo.com']
    start_urls = ['http://www.travelzoo.com/uk/']
    rules = (
        # links to all sub section index pages from the left hand menu
        Rule(LinkExtractor(restrict_xpaths=("//div[@id='leftNavigationWrapper']/ul/li//ul/li[@class]"))),
        # link to the main deal on a sub section index page
        Rule(LinkExtractor(restrict_xpaths=("//div[contains(@class,'featuredDeal')]//h2")), callback='parse_item', follow=True),
        # link to the premium placement deals below the main deal on a sub section index page
        Rule(LinkExtractor(restrict_xpaths=("//div[contains(@class,'premiumPlacement')]//h2")), callback='parse_item', follow=True)
    )

    def parse_item(self, response):
        self.log("Parsing response")
        if len(response.css('.page.noBorder')):
            return self.parse_item_no_border(response)
        elif len(response.css('.page.withBorder')):
            return self.parse_item_with_border(response)
        else:
            self.log("Parsing unknown page")
            i = TravelZooItem()
            i['name'] = response.css('h1::text').extract()
            i['url'] = response.url
            i['description'] = response.css('.dealText p:first-child').xpath('node()').extract()
            i['whats_included'] = response.css('.dealText ul').extract()
            return i

    def parse_item_with_border(self, response):
        self.log("Parsing page with border")
        i = TravelZooItem()
        page = response.css('.innerDealPage')
        self.log(page)
        i['name'] = page.css('h1::text').extract()
        i['description'] = page.css('.dealDetailsSection').css('.introDescription').xpath('node()').extract()
        i['url'] = response.url
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
        page = response.css('.page.noBorder')
        i['name'] = page.css('h1').xpath('text()').extract()
        i['url'] = response.url
        i['why_we_love_it'] = page.xpath(".//div[contains(@id,'spanWhyLove')]/ul").extract()
        i['whats_included'] = page.xpath(".//div[contains(@id,'DivWhatsIncluded')]/div").xpath('node()').extract()
        return i
