# ZhiHuSpider

### 目标：爬取知乎首页前x个问题(many)的详情及问题指定范围内的答案(many)

### power by:
1. Python 3.6
2. Scrapy 1.4
3. json
4. pymysql

#### 博客地址：http://blog.csdn.net/sinat_34200786/article/details/78449499
---
### How to use：

```
git clone 
```
Rewrite the POST_DATA, QUESTION_COUNT, ANSWER_COUNT_PER_QUESTION, ANSWER_OFFSET and Mysql information
in settings.py

```
Note: Before you run the project, make sure that you have created tables match the requirement 
```
```
scrapy crawl zhihu
```

---
###图片展示

