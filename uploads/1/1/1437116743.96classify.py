#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import csv

reload(sys)
sys.setdefaultencoding("utf-8")
baseDir = os.getcwd()

def searchKeyword(keyword, content, line):
	if str(content).find(keyword) != -1:
		if not os.path.exists(keyword + ".csv"):
			fi = open(keyword+".csv", 'ab')
			fi.write("博主名称,博主地址,微博地址,发布时间,微博内容".decode("utf-8").encode("gbk")+"\r\n")
			fi.close()
		fi = open(keyword+".csv", 'ab')
		fi.write(line[0] + "," + line[1] + "," + line[2] + "," + line[3] + "," + line[4].decode("gbk", "ignore").encode("utf-8").replace(',', '，'.decode("gbk", "ignore").encode("utf-8")).decode("utf-8").encode("gbk") +'\r\n')
		fi.flush()
		fi.close()


begin = datetime.datetime(2015,1,1)
end = datetime.datetime(2015,3,30)
for i in range((end - begin).days+1):
	day = begin + datetime.timedelta(days=i)
	if os.path.exists(day.strftime("%Y.%m.%d") + ".csv"):
		f = open(day.strftime("%Y.%m.%d") + ".csv", "rb")
		f.readline()
		reader = csv.reader(f)
		keyword = ["投资", "增长", "经济", "增速", "GDP", "财经", "金融", "创业", "人民币", "汇率", "上市", "IPO", "证券", "大盘", "股市", "股票", "融资", "商业", "O2O", "资本", "零售", "电商", "地产", "首富", "经济", "出口", "进口", "外贸", "利率", "市场", "代购", "水货", "淘宝", "购物", "便宜", "iphone", "奶粉", "海关", "免税"]
		for line in reader:
			for key in keyword:
				searchKeyword(key, line[4].decode("gbk", "ignore").encode("utf-8"), line)


