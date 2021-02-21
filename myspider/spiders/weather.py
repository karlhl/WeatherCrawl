import scrapy
from myspider.items import MyspiderItem


class WeatherSpider(scrapy.Spider):
    name = 'weather'
    allowed_domains = ['tianqihoubao.com']

    # start_urls = ['http://www.tianqihoubao.com/lishi/xian/month/201510.html']

    def parse(self, response):
        # 提取数据
        node_list = response.xpath('//*[@id="content"]/table/tr')
        # print(len(node_list))
        for i, node in enumerate(node_list):
            # if i != 5:
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
