# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 16:51:20 2021

@author: Herberth Peñate
@description: Extracción de información de manera horizontal y vertical
"""

from scrapy.spiders import Spider
from scrapy.item import Item
from scrapy.item import Field
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
import scrapy
import json

class Whisky(Item):
    name = Field()
    alcohol = Field()
    price = Field()
    description = Field()
    details = Field()
    
class WhiskySpider(Spider):
    name = 'SpiderWhisky'
    allowed_domain = ['whiskyshop.com']
    start_urls = ['https://www.whiskyshop.com/gifts/whiskies-under-50']
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    }
    download_delay = 5
    
    def cleanText(self, texto):
        cleanText = texto.replace('\n', '').replace('\r', '').replace('\t', '').strip()
        
        return cleanText
    
    def parse(self, response):
        page = 1
        sel = Selector(response)
        all_bottles = sel.xpath('//ol[contains(@class,"product-items")]/li')
        
        print("Número de botellas a analizar: " + str(len(all_bottles)))
        for i, bottle in enumerate(all_bottles):
            bottle_url_descr = bottle.xpath('.//div[@class="product-item-info"]/a/@href').extract_first()
            
            print("Botella analizada # "+ str(i) + " en la página " + str(page))
            yield scrapy.Request(bottle_url_descr, callback=self.parse_bottle)
        
        next_page = sel.xpath('//ul[@class="items pages-items"]/li[@class="item pages-item-next"]/a/@href').get()
        print('Link de la siguiente página ' + str(next_page))
        if next_page is not None:
            page += 1
            yield response.follow(next_page, callback=self.parse)
            
    def parse_bottle(self, response):
        item = Selector(response)
        bottle = ItemLoader(Whisky(), item)
        bottle.add_xpath('name', '//div[@class="page-title-wrapper product"]/h1[@class="page-title"]/text()', MapCompose(self.cleanText))
        bottle.add_xpath('alcohol', '//div[@class="product-actions-wrap"]/p[@class="product-info-size-abv"]/span/text()', MapCompose(self.cleanText))
        bottle.add_xpath('price', '//div[@class="product-info-price"]//span[@class="price"]/text()', MapCompose(self.cleanText))
        bottle.add_xpath('description', '//div[@id="product-description-wrap"]//div[@class="section-content"]/p/text()', MapCompose(self.cleanText))
        details_n = item.xpath('//div[@class="product-specifications-wrap"]//div[@class="section-content"]/dl/dt')
        details_des = item.xpath('//div[@class="product-specifications-wrap"]//div[@class="section-content"]/dl/dd')
        order_details = {}
        
        for i in range(len(details_n)):
            name = details_n[i].xpath('./text()').extract_first()
            info = details_des[i].xpath('./text()').extract_first()
            if info is None:
                info = details_des[i].xpath('./a/text()').extract_first()
                
            print("Name: "+str(name))
            print("Info: "+str(info))
            order_details[name] = info
            
        print(json.dumps(order_details))
        print(type(order_details))
        bottle.add_value('details', json.dumps(order_details), MapCompose(self.cleanText))
        
        print()
        
        yield bottle.load_item()