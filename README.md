spider_python
=============

抓取北邮人论坛/水木社区/cc98论坛的校招信息的爬虫程序。
感谢lizherui等大神的启发。


爬虫默认每隔1小时抓取1次，每抓取10次清空所有数据。
每次更新的是相应版面首页出现关键词的信息。

Unix/Windows下均需要先在本机安装[redis](http://redis.io)服务程序，然后在Unix下运行redis-server，在Windows下启动redis-server.exe。

安装示例：Mac OS X下安装redis

    brew install redis

此外，程序依赖以下Python第三方包：

* [APScheduler](http://pythonhosted.org/APScheduler)

* [BeautifulSoup 3.2.1](http://www.crummy.com/software/BeautifulSoup/bs3/documentation.zh.html)

* [redis-py](https://github.com/andymccurdy/redis-py)

* [requests](https://github.com/kennethreitz/requests)

安装示例：Mac OS X/Linux下安装Python第三方包
    
    pip install apscheduler
    pip install BeautifulSoup
    pip install redis
    pip install requests
    
然后直接运行main.py程序，访问<http://127.0.0.1:8888>
    
效果如下：

![1](https://lh4.googleusercontent.com/-DdobnB7RIf8/UhTs2OdrPNI/AAAAAAAAAM4/df2OmS0bhV0/w958-h599-no/%25E5%25B1%258F%25E5%25B9%2595%25E5%25BF%25AB%25E7%2585%25A7+2013-08-22+%25E4%25B8%258A%25E5%258D%258812.36.50.png)

Enjoy it。

