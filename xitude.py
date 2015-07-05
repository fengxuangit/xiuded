#!/usr/bin/env python
#! encoding: utf-8
import sys
import re
import time
import urllib2
import optparse
from bs4 import BeautifulSoup
from optparse import OptionParser

KEY = '2fdbb73b10c5c0a1e9c31f36140089cbc2d0c12fae18ae012c08be8adb30311f' #api网站所需要的key

class Xitude:
    country = ''
    city = ''
    def usage(self):
        parser = OptionParser()
        parser.add_option("-c", "--cfile", dest="cfile",
                          help="city file")  #城市列表文件
        parser.add_option("-s", "--sfile",dest="sfile",
                          help="The file to save") #保存经纬度文件
        global options
        (options, args) = parser.parse_args()

    def Getitude(self, ip):
        url = 'http://api.ipinfodb.com/v3/ip-city/?key=%s&ip=%s' % (KEY, ip)  #这个是查询经纬度api的网站
        #谷歌api貌似好难申请
        req = urllib2.urlopen(url)
        data = re.split('(.*?);', req.read())
        lai = data[-4:-3][0] #纬度
        long = data[-2:-1][0] #经度
        return lai, long

    def Zoomeyespider(self, query):
        url = 'http://www.zoomeye.org' + query
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) '
        'AppleWebKit/531.21.10 (KHTML, like Gecko) '
        'Version/4.0.4 Mobile/7B334b Safari/531.21.102011-10-16 20:23:50')
        try:
            html = urllib2.urlopen(req)
        except:
            return False
        return self.Calcitude(html)

    def Calcitude(self, html):
        soup = BeautifulSoup(html, 'lxml') #使用BeautifulSoup解析html,不用写正则的，比较快速、方便
        ips = soup.find_all('a', attrs={'class', 'ip'}, limit=3) #这一步对zoomeye的搜索页提取ip
        lai = 0.00
        longs = 0.00
        for ip in ips:
            la, long = list(self.Getitude(ip.text))
            lai += float(la)
            longs += float(long)
        return str(lai /3 ) + " : "+ str(longs/3)  #对经纬度进行平均分，保证准确度

    def filesave(self, data ,file=None):
        if file ==None:
            file = options.sfile
        savefile = open(file, 'a+')
        savefile.write(data + "\r\n")
        savefile.close()

    def main(self):
        self.usage()
        if sys.argv < 1:
            self.usage()
        for line in open(options.cfile):
            print "[*]----------start------------"
            line = line.strip()
            self.country = line[0:line.find('.')]
            self.city = line[line.find('.')+1:]
            query = '/search?q=country:"%s"+city:"%s"' % (self.country, self.city)
            if self.Zoomeyespider(query) != False: #这一步是因为有的城市名在zoomeye上搜索的时候报错 出现400错误
                tude = self.Zoomeyespider(query)

            else:
                self.filesave(line, 'error.log')  #把报错的城市名保存到错误日志中
                continue
            self.filesave(line + "    " + tude)
            print "[!]-- %s --is--ok" % (line + "    " + tude)

if __name__ == '__main__':
    a = Xitude()
    sys.exit(a.main())