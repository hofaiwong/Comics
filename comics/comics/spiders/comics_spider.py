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
        # rows = response.xpath('//*[@id="reviewsbypublisher"]/table[2]/tr').extract()
        rows = response.xpath('//*[@id="all-series"]/div/table[2]/tr').extract()
        for row in rows:
            series_url = Selector(text=row).xpath('//td[2]/a/@href').extract()
            yield Request('http://comicbookroundup.com'+series_url[0], callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        item = ComicsItem()

        # Scrape data from the top of the series page
        try:
            item['series'] = str(response.xpath('//*[@id="series"]/div/div[2]/div/h1/span/text()').extract()[0])
        except Exception as e:
            item['series'] = None
            print e

        try:
            item['publisher'] = str(response.xpath('//*[@id="series"]/div/div[2]/div/div[1]/span[1]/a/text()').extract()[0])
        except Exception as e:
            item['publisher'] = None
            print e

        try:
            item['release'] = str(response.xpath('//*[@id="series"]/div/div[2]/div/div[1]/span[2]/text()').extract()[0]).strip()
        except Exception as e:
            item['release'] = None
            print e

        try:
            item['issues_count'] = int(response.xpath('//*[@id="series"]/div/div[2]/div/div[1]/span[3]/text()').extract()[0])
        except Exception as e:
            item['issues_count'] = None
            print e

        try:
            item['avg_rating_critic'] = float(response.xpath('//*[@id="series"]/div/div[2]/div/div[2]/div[1]/span/span/text()').extract()[0])
        except Exception as e:
            item['avg_rating_critic'] = None
            print e

        try:
            item['avg_rating_user'] = float(response.xpath('//*[@id="series"]/div/div[2]/div/div[2]/div[2]/text()').extract()[0])
        except Exception as e:
            item['avg_rating_user'] = None
            print e

        # Scrape data from table of issues in the series page
        rows = response.xpath('//*[@id="issues"]/div[1]/table[2]/tr').extract()
        item['issues_list'] = {}
        for row in rows:
            try:
                rating_critic = float(Selector(text=row).xpath('//td[1]/div[1]/div/text()').extract()[0])
            except Exception as e:
                # print 'Error in rating_critic conversion'
                # print Selector(text=row).xpath('//td[1]/div[1]/div/text()').extract()
                # print e
                rating_critic = None

            try:
                rating_user = float(Selector(text=row).xpath('//td[1]/div[2]/div/text()').extract()[0])
            except Exception as e:
                # print 'Error in rating_user conversion'
                # print Selector(text=row).xpath('//td[1]/div[2]/div/text()').extract()
                # print e
                rating_user = None

            issue = Selector(text=row).xpath('//td[2]/a/text()').extract()
            issue = str(issue).replace('.', '-').replace('#','')

            try:
                writer = str(Selector(text=row).xpath('//td[3]/a/text()').extract()[0])
            except Exception as e:
                # print 'Error in writer conversion'
                # print Selector(text=row).xpath('//td[3]/a/text()').extract()
                # print e
                writer = None

            try:
                artist = str(Selector(text=row).xpath('//td[4]/a/text()').extract()[0])
            except Exception as e:
                # print 'Error in artist conversion'
                # print Selector(text=row).xpath('//td[4]/a/text()').extract()
                # print e
                artist = None

            reviews_critic_count = int(Selector(text=row).xpath('//td[5]/div[1]/a/text()').extract()[0])
            reviews_user_count = int(Selector(text=row).xpath('//td[5]/div[2]/a/text()').extract()[0])

            item['issues_list'][str(issue)] = {'rating_critic': rating_critic,
                                               'rating_user': rating_user,
                                               'writer': writer,
                                               'artist': artist,
                                               'reviews_critic_count': reviews_critic_count,
                                               'reviews_user_count': reviews_user_count}
        yield item