# -*- coding: utf-8 -*-
from scrapy import Item, Field

class ComicsItem(Item):
    publisher = Field()
    rating_critic = Field()
    rating_user = Field()
    series = Field()
    series_url = Field()
    issues = Field()

