import scrapy


xpath_dict = {
    'city_list': '//div[@class="city_list"]//li[@class="CLICKDATA"]',
    'district_list': '//li[@data-type="district"][position()>1]',
    'bizcircle_list': '//li[@data-type="bizcircle"][position()>1]',
    'content_list': '//p[@class="content__list--item--title"]',
    'next_page': '//div[@class="content__pg"]/a[@class="next"]/@href',
}

content_xpath_dict = {
    'content_title': '//p[@class="content__title"]/text()',
    'content_price': '//div[@class="content__aside--title"]/span/text()',
    'content_tag_list': '//p[@class="content__aside--tags"]/i/text()',
    'content_core': '//ul[@class="content__aside__list"]/li//text()',
    'content_info': '//div[@class="content__article__info"]/ul//text()',
    'content_facility_name': '//ul[@class="content__article__info2"]/li[count(i)=1]/text()',
    'content_facility_state': '//ul[@class="content__article__info2"]/li[count(i)=1]/@class',
    'content_picture_name': '//ul[@class="piclist"]/li/img/@data-name',
    'content_picture_url': '//ul[@class="piclist"]/li/img/@src',
    'content_cost_name': '//*[@id="cost"]/div/div[2]/ul/li/text()',
    'content_cost_value': '//*[@id="cost"]/div/div[2]/div/ul/li/text()',
    'content_around': '//div[@id="around"]/ul[2]/li/span/text()',
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
            yield scrapy.Request(url=url, callback=self.find_content_list, cb_kwargs=kwargs)

    def find_content_list(self, response, **kwargs):
        next_page = response.xpath(f"{xpath_dict['next_page']}").extract_first()
        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page, callback=self.find_content_list, cb_kwargs=kwargs)

        content_list = response.xpath(f"{xpath_dict['content_list']}//a/text()").extract()
        url_list = response.xpath(f"{xpath_dict['content_list']}//a/@href").extract()
        content_url_dict = dict(zip(content_list, url_list))
        for content, url in content_url_dict.items():
            url = response.urljoin(url)
            kwargs = {**kwargs, 'content': content.strip(), 'content_url': url}
            yield scrapy.Request(url=url, callback=self.parse_content, cb_kwargs=kwargs)

    def parse_content(self, response, **kwargs):
        for key, value in content_xpath_dict.items():
            content = response.xpath(value).extract()
            content = [x.strip() for x in content if x.strip()]
            kwargs = {**kwargs, key: content}

        content_core = kwargs.pop('content_core')
        kwargs['content_core'] = dict(zip(content_core[::2], content_core[1::2]))
        kwargs['content_facility'] = dict(zip(kwargs.pop('content_facility_name'), kwargs.pop('content_facility_state')))
        kwargs['content_picture'] = dict(zip(kwargs.pop('content_picture_name'), kwargs.pop('content_picture_url')))
        kwargs['content_cost'] = dict(zip(kwargs.pop('content_cost_name'), kwargs.pop('content_cost_value')))

        yield kwargs