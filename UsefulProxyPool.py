# -*- coding:utf-8 -*-
__author__ = 'Tengwei'

import requests
import threading
from xiciDbOps import xiciProxy
from getProxyInfo_xici import UpdateProxyPool
import datetime
# import traceback

freshPool = set()           # 检测可用的代理池

class TestProxyIp(threading.Thread):
    """
        功能: 测试代理的有效性
    """

    def __init__(self, ipList=[], highLevel=True, timeout=10):
        threading.Thread.__init__(self)
        self.testObjweb = "http://icanhazip.com"            # 用于验证高匿代理的网站
        self.ipList = ipList                                # 用于测试的代理ip列表
        self.highLevel = highLevel                          # 是否需要验证高匿代理的标志
        self.timeout = timeout                              # 超时
        self.headers = {                                    # 伪装请求头
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "icanhazip.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0}"
            }


    def checkHighLevel(self, ipProxy):
        """ 检测代理ip是否是高匿代理 """
        try:
            res = requests.get("http://icanhazip.com", proxies={"http": 'http://' + ipProxy}, headers=self.headers)
            if res.status_code == 200 and res.text.strip() == ipProxy.split(':')[0]:
                return True
            else:
                return False
        except:
            print "高匿检查出现异常!"
            return False
            pass
        pass


    def checkIpuseful(self, Proxyip=None, timeout=5):
        """ 检测代理ip是否有效 """
        try:
            res = requests.get(self.testObjweb, proxies={"http": 'http://' + Proxyip}, headers=self.headers, timeout=timeout)
            if res.status_code == 200:                                                  # 正常返回,代理有效
                if self.highLevel and res.text.strip() != Proxyip.split(':')[0]:        # 检测高匿代理
                    print "pass: not high level"
                    return False
                print 'get'
                return Proxyip
            # print res.text, res.status_code
            else:
                print 'pass'
                return False
        except Exception as e:
            print "timeout"
            # print e
            # print traceback.format_exc()
            return False
        pass
    pass

    def run(self):
        global freshPool
        usefulList = [x for x in self.ipList if self.checkIpuseful(x, self.timeout) != False]
        print "usefulList长度", len(usefulList)
        freshPool |= set(usefulList)
        return set(usefulList)  # 这里的返回值可以省略




class runningPool():
    """ 维护1个本地的有效的代理IP池 """
    # 确定一下使用哪几个库!!!!!!!这里的设计有问题
    def __init__(self, SourcePath, User, Password, databaseName, National=True, highLevel=True, timeout=10):
        """
            代理库的扩展:
                根据National 和 highLevel 决定从self.poolNames选出相应的表, 设置self.poolUpdateList
                注意:
                1.所有其他站的代理信息格式化为西祠代理的格式, 方便在数据库对象的操作
                2.所有其他站的表都存储在ProxyPool数据库中, 且都要使用CONTROLINFO表
        """
        self.dbop = xiciProxy(SourcePath, User, Password, databaseName)     # 数据库操作对象
        self.testObj = TestProxyIp()                                        # 用于测试代理ip的对象
        self.pool = set()                                                   # 实际有效的代理池
        self.timeout = 10                                                   # 超时
        self.poolUpdate = UpdateProxyPool(SourcePath, User, Password, databaseName, "XiCiNationalAnaymous")
        # self.poolNames = {                                                  # 所有代理池数据库名称的集合(暂时为空...)
        #                   "NA": ["XiCiNationalAnaymous"],
        #                   "WA": ["XiCiWesternAnanymous"]
        #                   }
        # self.poolUpdateList = [] (替换掉self.poolUpdate) 用于代理库的扩展
        pass

    # 这里的poolName设计有问题...
    # 答: 按照self.poolNames 确定的表进行提取
    def getFromProxyPool(self, poolName="XiCiNationalAnaymous", timeRange=2):
        """ 从已经建立好的代理的数据库中选取最新的代理ip
            # 扩展操作:
            # 先更新数据库
            # for i in self.poolUpdateList:
            #     i.run()
            # 再逐个提取代理数据
            # for i in self.runningPoolNames:
            #     ansList.append(self.dbop.getFreshIpfromProxyPool(poolName=poolName, timeRange=timeRange))
            # ansList = [x[0]+":"+x[1] for x in ansList]
            # return set(ansList), ansList
        """
        # 先更新数据库
        self.poolUpdate.run()
        # 再提取代理数据
        ansList = self.dbop.getFreshIpfromProxyPool(poolName=poolName, timeRange=timeRange)
        ansList = [x[0]+":"+x[1] for x in ansList]
        return set(ansList), ansList


    def getUsefulIpPool(self, timeRange=2):
        """ 单线程获取有效代理 """
        # ipsets, ipList = self.getFromDaXiangDaili()
        ipsets, ipList = self.getFromProxyPool(timeRange=timeRange)
        usefulList = [x for x in ipList if self.testObj.checkIpuseful(x, self.timeout) != False]
        print "usefulList长度", len(usefulList)
        if usefulList:
            self.pool = set(usefulList)
            # return self.pool.pop()
            return self.pool
        else:
            print "重新请求代理ip"
            return self.getUsefulIpPool()
        pass
    pass

    def multiProcessTest(self, processorNum=2, timeRange=2):
        """
         功能:
            多线程获取有效代理
         参数:
            processorNum : 多线程的个数
            timeRange: 时间范围, 指定选取的代理ip的范围
        """
        ipsets, ipList = self.getFromProxyPool(timeRange=timeRange)     # 获取代理信息
        threads = []
        lenIpList = len(ipList)                                         # 待测试的代理总数
        if processorNum > lenIpList or processorNum <= 0:               # 线程总数指定不合理的情况
            processorNum = lenIpList
        length = lenIpList / processorNum                               # 每个线程要测试的ip个数
        # length = (lenIpList / processorNum) if processorNum > lenIpList else 1   # 步长:每个线程验证的ip个数
        newPoint = 0
        for i in range(processorNum):       # 将待测代理分配给线程
            oldPoint = newPoint
            newPoint += length
            if newPoint <= lenIpList:
                threads.append(TestProxyIp(ipList[oldPoint:newPoint], timeout=self.timeout))
            elif oldPoint < lenIpList:
                threads.append(TestProxyIp(ipList[oldPoint:], timeout=self.timeout))

        for i in range(len(threads)):       # 启动线程
            threads[i].start()
        for i in range(len(threads)):       # 阻塞进程直到线程执行完毕(原理就是依次检验线程池中的线程是否结束，没有结束就阻塞
            threads[i].join()               # 直到线程结束，如果结束则跳转执行下一个线程的join函数。)

        global freshPool
        self.pool = freshPool               # 等到线程全部执行结束, 将有效代理池赋值给当前对象的代理池, 供外部访问
        pass

    def getRandomIp(self):
        """ 获取有效代理集合中的一个ip """
        if len(self.pool):
            return self.pool.pop()
        else:
            print "集合为空!"
            return False
        pass

    def run(self, mode='M', multiNum=10, timeRange=2880):
        """
        功能:
            实际执行控制
        参数
        mode:
            'M': 指定使用多线程
            'S'(或其他): 指定使用单线程
        multiNum:
            指定多线程的个数
        timeRange:
            时间范围, 指定选取的代理ip的范围
        """
        starttime = datetime.datetime.now()
        if mode == 'M':
            # 多线程测试
            self.multiProcessTest(multiNum, timeRange=timeRange)
        else:
            # 单线程测试
            self.getUsefulIpPool(timeRange=timeRange)
        endTime = datetime.datetime.now()
        print "耗时:", (endTime - starttime)
        pass

if __name__ == "__main__":
    # 单线程测试
    # starttime = datetime.datetime.now()
    # tp = runningPool("localhost", "root", "tw2016941017", "ProxyPool")
    # print tp.getUsefulIpPool()
    # endTime = datetime.datetime.now()
    # print (endTime - starttime)

    # 多线程测试
    # starttime = datetime.datetime.now()
    # tp = runningPool("localhost", "root", "tw2016941017", "ProxyPool")
    # tp.multiProcessTest(20)
    # endTime = datetime.datetime.now()
    # print (endTime - starttime)
    # print "获得的代理集合:", freshPool

    # 定义操作对象
    tp = runningPool("localhost", "root", "tw2016941017", "ProxyPool", National=True, highLevel=True, timeout=10)
    # 多线程
    tp.run()
    print tp.pool
    # 单线程
    # tp.run('S')


    pass