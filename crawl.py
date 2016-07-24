#!/usr/bin/env python
# -*- coding: utf-8 -*-
# haierlord@gmail.com 2015-11-21 17:17:11


url = 'https://shopsearch.taobao.com/search?app=shopsearch&initiative_id=staobaoz_20151202&q=大衣&fs=1&isb=0&sort=sale-desc&s=20'


import sys
reload(sys)

import urllib2, socket, time
import re, random, types

from bs4 import BeautifulSoup

user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0', \
		'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0', \
		'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+ \
		(KHTML, like Gecko) Element Browser 5.0', \
		'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)', \
		'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)', \
		'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14', \
		'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) \
			           Version/6.0 Mobile/10A5355d Safari/8536.25', \
		'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
			           Chrome/28.0.1468.0 Safari/537.36', \
		'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)']


base_url = 'https://www.baidu.com'

class TaobaoAPI:

	def __init__(self):
		timeout = 1
		socket.setdefaulttimeout(timeout)

	def randomSleep(self):
		sleeptime = random.randint(1, 2)
		time.sleep(sleeptime)

	def crawl_layer1(self, html):
		results = []
		soup = BeautifulSoup(html)
		div = soup.find("ul", id = "list-container")
		
		lis = div.findAll("li", {"class": "list-item"})
		if (len(lis) > 0):
			for li in lis[:]:
				result = {}
				cur_li = li.find("li", {"class": "list-img"})
				content = cur_li.find("a")
				uid = content.attrs["data-uid"]
				url = "https:" + content.attrs["href"]
				title = content.attrs["title"]
				text = li.find("span", {"class": "info-sale"}).getText()
				sales = re.search("\d+", text).group()
				text = li.find("div", {"class": "good-comt"}).getText()
				goodrate = re.search("[\d\.%]", text).group()
#				print url
				html = self.getHtml(url)
				description_score, service_score, logistics_score = self.get3score(html, url)
				result = {"id": uid, "url": url, "title": title, "sales": sales, "goodrate": goodrate, "description_score": description_score, "service_score": service_score, "logistics_score": logistics_score}
				results.append(result)
		return results

	def get3score(self, html, url):
		html = html.split("mini-dsr-wrap")
		if len(html) > 1:
			html = html[1]
			tuple6 = re.findall("\">(\s*\S+\s*)</span", html)
			return (tuple6[1], tuple6[3], tuple6[5])
		else:
			html = html[0]
			tuple3 = re.findall("\"rateinfo\">\s*<em>(\d\.\d)</em>\s*<i class=\"rate-icon", html)
			if len(tuple3) == 3:
				return tuple3
			else:
				print url
				if "该店铺尚未收到评价" in html:
					print "该店铺尚未收到评价"
				return ("NONE", "NONE", "NONE")


	def getHtml(self, url):
		retry = 3
		html = ""
		while(retry > 0):
			try:
				request = urllib2.Request(url)
				length = len(user_agents)
				index = random.randint(0, length - 1)
				user_agent = user_agents[index]
				request.add_header("User-agent", user_agent)
				request.add_header("connection", 'keep-alive')
				response = urllib2.urlopen(request)
				html = response.read()
				break
			except urllib2.URLError, e:
				print "url error", e
				self.randomSleep()
				retry = retry - 1
				continue
			
			except Exception, e:
				print "error", e
				retry = retry - 1
				self.randomSleep()
				continue
		return html



	def search(self, url):
		results = []
		retry = 3
		while(retry > 0):
			try:
				request = urllib2.Request(url)
				length = len(user_agents)
				index = random.randint(0, length - 1)
				user_agent = user_agents[index]
				request.add_header("User-agent", user_agent)
				request.add_header("connection", 'keep-alive')
				response = urllib2.urlopen(request)
				html = response.read()
				results += self.crawl_layer1(html)
				break
			except urllib2.URLError, e:
				print "url error", e
				self.randomSleep()
				retry = retry - 1
				continue
			
			except Exception, e:
				print "error", e
				retry = retry - 1
				self.randomSleep()
				continue
		return results
		
if __name__ == "__main__":
	categorys = ["大衣", "风衣", "羽绒服", "牛仔裤", "内衣", "帽子", "运动鞋", "篮球鞋", "毛衣", "衬衫"]
	url = 'https://shopsearch.taobao.com/search?app=shopsearch&initiative_id=staobaoz_20151202&q=大衣&fs=1&isb=0&sort=sale-desc&s=0'
	test = TaobaoAPI()
	out = open("test.csv", "w")
	keys = ["category", "id", "url", "title", "sales", "goodrate", "description_score", "service_score", "logistics_score"]
	for key in keys:
		out.write(key + ",")
	out.write("\n")
	for category in categorys:
		for s in range(100):
			url = 'https://shopsearch.taobao.com/search?app=shopsearch&initiative_id=staobaoz_20151202&q=%s&fs=1&isb=0&sort=sale-desc&s=%d'%(category, s)
			results = test.search(url)
			for t in results:
				out.write(category + ",")
				for key in keys[1: ]:
					out.write("%s," % t[key].encode("gbk"))
				out.write("\n")
	out.close()
