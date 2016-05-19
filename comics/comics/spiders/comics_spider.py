# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.selector import Selector
from comics.items import ComicsItem


class ComicsSpider(Spider):
    name = 'comics'
    allowed_urls = ['comicbookroundup.com']

    f = open("urls.txt")
    start_urls = [url.strip() for url in f.readlines()]
    f.close()

    def parse(self, response):
        rows = response.xpath('//*[@id="reviewsbypublisher"]/table[2]/tr').extract()
        publisher = response.url
        publisher = publisher[publisher.rfind('/') + 1:]

        for row in rows:
            rating_critic = Selector(text=row).xpath('//td[1]/div[1]/div/text()').extract()
            rating_user = Selector(text=row).xpath('//td[1]/div[2]/div/text()').extract()
            series = Selector(text=row).xpath('//td[2]/a/text()').extract()
            series_url = Selector(text=row).xpath('//td[2]/a/@href').extract()
            issues = Selector(text=row).xpath('//td[3]/text()').extract()
            pulls = Selector(text=row).xpath('//td[4]/text()').extract()

            item = ComicsItem()
            item['publisher'] = publisher
            item['rating_critic'] = rating_critic
            item['rating_user'] = rating_user
            item['series'] = series
            item['series_url'] = series_url
            item['issues'] = issues

            yield item
