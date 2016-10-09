# -*- coding:utf-8 -*-

import requests
import httplib
import urllib2
import traceback
import time
from xiciDbOps import xiciProxy

""" 验证代理是否有效的网站:http://icanhazip.com """

class WaysOfUsingProxy():
    def __init__(self, proxies, testObjweb="http://httpbin.org/ip"):
        self.proxies = proxies
        self.testObjweb = testObjweb
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.xicidaili.com",
            "Referer": "http://www.xicidaili.com/nn",
            "User-Agent": "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0}"
            }
        pass

    def WithRequests(self):
        turl = self.testObjweb
        proxies = {
            'http': self.proxies
        }
        # 'https': self.proxies
        r = requests.get(turl, headers=self.headers, proxies=proxies)
        return r.text, r.status_code
        pass

    def WithUrllib2(self):
        proxies = {"http": self.proxies}
        turl = self.testObjweb
        # 设置使用代理
        proxy_support = urllib2.ProxyHandler(proxies)
        # opener = urllib2.build_opener(proxy_support,urllib2.HTTPHandler(debuglevel=1))
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)

        # 添加头信息，模仿浏览器抓取网页，对付返回403禁止访问的问题
        # i_headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
        # i_headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0'}
        # req = urllib2.Request(turl)
        # html = urllib2.urlopen(req)
        # if turl == html.geturl():
        #     doc = html.read()
        #     return doc
        # return

        resp = urllib2.urlopen(turl)
        return resp.read()


        pass

    def WithHttplib(self):
        '''
            这里仅仅是使用HTTPConnectiona函数实现的，尝试一下set_tunnel函数
        '''

        h2 = httplib.HTTPConnection(self.proxies)  # , source_address=("120.52.72.24", 80)
        # h2.connect()
        h2.request("GET", self.testObjweb)
        resp = h2.getresponse()
        page = resp.read()
        # return page, resp.status
        return page


        pass

class ProxyPool():
    global ProxyIpsCount

    def __init__(self, count=3):
        self.pool = set()
        self.ProxyIpsCount = count
        self.testObjweb = "http://icanhazip.com"
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.xicidaili.com",
            "Referer": "http://www.xicidaili.com/nn",
            "User-Agent": "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0}"
            }


    # 代理商API获取代理
    def getFromDaXiangDaili(self):
        res = requests.get("http://tpv.daxiangip.com/ip/?tid=5570790711890420&num=100&delay=5&category=2")
        # with open("ProxyIps"+str(self.ProxyIpsCount)+".txt", 'w')as wr:
        #     wr.write(res.text)
        with open("ProxyIps1.txt", "r") as rd:
            lines = rd.readlines()
        self.ProxyIpsCount += 1
        ipList = lines
        # ipList = res.text.split()
        ipsets = set(ipList)
        return ipsets, ipList

    def getFromXiCiDaili(self):
        dbop = xiciProxy("localhost", "root", "tw2016941017", "ProxyPool")
        ansList = dbop.getoneIpfromProxyPool()
        ansList = [x[0]+":"+x[1] for x in ansList]
        return set(ansList), ansList

    def checkHighLevel(self, ipProxy):
        try:
            res = requests.get("http://icanhazip.com", proxies={"http": ipProxy})
            if res.status_code == 200 and res.text.strip() != ipProxy.split(':')[0]:
                return True
            else:
                return False
        except:
            print "高匿检查出现异常!"
            return False
            pass
        pass

    def getRandomIp(self, hignLevel=False):
        # ipsets, ipList = self.getFromDaXiangDaili()
        ipsets, ipList = self.getFromXiCiDaili()
        usefulList = [x for x in ipList if self.checkIpuseful(x) != False]
        if hignLevel:
            usefulList = [x for x in usefulList if self.checkHighLevel(x)]
        print "usefulList长度", len(usefulList)
        if usefulList:
            self.pool = set(usefulList)
            return self.pool.pop()
        else:
            print "重新请求代理ip"
            return self.getRandomIp()
        pass

    def checkIpuseful(self, Proxyip=None):
        try:
            res = requests.get(self.testObjweb, proxies={"http": Proxyip}, headers=self.headers, timeout=5)
            if res.status_code == 200:
                return Proxyip
            # print res.text, res.status_code
            else:
                return False
        except Exception as e:
            print "pass"
            # print e
            # print traceback.format_exc()
            return False
        pass

class testProxymethds():

    def testOfRequests(self, proxy = "111.1.23.213:8080"):
        """ use Requests do the proxies' job"""
        print "requests"
        # proxyTmp = WaysOfUsingProxy(proxy, "http://httpbin.org/ip", 1)
        proxyTmp = WaysOfUsingProxy(proxy, "http://www.xicidaili.com/wn/239")
        pagetext, status = proxyTmp.WithRequests()
        print pagetext
        # time.sleep(3)
        pass

    def testOfUrllib2(self, proxy = "111.1.23.213:8080"):
        """ use urllib package do the proxies' job"""
        print "urllib"
        proxyTmp = WaysOfUsingProxy(proxy, "http://www.xicidaili.com/wn/239")
        print proxyTmp.WithUrllib2()
        # time.sleep(3)
        pass

    def testOfHttpclient(self, proxy = "111.1.23.213:8080"):
        """ use httplib package do the proxies' job"""
        print "httpclient"
        proxyTmp = WaysOfUsingProxy(proxy, "http://www.xicidaili.com/wn/239")
        textJson = proxyTmp.WithHttplib()
        print textJson
        import json
        tj = json.loads(textJson)
        print "json:",tj['origin']

        pass

if __name__ == '__main__':
    # with open("ProxyIps.txt", 'r')as rd:
    #     lines = rd.readlines()
    # # proxy = '218.106.205.145:8080'
    # for line in lines:
    #     proxy = line
    #     proxyTmp = WaysOfUsingProxy(proxy, "http://httpbin.org/ip")
    #     try:
    #         textJson = proxyTmp.WithHttplib()
    #     except:
    #         print "pass"
    #         continue
    #     print textJson


    # test = testProxymethds()
    # test.testOfRequests("120.194.253.44:81")


    # proxy = '218.106.205.145:8080'
    # proxyTmp = WaysOfUsingProxy(proxy, "http://www.xicidaili.com/wn/239")
    # proxyTmp.getFromDaXiangDaili()
    #


    # Gp = ProxyPool()
    # # print Gp.getFromDaXiangDaili()
    # print Gp.getRandomIp()


    # import UsefulProxyPool
    # tp = UsefulProxyPool.runningPool("localhost", "root", "tw2016941017", "ProxyPool", National=True, highLevel=True)
    # proxypool = tp.run()
    # tmpip = tp.getRandomIp()
    # res = requests.get("http://www.kuaidaili.com/free/inha/", proxies={"http": tmpip},  timeout=5)
    # if res.status_code == 200:
    #     print res.text
    # else:
    #     print "访问出错"
    pass









""" #####httpclient的用法
        # data = {
        #     'as_sdt': '0,5',
        #     'as_yhi': startYear,
        #     'as_ylo': endYear,
        #     'hl': 'en',
        #     'q': 'openstreetmap',
        #     'start': pageNum
        # }
        # data_encode = urllib.urlencode(data)
        # # print data_encode
        # aurl = 'http://scholar.google.com/scholar?' + data_encode
        # mcookie = '''
        #     NID=82=KpOZZ2CBQNKCtQiVCOq8dq8u-uTy5_vA3Rq0AGz4-oDoUjn030DaSKrC2o4FI_JSjoDU-_Ya8dsrgUyK1bCHLgqoUN9CpfCANVcTcFu_RMNZXKHBgyGyE4ibpOOSDdC4q5Ki7sHKJS6elrGoDec3zg
        #     ; GSP=LM=1468510570:S=lcfT3dr_eFiDDYmb
        # '''
        # headers = {
        #     'Host': 'scholar.google.com',
        #     'User-Agent': 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        #     'Accept-Language': 'en-US,en;q=0.5',
        #     'Connection': 'keep-alive',
        #     # 'Referer': 'http://scholar.google.com/scholar?q=openstreetmap&hl=en&as_sdt=0%2C5&as_ylo=2010&as_yhi=2011',
        #     'Cache-Control': 'max-age=0',
        #     # 'Accept-Encoding':'gzip, deflate'
        #     # 'Content-Length': len(data_encode),
        #     # 'Cookie': mcookie
        # }
        #
        # httpClient = None
        # page = ''
        # try:
        #     httpClient = httplib.HTTPConnection("scholar.google.com", 80, timeout=100)
        #     httpClient.request(method="GET", url=aurl, headers=headers)  # body=data_encode, headers=headers
        #     response = httpClient.getresponse()
        #     print '返回值:', response.read()
        #     print '状态:', response.status
        #     print '原因:', response.reason
        #     print '版本:', response.version
        #     # print response.read()
        #     print '头信息:', response.getheaders() # 获取头信息
        # except Exception, e:
        #     print '捕捉到错误！'
        #     print traceback.format_exc()
        #     print e
        # finally:
        #     if httpClient:
        #         httpClient.close()
        # # page = Selector(text=page)
        # # mlist = page.xpath('//a[@class="poi-tile__head"]/@href').extract()
        # # return mlist
        # pass
"""