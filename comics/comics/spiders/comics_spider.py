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

    # Generic function to get details from xpath in response
    def getdetail(self, response, path, function, index, alt):
        try:
            return function(response.xpath(path).extract()[index])
        except Exception:
            return alt

    # Main parse function
    def parse(self, response):
        rows = response.xpath('//*[@id="all-series"]/div/table[2]/tr').extract()
        for row in rows:
            series_url = Selector(text=row).xpath('//td[2]/a/@href').extract()
            yield Request('http://comicbookroundup.com'+series_url[0], callback=self.parse_series_contents)

    # Function to parse contents of a given series page
    def parse_series_contents(self, response):
        item = ComicsItem()

        # Scrape data from the top of the series page
        item['series'] = self.getdetail(response, '//span[@itemprop="itemreviewed"]/text()', str, 0, None)
        item['publisher'] = self.getdetail(response, '//div[@itemprop="description"]/span[1]/a/text()', str, 0, None)

        item['release'] = self.getdetail(response, '//div[@itemprop="description"]/span[2]/text()', str, 0, None).strip()
        if item['release'] == '':
            item['release'] = None

        item['issues_count'] = self.getdetail(response, '//div[@itemprop="description"]/span[3]/text()', int, 0, 0)
        item['series_reviews_critic'] = self.getdetail(response, '//span[@itemprop="votes"]/text()', int, 0, 0)
        item['series_reviews_user'] = self.getdetail(response, '//span[@itemprop="votes"]/../text()', int, -1, 0)
        item['avg_rating_critic'] = self.getdetail(response, '//span[@itemprop="average"]/text()', float, 0, None)
        item['avg_rating_user'] = self.getdetail(response, '//span[@class="rating-title"]/../text()', float, 1, None)

        # Scrape data from table of issues in the series page
        rows = response.xpath('//*[@id="issues"]/div[1]/table[2]/tr').extract()
        item['issues_list'] = {}
        for row in rows:
            rating_critic = self.getdetail(Selector(text=row), '//div[@class="CriticRatingList"]/div/text()', float, 0, None)
            rating_user = self.getdetail(Selector(text=row), '//div[@class="UserRatingList"]/div/text()', float, 0, None)

            issue = Selector(text=row).xpath('//td[@class="issues"]/a/text()').extract()
            issue = str(issue).replace('.', '-').replace('#','')

            writer = self.getdetail(Selector(text=row), '//td[@class="writer"]/a/text()', str, 0, None)
            artist = self.getdetail(Selector(text=row), '//td[@class="artist"]/a/text()', str, 0, None)
            reviews_critic_count = self.getdetail(Selector(text=row), '//div[@class="CriticReviewNumList"]/a/text()', int, 0, 0)
            reviews_user_count = self.getdetail(Selector(text=row), '//div[@class="UserReviewNumList"]/a/text()', int, 0, 0)

            item['issues_list'][str(issue)] = {'rating_critic': rating_critic,
                                               'rating_user': rating_user,
                                               'writer': writer,
                                               'artist': artist,
                                               'reviews_critic_count': reviews_critic_count,
                                               'reviews_user_count': reviews_user_count}
        yield item