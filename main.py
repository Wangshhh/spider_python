#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: main.py
#         Desc: 运行程序之后，请不要关闭运行窗口，可以在浏览器中通过"http://127.0.0.1:8888"访问爬虫找到的工作链接。
#       Author: lizherui, mmoonzhu, wangjingyao
#        Email: lzrak47m4a1@gmail.com, myzhu@tju.edu.cn
#     HomePage: https://github.com/lizherui/spider_python
#      Version: 0.0.1.1
#          Add: 增加了对cc98内的帖子的抓取
#   LastChange: 2013-08-20 15:27:25
#=============================================================================
'''

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from BeautifulSoup import BeautifulSoup
from apscheduler.scheduler import Scheduler
import re
import redis
import requests
from urllib import urlopen

HOST_NAME = '127.0.0.1'  # Web页面的ip
PORT_NUMBER = 8888  # Web页面的port
REDIS_IP = '127.0.0.1'  # Redis的ip
REDIS_PORT = 6379  # Redis的port
REDIS_FLUSH_FREQUENCE = 2  # Redis清空的频率
SPIDER_KEYS = (u'校招', u'应届', u'毕业生', 'Google', u'北京')  # 筛选的关键词
CRAWLER_FREQUENCE_HOURS = 1  # 每隔一个小时爬取一次


class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        crawler = Crawler()
        page = crawler.generate_page()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(page)
        return 
    

class Crawler:

    def __init__(self):
        self.rs = redis.Redis(host=REDIS_IP, port=REDIS_PORT)
        self.http_querys = (
                                {
                                   'host' : 'http://bbs.byr.cn',
                                    'url'  : 'http://bbs.byr.cn/board/JobInfo',
                                    'headers' : {
                                        "X-Requested-With" : "XMLHttpRequest",
                                    },
                                    'href' : "^/article/JobInfo/\d+$",
                                },

                                {
                                    'host' : 'http://www.newsmth.net',
                                    'url'  : 'http://www.newsmth.net/nForum/board/Career_Campus',
                                    'headers' : {
                                        "X-Requested-With" : "XMLHttpRequest",
                                    },
                                    'href' : "^/nForum/article/Career_Campus/\d+$",
                                },

				{
                                    'host' : 'http://www.cc98.org',
                                    'url'  : 'http://www.cc98.org/list.asp?boardid=235',
                                    'headers' : {
                                        "X-Requested-With" : "XMLHttpRequest",
                                    },
                                   # 'href' : "^dispbbs\.asp\?boardID\=235\&ID\=(\d)*\&page\=",
                                    'href' : "^dispbbs\.asp.+$",
                                },
                        )

    def _parse_html_to_urls(self, host, url, headers, href):
        if 'cc98' in host:
            r = urlopen(url).read()
            frs_soup = BeautifulSoup(r)
            frs_attrs = {
                'href' : re.compile(href),
                'id' : re.compile("^topic")
            }
        else:       
            r = requests.get(url, headers = headers)
            frs_soup = BeautifulSoup(r.text)
            frs_attrs = {
                'href' : re.compile(href),
                'title' : None,
                'target' : None,
            }
        frs_res = frs_soup.findAll('a', frs_attrs)
        urls = []
        for res in frs_res:
            if res.parent.parent.get('class') != 'top':
                if 'cc98' in host:
                    res['href'] = host + '/' + res['href']
                else:                
                    res['href'] = host + res['href']
                urls.append(res)
        return urls

    def _put_urls_into_redis(self, urls):
        for url in urls:
            if 'cc98' in url['href']:
                r = urlopen(url['href']).read()
                frs_soup = BeautifulSoup(r)
                title = frs_soup.title.string
            else:
                title = url.string

            if filter(lambda x: x in title, SPIDER_KEYS):
                self.rs.sadd('urls', url)

    def _flush_redis_if_needed(self):
        if int(self.rs.get('times')) >= REDIS_FLUSH_FREQUENCE:
            self.rs.flushall()

    def _get_urls_from_redis(self):
        ret = self.rs.smembers('urls')
        urls = "" 
        for herf in ret:
            urls += "<tr><td>" + herf + "</td></tr>"
        return urls
    
    def generate_page(self):
        return '''
                <html>
                    <head>
                        <meta charset="utf-8">
                        <title>Welcome to spider!</title>
                        <link href="//cdnjs.bootcss.com/ajax/libs/twitter-bootstrap/2.3.1/css/bootstrap.min.css" rel="stylesheet">
                        <style>
                            body {
                                width: 35em;
                                margin: 0 auto;
                            }
                            .table-hover tbody tr:hover > td,
                                .table-hover tbody tr:hover > th {
                                background-color: #D2DAFF;
                            }
                            a:visited { color: red; }
                        </style>
                    </head>
                    <body>
                        <h3>招聘信息筛选</h3>
                        <h4 class="text-info">红色链接为您已打开过的链接</h4><hr>
                        <div class="well well-large">
                            <table class="table table-hover">
                                <tbody>
                                    %s
                                </tbody>
                            </table>
                    </body>
                    </html>
                ''' % self._get_urls_from_redis()
    
    def run(self):
        print "start crawler ..."
        self.rs.incr('times')
        self._flush_redis_if_needed()
        for http_query in self.http_querys :
            urls = self._parse_html_to_urls(http_query['host'], http_query['url'], http_query['headers'], http_query['href'])
            self._put_urls_into_redis(urls)
        print "finish crawler ..."


if __name__ == '__main__':

    crawler = Crawler()
    crawler.run()

    sched = Scheduler()
    sched.start()
    sched.add_interval_job(crawler.run, hours=CRAWLER_FREQUENCE_HOURS)
    

    try:
        print "start server ..."
        server = HTTPServer((HOST_NAME, PORT_NUMBER), HttpHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print "finish server ..."
        server.socket.close()
