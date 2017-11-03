import scrapy
import re
from zhihu.items import ZhihuItem
from zhihu.items import ZhihuQuestionItem


class ZhiHuSpider(scrapy.Spider):

    name = "zhihu"
    start_urls = ['https://zhihu.com']
    allowed_domains = ['www.zhihu.com']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
        'Connection': 'keep-alive',
        'Host': 'www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 ('
                      'KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
        'Referer': 'https://www.zhihu.com/',
    }

    post_data = {
        'captcha_type': 'cn',
        'email': '123456@qq.com',
        'password': 'password',
    }

    capacha_index = [
        [12.95, 14.969999999999998],
        [36.1, 16.009999999999998],
        [57.16, 24.44],
        [84.52, 19.17],
        [108.72, 28.64],
        [132.95, 24.44],
        [151.89, 23.380000000000002]
    ]

    def start_requests(self):

        yield scrapy.Request('https://www.zhihu.com/', headers=self.headers,
                             callback=self.login_zhihu)

    def login_zhihu(self, response):

        xsrf = re.findall(r'name="_xsrf" value="(.*?)"/>', response.text)[0]
        self.headers['X-Xsrftoken'] = xsrf
        self.post_data['_xsrf'] = xsrf
        times = re.findall(r'<script type="text/json" class="json-inline" data-n'
                           r'ame="ga_vars">{"user_created":0,"now":(\d+),', response.text)[0]
        captcha_url = 'https://www.zhihu.com/' + 'captcha.gif?r=' + times + '&type=login&lang=cn'

        yield scrapy.Request(captcha_url, headers=self.headers, meta={'post_data': self.post_data},
                             callback=self.veri_captcha)

    def veri_captcha(self, response):

        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)
        loca1 = input('input the loca 1:')
        loca2 = input('input the loca 2:')
        captcha = self.location(loca1, loca2)
        self.post_data = response.meta.get('post_data', {})
        self.post_data['captcha'] = captcha
        post_url = 'https://www.zhihu.com/login/email'
        yield scrapy.FormRequest(post_url, formdata=self.post_data, headers=self.headers,
                                 callback=self.login_success)

    def location(self, a, b):

        a = int(a)
        b = int(b)
        if b != 0:
            captcha = "{\"img_size\":[200,44],\"input_points\":[%s,%s]}" % (str(self.capacha_index[a - 1]),
                                                                            str(self.capacha_index[b - 1]))
        else:
            captcha = "{\"img_size\":[200,44],\"input_points\":[%s]}" % str(self.capacha_index[a - 1])
        return captcha

    def login_success(self, response):

        if 'err' in response.text:
            print(response.text)
            print("error!!!!!!")
        else:
            print("successful!!!!!!")
            yield scrapy.Request('https://www.zhihu.com', headers=self.headers, dont_filter=True)

    def parse(self, response):

        question_ursl = re.findall(r'https://www.zhihu.com/question/(\d+)', response.text)
        for url in question_ursl:
            question_detail = 'https://www.zhihu.com/question/' + url
            yield scrapy.Request(question_detail, headers=self.headers, callback=self.parse_question)

    def parse_question(self, response):

        text = response.text
        item = ZhihuQuestionItem()

        item['name'] = re.findall(r'<meta itemprop="name" content="(.*?)"', text)[0]
        item['url'] = re.findall(r'<meta itemprop="url" content="(.*?)"', text)[0]
        item['keywords'] = re.findall(r'<meta itemprop="keywords" content="(.*?)"', text)[0]
        item['answer_count'] = int(re.findall(r'<meta itemprop="answerCount" content="(.*?)"', text)[0])
        item['comment_count'] = int(re.findall(r'<meta itemprop="commentCount" content="(.*?)"', text)[0])
        item['flower_count'] = int(re.findall(r'<meta itemprop="zhihu:followerCount" content="(.*?)"', text)[0])
        item['date_created'] = re.findall(r'<meta itemprop="dateCreated" content="(.*?)"', text)[0]
        yield item
