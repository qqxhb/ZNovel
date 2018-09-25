#!/usr/bin/env python
#!-*-coding:utf-8 -*-
#!@Time :2018/6/13/013 17:47
#!@Author :zhiyuansun
#!@File :.py

import scrapy
import datetime
class QidianNovelSpider(scrapy.Spider):
    #爬虫名
    name='qidian_novel'
    #允许爬的域名
    allowed_domains=['www.qidian.com','book.qidian.com']
    #开始的起点url
    start_urls=['https://www.qidian.com/all',]

    #解析网站入口，提取所有页的url信息
    def parse(self,res):
        #得到all页面中最大页码的数量
        ul_max_page = res.xpath('//ul[contains(@class,"lbf-pagination-item-list")]/li')[-2]
        max_page=int(ul_max_page.xpath('.//a/@data-page').extract_first())
        novel_urls=['https://www.qidian.com/all?orderId=&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page={i}'.format(i=i) for i in range(1,max_page)]
        #为了防止被Ban不能访问相关的网址，这里要做一个一些反爬的操作，最简单的是做一个用户池
        for url_page in novel_urls:
            print(url_page+'\n')
            yield scrapy.Request(url=url_page,callback=self.parse_page)

    #提取每页中所有的小说项的url
    def parse_page(self,res):
        #得到所有的li的数量，每一个li是一本小说
        lis = res.xpath('//ul[contains(@class,"all-img-list cf")]/li')

        for item in lis:
            novel_detail='https:'+item.xpath('.//h4/a/@href')[0].extract().strip()
            print(novel_detail)
             #将每一个li的url放入novel_details中
            yield  scrapy.Request(url=novel_detail,callback=self.parse_novel_item)


    #解析每本小说的详细的信息，并且封装成novel_item
    def parse_novel_item(self, res):
        novel_about = res.xpath('//div[contains(@class,"book-information cf")]')
        novel_img_url = 'https:'+novel_about.xpath('.//div[contains(@class,"book-img")]/a[@id="bookImg"]/img/@src').extract_first().strip()
        novel_info = novel_about.xpath('.//div[contains(@class,"book-info")]')
        novel_name = novel_info.xpath('.//h1/em/text()').extract_first()
        novel_author = novel_info.xpath('.//h1/span/a/text()').extract_first()
        novel_tags=''
        novel_tag_1 = novel_info.xpath('.//p[contains(@class,"tag")]/span/text()')
        novel_tag_2 = novel_info.xpath('.//p[contains(@class,"tag")]/a/text()')
        novel_tags=' '.join(novel_tag_1.extract()+novel_tag_2.extract())
        novel_intro=novel_info.xpath('.//p[contains(@class,"intro")]/text()').extract_first()
        #args=(novel_name,novel_author,novel_intro,novel_tags)
        novel_chapters=res._url

        data = {
            'title': novel_name.strip(),
            'url': novel_chapters,
            'image': novel_img_url,
            'author': novel_author.strip(),
            'profile': novel_intro.strip().replace('\u3000', '').replace('\n', ''),
            'style': novel_tags,
            'time': datetime.datetime.now()
        }
        yield data
