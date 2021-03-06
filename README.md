# 利用scrapy爬取天气信息



爬取西安近几年的天气信息。选择爬取网站http://www.tianqihoubao.com西安从2016.1.1日至2020.9.30号近五年的天气，包含白天晚上的天气，气温，风向以及风力大小，并存储为csv。

<img src="https://gitee.com/karlhan/picgo/raw/master/img//image-20201007164137298.png" alt="image-20201007164137298" style="zoom:67%;" />

环境：python3.8 ，需要安装Scrapy框架 `pip install Scrapy`版本2.3

运行：首先cd到myspider工程目录，然后终端：`scrapy crawl weather --nolog`

会自动在根目录生成一个weather.csv文件，weather_2.csv是稍改进后的数据。

数据包括日期，日期详情链接，天气（白天），天气（晚上），气温（白天），气温（晚上），风力（白天），风力（晚上）

<img src="https://gitee.com/karlhan/picgo/raw/master/img//image-20201007164204601.png" alt="image-20201007164204601" style="zoom:67%;" />

### Scrapy 工具介绍

Scrapy是一个爬取网站数据，提取结构化特征的应用框架。

Scrapy使用了异步网络框架来处理网络通信，可以加快下载速度，不用自己取实现异步框架。

Scrapy架构图

<img src="https://gitee.com/karlhan/picgo/raw/master/img//image-20201003192742918.png" alt="image-20201003192742918" style="zoom:67%;" />

Scrapy Engine:负责Spider，ItemPipeline,Downloader,Scheduler中间通信，信号数据传递等。

Scheduler(调度器)：负责接受引擎发送的Request请求，并按照一定的方式进行整理排序，入队，当引擎需要时，交还给引擎。

Downloader(下载器)：负责下载Scrapy Engine 所有的Request请求，并将获取的Responses交还给Scrapy Engine,再由引擎交给Spider

Spide(爬虫)：负责从Responses中分析提取数据，获取item字段，并将跟进的url交给引擎，再次进入Scheduler调度器。

Downloader Middlewares（下载中间件）：可以自定义扩展下载功能的组件。

Spider Middlewares(spider中间件)：可以自定义扩展和操作引擎通信的功能组件。

### 工程实现

##### 1.创建工程

首先创建一个scrapy工程，名为myspider

```
scrapy startproject myspider
```

然后创建爬虫,进入项目录，创建一个名为`weather`的爬虫，爬虫限制域为`tianqihaobao.com`,这样在爬取的时候就不会超过这个域名。

```
cd myspider
scrapy genspider weather tianqihoubao.com
```

使用`tree /f myspider`查看生成的目录

<img src="https://gitee.com/karlhan/picgo/raw/master/img//image-20201003162223071.png" alt="image-20201003162223071" style="zoom:50%;" />

##### 2.构建爬虫

首先定位要爬取的信息

<img src="https://gitee.com/karlhan/picgo/raw/master/img//image-20201003160527708.png" alt="image-20201003160527708" style="zoom:67%;" />

每天包含五个要素，首先是日期，日期是超链接，可以点进去查看详情，所以保留了日期的具体url，天气状况，气温，风力风向。

在items.py中创建需要爬取的属性，进行封装。封装的好处是可以减少打错，以及易于阅读理解。

```python
class MyspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # 日期
    date = scrapy.Field()
    # 日期链接
    link = scrapy.Field()
    # 天气状况
    situation = scrapy.Field()
    # 气温
    temperature = scrapy.Field()
    # 风力风向
    wind = scrapy.Field()
```

具体爬虫所在myspider->spiders->weather.py，是刚刚的命令生成的。

```python
import scrapy
from myspider.items import MyspiderItem

class WeatherSpider(scrapy.Spider):
    # 爬虫名称
    name = 'weather'
    # 允许的爬虫范围
    allowed_domains = ['tianqihoubao.com']
    # start_urls = ['http://www.tianqihoubao.com/lishi/xian/month/201510.html']
	
	# 数据提取的方法，接受response
    def parse(self, response):
        # 提取数据
        node_list = response.xpath('//*[@id="content"]/table/tr')
        # print(len(node_list))
        for i,node in enumerate(node_list):
            # if i != 1:
            item = MyspiderItem()
            item["date"] = node.xpath("./td[1]/a/text()").extract_first()
            item["link"] = response.urljoin(node.xpath("./td[1]/a/@href").extract_first())
            item["situation"] = node.xpath("./td[2]/text()").extract_first().strip()
            item["temperature"] = node.xpath("./td[3]/text()").extract_first().strip()
            item["wind"] = node.xpath("./td[4]/text()").extract_first().strip()
            yield item

    def start_requests(self):
        urls = []

        for i in range(2016, 2020):
            for j in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
                urls.append("http://www.tianqihoubao.com/lishi/xian/month/{}{}.html".format(i, j))
        for i in ['01', '02', '03', '04', '05', '06', '07', '08', '09']:
            urls.append("http://www.tianqihoubao.com/lishi/xian/month/2020{}.html".format(i))

        for url in urls:
            yield self.make_requests_from_url(url)
```

首先是查找第一页的元素定位。使用的是XPath，在第一个信息`2016年01月01日`，右键检查，可以看到当前所在的源码的位置，然后查看其父类，删除掉选择第一行的信息，这里使用了Chrome商店的XPath Helper，可以看到result的长度是32，因为第一个月是31天，外加表头所以是32行。将行信息存入到`node_list`中。

![image-20201003162735556](https://gitee.com/karlhan/picgo/raw/master/img//image-20201003162735556.png)

然后遍历`node_list`分别取出每一天的信息，td[1]包含了日期和日期的链接。td[2]包含了天气状况，td[3]包含了气温，td[4]包含了风力风向。

每一行就会实例化一个MyspiderItem()对象，然后将各个属性进行存入。返回是item，这里使用了yield，因为可以在爬取多页的时候多次存入。

如果只爬取一页，那么只需要一个`start_urls`,然后scrapy框架会调用自带的`start_requests()`方法中的`make_requests_from_url()`，以`start_urls`中的所有连接生成对应的Request对象，因为这里需要爬取多个网页，所以重写了`start_requests()`方法，给了一个`urls`的列表，逐个返回每个连接的`Response`.

##### 3.文件存储

使用了scrapy管道，pipelines

管道文件的修改：

```python
import csv

class MyspiderPipeline:
    def __init__(self):
        # self.file = open('itcast.json','w')
        self.file = open('weather.csv','w',newline='')
        self.csvwriter = csv.writer(self.file)
        self.csvwriter.writerow(['date', 'link', 'situation','temperature','wind'])

    def process_item(self, item, spider):
        tem = dict(item)
        self.csvwriter.writerow([item["date"].strip(), item["link"], item["situation"].replace("\r\n","").replace(" ",""),item["temperature"].replace("\r\n","").replace(" ",""),item["wind"].replace("\r\n","").replace(" ","")])

        return item

    def close_spider(self,spider):
        self.file.close()
```

存储成csv文件。首先初始化新建文件，写入表头。然后处理数据，中间件返回的item是自己建的一个实例化对象，使用的时候是需要将自己创建的对象转化为dict的，这里scrapy带了一个dict方法可以实现直接转。

日志中的输出，因为网页自带了分隔符，中间有\r\n，所以存储的时候需要替换所有分隔符，以及删除空格。这是log过程中打印的内容，可以看到白天地方数据和晚上的数据中间有分隔符。

`__init__()`方法用于打开文件，如果不存在则新建。`__close_spider__()`这两个方法分别在开启和关闭的时候执行一次。



```
{'date': '\r\n                                           2019年07月10日\r\n                                         \r\n
   ', 'link': 'http://www.tianqihoubao.com/lishi/xian/20190710.html', 'situation': '多云\r\n                                        /阴', 'temperature': '31℃\r
\n                                        /\r\n                                        18℃', 'wind': '东北风 1-2级\r\n                                        /
东北风 1-2级'}
```

启用管道

设置管道之后需要在settings.py中注释的代码取消注释。顺便将遵守网站爬虫的协议改为False

```python
ITEM_PIPELINES = {
   'myspider.pipelines.MyspiderPipeline': 300,
}

ROBOTSTXT_OBEY = False
```

##### 4.实验结果

![image-20201003171010878](https://gitee.com/karlhan/picgo/raw/master/img//image-20201003171010878.png)

一共是1737条数据，含表头。存储在了weather.csv文件中。

### 改进优化

###### 1.顺序爬取

Scrapy使用了多线程机制，所以每次爬取的内容不一样，顺序也不是按照时间为序的。这是官方文档的解释。

![在这里插入图片描述](https://gitee.com/karlhan/picgo/raw/master/img//20190810200807343.jpg)

异步处理请求，就是在Scrapy发送请求之后，不会等待这个请求的相应，而是同时发送其他请求或者做别的事。影响服务器对相应的请求是多方面的。

所以我这里是最简单的办法，将年份的年月日省去，直接升序排列。

###### 2.数据进一步处理

数据需要再进一步处理，不能直接用。比如需要把白天和晚上的数据分开。存在了weather_2.csv中。

![image-20201007164022700](https://gitee.com/karlhan/picgo/raw/master/img//image-20201007164022700.png)

###### 3. 随机请求代理

爬虫在请求的时候会自己声明是一个爬虫，因此网站可能会对其进行限制。

User-Agent是HTTP头的一部分，向网站提供者标明使用的浏览器，操作系统版本等。可以用来进行伪装。

新建一个USER_AGENT_LSET

```python
USER_AGENT_LIST=[
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]
```

在middlewares.py中，写RandomUserAgent()

```python
class RandomUserAgent(object):
    def process_request(self,request,spider):
        print(request.headers['User-Agent'])
        ua = random.choice(USER_AGENT_LIST)
        request.headers['User-Agent'] = ua
```

然后再去管道启用，这样每次爬取就会从列表中随机选一个名称，然后发送给网站，网站就不会封禁了。

### 遇到的坑

##### 通过xpath爬取数据返回空列表：

浏览器会对html文本进行一定的规范化，所以会自动在路径中加入tbody，导致读取失败，在此处直接在路径中去除tbody即可。https://jingyan.baidu.com/article/d621e8dac5c0da6865913fa5.html



### 总结

首先是寻找要爬的网站，这里国内很少很少，很多只能查看七天的数据，中国气象局只能看热力图，可能我太菜了，不会爬取。国外的数据真的是非常非常多，有的可以直接下载。

这个框架是先花了三天临时学的，有很多可以改进的地方。尽力了。。

