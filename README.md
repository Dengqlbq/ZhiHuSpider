# ZhiHuSpider

### 目标：爬取知乎首页前x个问题(many)的详情及问题指定范围内的答案(many)的摘要

### Power by:
1. Python 3.6
2. Scrapy 1.4
3. json
4. pymysql
5. redis

#### Project blog：http://blog.csdn.net/sinat_34200786/article/details/78449499
---
### How to use ?

```
git clone https://github.com/Dengqlbq/ZhiHuSpider.git
```

Rewrite the POST_DATA, QUESTION_COUNT, ANSWER_COUNT_PER_QUESTION, ANSWER_OFFSET and Mysql information
in settings.py

```
cd zhihu/zhihu
```

```
scrapy crawl zhihu
```

```
Note: Before you run the project, make sure that you have created tables match the requirement 
```
---
### Achievement

![1](https://github.com/Dengqlbq/ZhiHuSpider/blob/master/Image/question.png)

![2](https://github.com/Dengqlbq/ZhiHuSpider/blob/master/Image/answer.png)
