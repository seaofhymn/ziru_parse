# -*- coding: utf-8 -*-
from pymysql import *
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ZiruPipeline(object):
    def process_item(self, item, spider):
        con = connect(host="192.168.64.129", port=3306, user='root', password='123', database='ziru', charset='utf8')
        cur = con.cursor()

        sql = """insert into zufang (name,price,detail,more,href,img) values("%s","%s","%s","%s","%s","%s");""" %(item["name"], item["price"], item["detail"], item["more"], item["href"], item["img"])

        # sql = """insert into yunyinyue (na,likes,href) values("%s","%s","%s");""" %(item["name"],item["likes"],item["href"])
        cur.execute(sql)
        con.commit()
        # print(item)

        print(item)
        cur.close()
        con.close()
        return item
