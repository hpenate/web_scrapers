# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 16:24:20 2021

@author: Herberth Peñate
@description: Extracción horizontal con Scrapy
"""
#Importación de Scrapy
from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.loader import ItemLoader

#Clase referente a la estructura de cada elemento a almacenar
class Whisky(Item):
    name = Field()
    price = Field()
    link = Field()
    
class WhiskySpider(Spider):
    name = "SpiderWhisky"
    custom_settings = {
            "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        }
    
    start_urls =['https://www.whiskyshop.com/gifts/whiskies-under-50']
    
    def parse(self, response):
        sel = Selector(response)
        whisky_bottles = sel.xpath('//ol[contains(@class,"product-items")]/li')
        
        for bottle in whisky_bottles:
            item = ItemLoader(Whisky(), bottle)
            item.add_xpath('name', './/a[@class="product-item-link"]/text()')
            item.add_xpath('price', './/span[@class="price"]/text()')
            item.add_xpath('link', './/a[@class="product-item-link"]/@href')
            
            yield item.load_item()
        
        next_page = sel.xpath('//ul[@class="items pages-items"]/li[@class="item pages-item-next"]/a/@href').get()
        print('Link de la siguiente página ' + str(next_page))
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)