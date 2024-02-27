from pathlib import Path

import scrapy


xpath_dict = {
    'city_list': '//div[@class="city_list"]//li[@class="CLICKDATA"]',
    'district_list': '//li[@data-type="district"][position()>1]',
    'bizcircle_list': '//li[@data-type="bizcircle"][position()>1]',
    'content_list': '//div[@class="content__list"]',
    'content_num': '',
    'page_down': '',
}


class HouseSpider(scrapy.Spider):
    name = "house"

    def start_requests(self):
        urls = [
            'https://www.ke.com/city/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.find_city_list)

    def find_city_list(self, response):
        city_list = response.xpath(f"{xpath_dict['city_list']}/a/text()").extract()
        url_list = response.xpath(f"{xpath_dict['city_list']}/a/@href").extract()
        city_url_dict = dict(zip(city_list, url_list))
        for city, url in city_url_dict.items():
            url = f'https:{url}/zufang'
            kwargs = {'city': city, 'city_url': url}
            yield scrapy.Request(url=url, callback=self.find_district_list, cb_kwargs=kwargs)

    def find_district_list(self, response, **kwargs):
        district_list = response.xpath(f"{xpath_dict['district_list']}/a/text()").extract()
        url_list = response.xpath(f"{xpath_dict['district_list']}/a/@href").extract()
        district_url_dict = dict(zip(district_list, url_list))
        for district, url in district_url_dict.items():
            url = response.urljoin(url)
            kwargs = {**kwargs, 'district': district, 'district_url': url}
            yield scrapy.Request(url=url, callback=self.find_bizcircle_list, cb_kwargs=kwargs)

    def find_bizcircle_list(self, response, **kwargs):
        bizcircle_list = response.xpath(f"{xpath_dict['bizcircle_list']}/a/text()").extract()
        url_list = response.xpath(f"{xpath_dict['bizcircle_list']}/a/@href").extract()
        bizcircle_url_dict = dict(zip(bizcircle_list, url_list))
        for bizcircle, url in bizcircle_url_dict.items():
            url = response.urljoin(url)
            kwargs = {**kwargs, 'bizcircle': bizcircle, 'bizcircle_url': url}
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs=kwargs)

    def parse(self, response, **kwargs):
        print(kwargs)
        print(response.url)
