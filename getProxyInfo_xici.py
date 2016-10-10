# -*- coding:utf-8 -*-
__author__ = 'Tengwei'
from bs4 import BeautifulSoup
from xiciDbOps import xiciProxy
import requests
import datetime
import json
# import time
# import random

# 从网页提取的数据(utf8编码)无法正常显示
# 设置系统内部的编码为utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# firefox和chrome的伪装头
user_agent_list = {"firefox":"Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0}",
                   "chrome":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
                   }

class ParsePage():
    """ 解析XiCidaili网页数据, 提取代理ip的信息"""

    def __init__(self):
        # 西祠代理的url
        self.url = "http://www.xicidaili.com/nn/1"
        # 用于应对反爬虫的的请求头
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.xicidaili.com",
            "Referer": "http://www.xicidaili.com/nn",
            # "User-Agent": "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0}"
            "User-Agent": '''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)
            Chrome/41.0.2227.0 Safari/537.36'''
            }

    def getItemInfo(self, tag):
        """ 整理重组每条代理信息格式 """
        # 检查tag的内容???
        InfoList = []
        tdList = tag.find_all('td')
        try:                                       # 国家的图片src
            InfoList.append(tdList[0].img['src'])
        except:                                    # 国家属性可能为空
            InfoList.append('')
        InfoList.append(tdList[1].string)          # ip
        InfoList.append(tdList[2].string)          # port
        try:                                       # 代理所在地
            InfoList.append(tdList[3].a.string)
        except:                                    # 所在地可能为空
            InfoList.append('')
        InfoList.append(tdList[4].string)          # 匿名等级
        InfoList.append(tdList[5].string)          # 代理类别:HTTP, SOCKET...
        InfoList.append(tdList[6].div['title'])    # 通信速度
        InfoList.append(tdList[7].div['title'])    # 连接速度
        InfoList.append(tdList[8].string)          # 存活时间
        InfoList.append(tdList[9].string)          # 最近一次验证的时间
        # print InfoList[3]
        return InfoList


    def parseThePage(self, pageUrl, mode="normal"):
        """ 解析XiCi代理的网页,获取网页中的代理ip信息 """

        # 获取网页源码
        try:
            # 创建ip池需要大量访问网页, 所以最好用已有的代理
            if mode == "normal":
                res = requests.get(pageUrl, headers=self.headers, proxies=self.getProxy(), timeout=10)

            # 更新网页需要读取的页数比较少, 所以用自己的ip就好, 一般不会被封
            elif mode == "update":
                res = requests.get(pageUrl, headers=self.headers)
        except:
            # 处理返回gzip格式数据,直接退出重启, not known the reson,
            # 我都把headers当中的相关请求都删除了,尝试将返回类型要求成html,或文本形式
            print "获取网页失败!"
            self.writeBack(pageUrl)
            return False

        if res.status_code == 200:
            print '正在解析"' + pageUrl + '...'
            tmpText = res.text
            soup = BeautifulSoup(tmpText, 'html.parser')

            # 获得下一页的url
            try:
                nextUrl = "http://www.xicidaili.com" + soup.find('a', attrs={'class': "next_page"}).get('href')
            except AttributeError as ar:
                nextUrl = None

            # 获取每个代理ip的信息
            trlist = soup.find('table', attrs={"id": "ip_list"})
            trlist = trlist.find_all('tr')
            pageInfoList = []
            for child in trlist[1:]:        # 第一行是各列名称
                pageInfoList.append(self.getItemInfo(child))
            print '解析成功!'
            return (pageInfoList, nextUrl,)

        else:
            print '解析"' + pageUrl + '" 失败!'
            self.writeBack(pageUrl)
            return False

        pass

    def writeBack(self, data, keyStr='nextUrl'):
        """ 保存控制信息(到本地) """
        tmpdict = self.readfromsetup()
        if keyStr in tmpdict.keys():
            tmpdict[keyStr] = data
            with open('xiciSetup.txt', 'w') as wr:
                wr.write(json.dumps(tmpdict))
            return True
        else:
            print "写回失败...."
            return False
        pass

    def readfromsetup(self):
        """ 读取控制信息(从本地读) """
        with open('xiciSetup.txt') as rd:
            tmptext = json.loads(rd.read())
            return tmptext
        pass

    def initSetup(self, dbObj, poolName):
        """ 初始化本地配置文件:从数据库读取到本地,结束前写回数据库 """
        ConData = dbObj.getSetUpData(poolName)
        if ConData != False:
            tmpDict = {
                "poolName": ConData[0],
                "startUrl": ConData[1],
                "lastUpdate": str(ConData[2]),
                "nextUrl": ConData[3]
            }
            with open('xiciSetup.txt', 'w') as wr:
                wr.write(json.dumps(tmpDict))
            return True
        else:
            print "初始化配置文件失败..."
            return False
        pass

    def writebackSetup(self, dbObj, poolName, lastUpdate, nextUrl):
        """ 写配置信息到数据库 """
        return dbObj.writebackSetup(poolName, lastUpdate, nextUrl)
        pass

class CreateProxyPool(ParsePage):
    """ 创建代理池:爬取XiCi代理已有数据 """
    def __init__(self, SourcePath, User, Password, databaseName, poolName="XiCiProxyInfo"):
        self.dboperator = xiciProxy(SourcePath, User, Password, databaseName)   # 数据库操作对象
        ParsePage.__init__(self)                                                # 网页数据提取对象
        self.poolName = poolName                                                # 本地某一代理池名称
        ParsePage.initSetup(self, self.dboperator, self.poolName)               # 初始化本地配置文件

    def wirteBkToDb(self, pageUrl):
        """ 把配置信息写回数据库 """
        ParsePage.writebackSetup(self, self.dboperator, self.poolName, self.dboperator.getlastDate(self.poolName), pageUrl)
        pass

    def createThePool(self, pageUrl):
        """ 递归创建代理池 """
        flag = ParsePage.parseThePage(self, pageUrl, "update")
        if flag:
            pageInfoList = flag[0]  # 当前页所有ip信息的列表
            nextUrl = flag[1]       # 下一页的url
            if self.dboperator.InsertIpInfo(pageInfoList, self.poolName):
                if nextUrl != None:
                    # time.sleep(1 + random.randint(1, 10))  # 休息一下, 健康爬站...
                    self.writeBack(pageUrl)
                    return self.createThePool(nextUrl)
                else:
                    print "last page is done!"
                    self.wirteBkToDb(pageUrl)
                    return True
            else:
                print "插入数据失败!"
                self.wirteBkToDb(pageUrl)
                return False
        else:
            print "解析失败,返回重启..."
            self.wirteBkToDb(pageUrl)
            return False

    def run(self, mode='start'):
        """
        1. 实际运行创建程序
        2. 参数:
        mode:
        'start' 从 startUrl 开始
        'restart' 从 nextUrl 开始
        """
        try:
            if mode == 'start':
                return self.createThePool(self.readfromsetup()['startUrl'])
            elif mode == 'restart':
                return self.createThePool(self.readfromsetup()['nextUrl'])
            else:
                print "启动参数错误(start/restart)..."
                return False
        except:
            print "创建终止!"
            self.wirteBkToDb(self.readfromsetup()['nextUrl'])
            return False
        pass

class UpdateProxyPool(ParsePage):
    """ 更新指定代理池 """
    def __init__(self, SourcePath, User, Password, databaseName, poolName="XiCiProxyInfo"):
        # 数据库操作对象
        self.dboperator = xiciProxy(SourcePath, User, Password, databaseName)
        # 代理池名称
        self.poolName = poolName
        # 起始pool的控制信息
        self.controlInfo = self.dboperator.getControlInfo(poolName)
        # 网页数据提取对象
        ParsePage.__init__(self)
        # 初始化本地配置文件
        ParsePage.initSetup(self, self.dboperator, self.poolName)

    def filterInfo(self, checkdateStr, pageInfoList):
        """
        1.过滤提取的代理数据, 将上次更新提取国的代理ip舍弃
        2.判断更新是否结束: 由于XiCi代理的数据1分钟更新一次,所以代理数据都是按时间排序的, 若某一页出现已提取过的数据,
          则更新完本页后,更新结束
        """
        checkdate = datetime.datetime.strptime(checkdateStr, "%Y-%m-%d %H:%M:%S")
        ansList = []
        overFlag = False
        for info in pageInfoList:
            tmpdate = datetime.datetime.strptime(info[9], "%y-%m-%d %H:%M")
            if checkdate < tmpdate:
                ansList.append(info)
            else:
                overFlag = True
        return ansList, overFlag

    def wirteBkToDb(self, pageUrl):
        """ 把配置信息写回数据库 """
        ParsePage.writebackSetup(self, self.dboperator, self.poolName, self.dboperator.getlastDate(self.poolName), pageUrl)
        pass

    def UpdatePool(self, url="http://www.xicidaili.com/nn/1"):
        """ 递归爬取页面,更新西祠代理池数据 """
        # 获取控制信息
        setupInfo = ParsePage.readfromsetup(self)
        checkDate = setupInfo['lastUpdate']
        flag = ParsePage.parseThePage(self, url, "update")
        if flag:
            pageInfoList = flag[0]          # 当前页的所有代理ip的信息
            nextUrl = flag[1]               # 下一页的url
            ansList, overFlag = self.filterInfo(checkDate, pageInfoList)  # 筛选信息

            if ansList != []:
                if self.dboperator.InsertIpInfo(pageInfoList, self.poolName):
                    if overFlag == False:
                        self.UpdatePool(nextUrl)
                    else:
                        print "更新完毕!"
                        self.wirteBkToDb(url)
                        return True
                else:
                    print "更新数据时插入数据失败!"
                    self.wirteBkToDb(url)
                    return False
        else:
            print "解析失败,返回重启..."
            self.wirteBkToDb(url)
            return False
    pass

    def run(self):
        try:
            return self.UpdatePool(self.readfromsetup()['startUrl'])
        except:
            print "更新终止!"
            self.wirteBkToDb(self.readfromsetup()['nextUrl'])
            return False
        pass



    
# if __name__ == "__main__":
#     # tp = CreateProxyPool("localhost", "root", "tw2016941017", "ProxyPool", "XiCiNationalAnaymous")
#     # tp.run('restart')
#     # tp = UpdateProxyPool("localhost", "root", "tw2016941017", "ProxyPool", "XiCiNationalAnaymous")
#     # tp.run()
#
#     # tp = CreateProxyPool("localhost", "root", "tw2016941017", "ProxyPool", "XiCiWesternAnanymous")
#     # tp.run()
#     # tp.run('restart')
#     # tp = UpdateProxyPool("localhost", "root", "tw2016941017", "ProxyPool", "XiCiWesternAnanymous")
#     # tp.run()
#     pass