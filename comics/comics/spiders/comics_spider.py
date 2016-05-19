# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from scrapy.selector import Selector
from comics.items import ComicsItem


class ComicsSpider(Spider):
    name = 'comics'
    allowed_urls = ['comicbookroundup.com']

    f = open("urls.txt")
    start_urls = [url.strip() for url in f.readlines()]
    f.close()

    # start_urls = ['http://comicbookroundup.com/comic-books/reviews/vertigo']


    def parse(self, response):
        rows = response.xpath('//*[@id="reviewsbypublisher"]/table[2]/tr').extract()
        for row in rows:
            series_url = Selector(text=row).xpath('//td[2]/a/@href').extract()
            yield Request('http://comicbookroundup.com'+series_url[0], callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        item = ComicsItem()
        item['series'] = response.xpath('//*[@id="series"]/div/div[2]/div/h1/span/text()').extract()
        item['publisher'] = response.xpath('//*[@id="series"]/div/div[2]/div/div[1]/span[1]/a/text()').extract()
        item['release'] = response.xpath('//*[@id="series"]/div/div[2]/div/div[1]/span[2]/text()').extract()
        item['issues_count'] = response.xpath('//*[@id="series"]/div/div[2]/div/div[1]/span[3]/text()').extract()
        item['avg_rating_critic'] = response.xpath('//*[@id="series"]/div/div[2]/div/div[2]/div[1]/span/span/text()').extract()
        item['avg_rating_user'] = response.xpath('//*[@id="series"]/div/div[2]/div/div[2]/div[2]/text()').extract()

        rows = response.xpath('//*[@id="issues"]/div[1]/table[2]/tr').extract()
        item['issues_list'] = {}

        for row in rows:
            rating_critic = Selector(text=row).xpath('//td[1]/div[1]/div/text()').extract()
            rating_user = Selector(text=row).xpath('//td[1]/div[2]/div/text()').extract()
            issue = Selector(text=row).xpath('//td[2]/a/text()').extract()
            issue = str(issue).replace('.', '-')
            writer = Selector(text=row).xpath('//td[3]/a/text()').extract()
            artist = Selector(text=row).xpath('//td[4]/a/text()').extract()
            reviews_critic_count = Selector(text=row).xpath('//td[5]/div[1]/a/text()').extract()
            reviews_user_count = Selector(text=row).xpath('//td[5]/div[2]/a/text()').extract()

            item['issues_list'][str(issue)] = {'rating_critic': rating_critic,
                                               'rating_user': rating_user,
                                               'writer': writer,
                                               'artist': artist,
                                               'reviews_critic_count': reviews_critic_count,
                                               'reviews_user_count': reviews_user_count}
        yield item