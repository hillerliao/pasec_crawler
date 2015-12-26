# coding=utf-8
# 文章信息保存到details_list中，包括标题，作者，发布时间，内容, 页面地址
# /usr/bin/python
# 参考教程 http://ju.outofmemory.cn/entry/75116
# BeautifulSoap教程 http://cuiqingcai.com/1319.html
# BeautifulSoap文档 http://www.crummy.com/software/BeautifulSoup/bs4/doc/#string
# 

'''
1、抓取 http://stock.pingan.com/guanyuwomen/zuixingonggao/index.shtml 
中 title 包含 『测试公告』 or 『维护公告』 字符的文章，抓取内容包括：日期 、标题、链接、正文。
2、将抓取下来的文章，发邮件到 liaozhihai@xueqiu.com 。
邮件标题 = 日期+标题 
邮件正文 = 日期+标题+
'''

import sys

reload(sys)
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup
import urllib2
import socket
import sqlite3
import requests
import re

url = 'http://stock.pingan.com/servlet/article/Article?catalogId=2962'
socket.setdefaulttimeout(200)
# soup = BeautifulSoup(urllib2.urlopen(url).read(), 'lxml', from_encoding='GBK')
soup = BeautifulSoup(urllib2.urlopen(url).read(), 'lxml', from_encoding='utf-8')

href_list_all = [a.get('href') for a in soup.find_all('a')]


re_web_url = re.compile(r'(http://stock.pingan.com/a/[0-9.]+)\/[0-9.]+\.shtml$')

href_list = []
for href in href_list_all:
    if re_web_url.match(href) and urllib2.urlopen(href).read().find('body') > 0:
        href_list.append(href)

#print href_list

details_list = []
# connect to SQLite
try:
    con = sqlite3.connect('PA_NOTICE')
    cur = con.cursor()
    cur.execute("drop table if exists notice_category")
    cur.execute("drop table if exists notice_content")
    cur.execute("drop table if exists notice")
    cur.execute("create table notice (title text, author varchar(50), date varchar(50), source_address text, content text)")
    cur.execute("create table notice_category(sid int, title text, date varchar(50), author varchar(50), source_address text)")
    cur.execute("create table notice_content(source_address text, content text)")


    for href in href_list:
        sub_details_list = []
        detail_soup = BeautifulSoup(urllib2.urlopen(href).read(), 'lxml', from_encoding='utf-8')

        try:
            article_title = detail_soup.find('span', {'id': 'title'}).string
            article_contents_original = detail_soup.find('div', {'class':'artMain'}).contents
            #过滤 <STYLE>里面的一大坨
            dr1 = re.compile(r'<style>*<style>')
            article_contents = dr1.sub('', str(article_contents_original))
            #过滤html标签
            dr2 = re.compile(r'<[^>]+>')
            article_contents = dr2.sub('', str(article_contents))
            article_pub_date = detail_soup.find('div', {'class':'futxt'}).span.string
           # 发布时间还可以从 href 中找到 http://stock.pingan.com/a/20151127/8370644.shtml
            article_author = '平安证券官网'
            # TODO 需要过滤内容中的html标签
            article_source_address = href
            
            sub_details_list.append(article_title)
            sub_details_list.append(article_author)
            sub_details_list.append(article_pub_date)
            sub_details_list.append(article_source_address)
            sub_details_list.append(article_contents)

            details_list.append(sub_details_list)
            
            cur.execute('delete from notice_category where source_address = "%s"' %article_source_address)
            cur.execute('delete from notice_content where source_address = "%s"' %article_source_address)
            cur.execute('insert into notice_category(sid, title, date, author, source_address) values(3, "%s", "%s",  "%s", "%s")' %(article_title, article_pub_date, article_author, article_source_address))
            #TODO 先测试数据库连接与建表
            
            #article_contents = con.escape_string(str(article_contents))
            cur.execute('insert into notice_content(source_address, content) values("%s", "%s")' %(article_source_address, article_contents))
        


        except sqlite3.Error, msg:
            print msg
        
    con.commit()
    cur.close()
    con.close()
except sqlite3.Error, msg:
    print msg
#print str(details_list[1])
