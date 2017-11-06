import scrapy
import re
from zhihu.items import ZhihuQuestionItem, ZhihuAnswerItem
import json


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
        'email': '610426459@qq.com',
        'password': 'zhihu,wohen.610',
    }

    # 验证码的文字位置是固定的
    capacha_index = [
        [12.95, 14.969999999999998],
        [36.1, 16.009999999999998],
        [57.16, 24.44],
        [84.52, 19.17],
        [108.72, 28.64],
        [132.95, 24.44],
        [151.89, 23.380000000000002]
    ]

    # 点击查看更多答案触发的url
    more_answer_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B*%5D.i' \
                      's_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_actio' \
                      'n%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_ed' \
                      'it%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2' \
                      'Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Crevie' \
                      'w_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2' \
                      'Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B*%5D.mark_infos%5B*%5D.ur' \
                      'l%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.t' \
                      'opics&offset={1}&limit={2}&sort_by=default'

    def start_requests(self):

        yield scrapy.Request('https://www.zhihu.com/', headers=self.headers,
                             callback=self.login_zhihu)

    def login_zhihu(self, response):
        """ 获取xsrf及验证码图片 """
        xsrf = re.findall(r'name="_xsrf" value="(.*?)"/>', response.text)[0]
        self.headers['X-Xsrftoken'] = xsrf
        self.post_data['_xsrf'] = xsrf

        times = re.findall(r'<script type="text/json" class="json-inline" data-n'
                           r'ame="ga_vars">{"user_created":0,"now":(\d+),', response.text)[0]
        captcha_url = 'https://www.zhihu.com/' + 'captcha.gif?r=' + times + '&type=login&lang=cn'

        yield scrapy.Request(captcha_url, headers=self.headers, meta={'post_data': self.post_data},
                             callback=self.veri_captcha)

    def veri_captcha(self, response):
        """ 输入验证码信息进行登录 """
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
        """ 将输入的位置转换为相应信息 """
        a = int(a)
        b = int(b)
        # b = 0代表只有一个倒立文字
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
        """ 获取首页问题 """
        question_ursl = re.findall(r'https://www.zhihu.com/question/(\d+)', response.text)

        for url in question_ursl:
            question_detail = 'https://www.zhihu.com/question/' + url
            yield scrapy.Request(question_detail, headers=self.headers, callback=self.parse_question)

    def parse_question(self, response):
        """ 解析问题详情及获取指定范围答案 """
        text = response.text
        item = ZhihuQuestionItem()

        item['name'] = re.findall(r'<meta itemprop="name" content="(.*?)"', text)[0]
        item['url'] = re.findall(r'<meta itemprop="url" content="(.*?)"', text)[0]
        item['keywords'] = re.findall(r'<meta itemprop="keywords" content="(.*?)"', text)[0]
        item['answer_count'] = re.findall(r'<meta itemprop="answerCount" content="(.*?)"', text)[0]
        item['comment_count'] = re.findall(r'<meta itemprop="commentCount" content="(.*?)"', text)[0]
        item['flower_count'] = re.findall(r'<meta itemprop="zhihu:followerCount" content="(.*?)"', text)[0]
        item['date_created'] = re.findall(r'<meta itemprop="dateCreated" content="(.*?)"', text)[0]

        yield item

        question_id = int(re.match(r'https://www.zhihu.com/question/(\d+)', response.url).group(1))
        # 此处为获取该问题第10到第30的答案
        yield scrapy.Request(self.more_answer_url.format(question_id, 10, 30), headers=self.headers,
                             callback=self.parse_answer)

    def parse_answer(self, response):
        """ 解析获取到的指定范围答案 """
        answers = json.loads(response.text)

        for ans in answers['data']:
            item = ZhihuAnswerItem()
            item['question_id'] = re.match(r'http://www.zhihu.com/api/v4/questions/(\d+)', ans['question']['url']).group(1)
            item['author'] = ans['author']['name']
            item['ans_url'] = ans['url']
            item['comment_count'] = ans['comment_count']
            item['upvote_count'] = ans['voteup_count']
            item['excerpt'] = ans['excerpt']

            yield item



