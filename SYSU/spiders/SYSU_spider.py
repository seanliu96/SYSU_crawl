#coding:utf-8

import scrapy
import logging
import re
import os
import bs4
from bs4 import BeautifulSoup
import urllib.parse
import chardet

logger = logging.getLogger('SYSU spider')

class SYSUSpider(scrapy.Spider):
    name = 'SYSU'
    allowed_domains = ["sysu.edu.cn"]
    website_possible_httpstatus_list = [301, 302, 404]
    start_urls = [
        "http://www.sysu.edu.cn/2012/cn/index.htm"
    ]
    
    def parse(self, response):
        if response.body == 'banned':
            request = response.request
            request.meta['change_proxy'] = True
            yield request
        else:
            if response.url.find('error') != -1:
                pass
            else:
                logging.info('got page: %s' % response.url)
                content_type = response.headers.get("Content-Type")
                print(content_type)
                if content_type.find(b'text/html') != -1:
                    from_encoding=chardet.detect(response.body)['encoding']
                    soup = BeautifulSoup(response.body, 'lxml', from_encoding=from_encoding)
                    m = re.match(r'http[s]*://(.*?).sysu.edu.cn', response.url)
                    if m:
                        if not os.path.exists(os.path.join('data', m.group(1))):
                            os.mkdir(os.path.join('data', m.group(1)))
                        with open(os.path.join('data', m.group(1), soup.title.text) + '.html', 'wb') as f:
                            f.write(response.body)
                    for link in soup.find_all('a'):
                        url = link.get('href')
                        if url:
                            url = link['href']
                            if not link.get('type'):
                                url = urllib.parse.urljoin(response.url, url)
                                print("url: " + url)
                                yield scrapy.Request(url)
