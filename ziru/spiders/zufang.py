# -*- coding: utf-8 -*-
import scrapy
import re
from PIL import Image
import base64
import requests
import sys
import io
# tesseract  captcha_0.tif stdout nobatch letters_digits
import pytesseract
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
from scrapy_redis.spiders import RedisSpider
import time
import os
# pytesseract.SetVariable("tessedit_char_whitelist", "0123456789")
class ZufangSpider(RedisSpider):
    name = 'zufang'
    allowed_domains = ['ziroom.com']
    redis_key = 'zufang:start_urls'
    # start_urls = ['http://www.ziroom.com/z/nl/z2-d23008614.html','http://www.ziroom.com/z/nl/z3-d23008626.html','http://www.ziroom.com/z/nl/z3-d23008613.html','http://www.ziroom.com/z/nl/z3-d23008618.html','http://www.ziroom.com/z/nl/z3-d23008629.html','http://www.ziroom.com/z/nl/z3-d23008620.html','http://www.ziroom.com/z/nl/z3-d23008616.html','http://www.ziroom.com/z/nl/z3-d23008624.html','http://www.ziroom.com/z/nl/z3-d23008615.html','http://www.ziroom.com/z/nl/z3-d23008611.html','http://www.ziroom.com/z/nl/z3-d23008625.html','http://www.ziroom.com/z/nl/z3-d23008623.html','http://www.ziroom.com/z/nl/z3-d23008617.html','http://www.ziroom.com/z/nl/z1.html','http://www.ziroom.com/z/nl/z6.html','http://www.ziroom.com/z/nl/z7.html']
    # start_urls =[]
    def parse(self, response):
        self.con = response.body.decode()
        # print(self.con)
        mat = re.search(r"//(.*)s\.png",self.con).group()
        mat_name = "http:"+mat.split("s.png")[0]+".png"
        ret = re.search(r"""png","offset":\[\[(.*)\]\]\};""", self.con).group(1)
        # print(ret)
        print(mat_name)
        ret = ret.split("],[")
        pos_list = list(ret)
        pos = []
        for i in pos_list:
            pos_tmp = list(i.split(','))
            pos.append(pos_tmp)
        # print(each_pos)

        li_list = response.xpath("//li[@class ='clearfix']")
        # print(li_list[6].xpath("./div[@class='txt']/h3/a/text()").extract_first())
        for i in range(0,len(li_list)):
            # print(i)
            item = {}
            item["NUM"] = i
            item["name"] = li_list[i].xpath("./div[@class='txt']/h3/a/text()").extract_first()
            item["detail"] = ",".join(li_list[i].xpath("./div[@class='txt']/div[@class = 'detail']/p/span/text()").extract())
            item["more"] = ",".join(li_list[i].xpath("./div[@class='txt']/p[@class='room_tags clearfix']/span/text()").extract())
            item["href"] = "http:"+li_list[i].xpath("./div[@class ='img pr']/a/@href").extract_first()
            item["img"] = "http:"+li_list[i].xpath("./div[@class ='img pr']/a/img/@_src").extract_first()
            item["pos"] = pos
            # print(item)
            yield scrapy.Request(mat_name, callback=self.write_pic,meta={"item":item},dont_filter=True)

        next_url = "http:"+response.xpath("//a[@class = 'next']/@href").extract_first()
        print(next_url)
        if next_url is not None:
            yield scrapy.Request(next_url,callback=self.parse)

    def write_pic(self,response):
        item = response.meta["item"]
        # print(item["pos"])
        con = response.body
        # print(con)
        self.mat_name = response.url.split("price/")[1]
        with open(r"{}".format(self.mat_name),"wb") as f:
            f.write(con)
            # f.write(con)
            # print(self.mat_name*100)
        try:
            pic_str = list(self.recognize())
            pic_pos=item["pos"][item["NUM"]]
            price = []
            for pos in pic_pos:
                price_tmp = pic_str[int(pos)]
                price.append(price_tmp)
            item["price"] ="".join(price)
            print(item["price"]*100)
            # print(pic_pos)
            # print(pic_str)
            yield item
            # os.remove(self.mat_name)
        except:
            item["price"] = None
            yield item
            # os.remove(self.mat_name)

    def recognize(self):
        img_name = self.mat_name
        img = Image.open("{}".format(img_name))
        img = img.convert("1")
        img.save(self.mat_name)
        result = pytesseract.image_to_string(img)
        if result:
            print(result)
            num_str = "0123456789"
            for i in result:
                num_str = num_str.replace(i, "")
            print(num_str)
            str_get = num_str + result
            print(str_get)
            return str_get
        else:
            return None