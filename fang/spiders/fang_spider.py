# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy_redis.spiders import RedisSpider
from fang.items import NewHouseItem,ESFItem
class FangSpiderSpider(RedisSpider):
    name = 'fang_spider'
    allowed_domains = ['fang.com']
    #start_urls = ['https://www.fang.com/SoufunFamily.htm']
    redis_key = "fang:start_urls"

    def parse(self, response):
        trs = response.xpath('.//table[@class="table01"]//tr')
        province=None
        for tr in trs:

            tds = tr.xpath('.//td[not(@class)]')
            print(tds)
            province_td=tds[0]
            province_text=province_td.xpath('.//text()').get()


            province_text=re.sub(r'\s','',province_text)
            if province_text:
                province=province_text
            if province =="其它":
                continue

            #print(province)

            city_td=tds[-1]
            print(city_td)
            city_links=city_td.xpath('.//a')
            for city_link in city_links:
                city=city_link.xpath('.//text()').get()
                city_url=city_link.xpath('.//@href').get()
                #print(province,city,city_url)
                url_module=city_url.split('//')
                #print(url_module)
                scheme =url_module[0]
                domain = url_module[1]
                if 'bj.' in domain:
                    newhourse_url="https://newhouse.fang.com/house/s/"
                    esf_url="https://esf.fang.com"
                else:
                    newhourse_url = scheme + '//' + "newhouse." + domain + "house/s/"
                    esf_url = scheme + "//" + "esf." + domain

                #print(newhourse_url,esf_url)
                yield scrapy.Request(url=newhourse_url,callback=self.parse_newhouse,meta={'info':(province,city)})



                yield  scrapy.Request(url=esf_url,callback=self.parse_esf,meta={'info':(province,city)})



    def parse_newhouse(self,response):
        province = response.meta['info'][0]
        city = response.meta['info'][1]
        newhouse_lis=response.xpath('.//div[@id="newhouse_loupai_list"]/ul/li')
        for newhouse_li in newhouse_lis:
            name=newhouse_li.xpath('.//div[@class="nlcd_name"]/a/text()').get()
            if name ==None:
                continue
            name=name.strip()
            rooms = newhouse_li.xpath(".//div[contains(@class,'house_type')]/a/text()").getall()
            if rooms==[]:
                continue
            area = "".join(newhouse_li.xpath(".//div[contains(@class,'house_type')]/text()").getall())
            area = re.sub(r"\s|/|－","",area)
            address = newhouse_li.xpath(".//div[@class='address']/a/@title").get()
            district = "".join(newhouse_li.xpath(".//div[@class='address']/a//text()").getall())

            district=re.search(r".*\[(.*?)\].*",district).group(1)
            sale = newhouse_li.xpath('.//div[contains(@class,"fangyuan")]/span/text()').get()
            prise = newhouse_li.xpath(".//div[@class='nhouse_price']//text()").getall()
            prise="".join(prise)
            prise = re.sub(r"\s|广告","",prise)
            origin_url= newhouse_li.xpath(".//div[@class='nlcd_name']/a/@href").get()
            origin_url="http:"+origin_url

            item=NewHouseItem(name=name,rooms=rooms,area=area,address=address,district=district,sale=sale,prise=prise,origin_url=origin_url,province=province,city=city,where="NH")
            yield item
        next_url=response.xpath('.//a[@class="next"]/@href').get()
        if next_url:

            next_url=response.urljoin(next_url)
            print(next_url)
            yield  scrapy.Request(next_url,callback=self.parse_newhouse,meta={'info':(province,city)})



    def parse_esf(self,response):
        province = response.meta['info'][0]
        city = response.meta['info'][1]
        esf_dls=response.xpath(".//dl[@class='clearfix']")
        for esf_dl in esf_dls:
            #print(esf_dl)
            name=esf_dl.xpath(".//h4/a/@title").get()
            #print(name)
            details="".join(esf_dl.xpath(".//p[@class='tel_shop']//text()").getall()).strip()
            details=re.sub(r"\s","",details)
            district=esf_dl.xpath(".//p[@class='add_shop']/a/@title").get()

            address = esf_dl.xpath(".//p[@class='add_shop']/span/text()").get()
            prise = " ".join(esf_dl.xpath('.//dd[@class="price_right"]//text()').getall())
            prise = re.sub(r"\s|\r|\n","",prise)
            origin_url = response.urljoin(esf_dl.xpath(".//h4/a/@href").get())

            item=ESFItem(name=name,address=address,prise=prise,details=details,district=district,origin_url=origin_url,province=province,city=city,where="ESF")
            yield item
        next_url = response.xpath(".//div[@class='page_al']//a[text()='下一页']/@href").get()
        if next_url:
            next_url=response.urljoin(next_url)
            print(next_url)
            yield scrapy.Request(url=next_url,callback=self.parse_esf,meta={'info':(province,city)})




