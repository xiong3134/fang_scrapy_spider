# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from fang import settings

class FangPipeline(object):
    def __init__(self):
                  connection = pymongo.MongoClient(host="193.112.19.138",port=12707)
                  db = connection.fangzi
                  self.collect_hewhouse = db.newhouse
                  self.collect_ESF = db.esf

    def process_item(self, item, spider):
        if item['where']=="NH":

           self.collect_hewhouse.insert([item])
        else:
            self.collect_ESF.insert([item])
        return item
