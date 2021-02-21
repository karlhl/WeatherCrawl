# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv

class MyspiderPipeline:
    def __init__(self):
        self.file = open('weather_2.csv','w',newline='')
        self.csvwriter = csv.writer(self.file)
        self.csvwriter.writerow(['date', 'link', 'situation(day)','situation(night)','temperature(day)','temperature(night)','wind(day)','wind(night)'])

    def process_item(self, item, spider):
        item = dict(item)
        temp_situ = item["situation"].replace("\r\n","").replace(" ","").split('/')
        temp_tenperature = item["temperature"].replace("\r\n","").replace(" ","").split('/')
        temp_wind = item["wind"].replace("\r\n","").replace(" ","").split('/')
        self.csvwriter.writerow([item["date"].strip().replace("年","").replace("月","").replace("日",""), item["link"], temp_situ[0],temp_situ[1],temp_tenperature[0],temp_tenperature[1],temp_wind[0],temp_wind[1]])

        return item

    def close_spider(self,spider):
        self.file.close()