# -*- coding:utf-8 -*-
__author__ = 'Tengwei'
import MySQLdb
import traceback
import datetime

class xiciProxy():
    def __init__(self, SourcePath, User, Password, databaseName="ProxyPool"):
        self.databaseName = "ProxyPool"
        self.db = MySQLdb.connect(SourcePath, User, Password, charset='utf8')
        self.cursor = self.db.cursor()
        if databaseName != self.databaseName:
            print "数据库名称固定为:" + self.databaseName + "..."
        try:
            self.cursor.execute('use' + ' ' + self.databaseName)
        except:
            self.initProxyPoolDatabase()
        pass

    def __del__(self):
        """ 析构函数 """
        self.cursor.close()
        self.db.commit()
        pass

    def isDatabaseReady(self):
        """ 判断数据库是否准备好 """
        sql = 'show databases'
        self.cursor.execute(sql)
        dbList = [x[0] for x in self.cursor.fetchall()]
        return True if self.databaseName in dbList else False

    def initControlTable(self):
        """ 初始化数据库控制表 """
        ConList = [
            ['XiCiNationalAnaymous', 'http://www.xicidaili.com/nn/1', 'http://www.xicidaili.com/nn/1'],
            ['XiCiWesternAnanymous', 'http://www.xicidaili.com/wn/1', 'http://www.xicidaili.com/wn/1']
        ]
        sql = 'INSERT IGNORE INTO CONTROLINFO(poolName, startUrl, nextUrl) VALUE(%s, %s, %s)'
        try:
            self.cursor.executemany(sql, ConList)
            self.db.commit()
            return True
        except:
            print "初始化控制信息表失败!"
            self.db.rollback()
            return False
        pass

    def initProxyPoolDatabase(self):
        """ 初始化数据库 """
        print "初始化数据库..."
        # 创建数据库
        self.cursor.execute('CREATE DATABASE IF NOT EXISTS' + ' ' + self.databaseName)
        self.cursor.execute('use' + ' ' + self.databaseName)
        # 创建XA, WA, CONTROLINFO 三张表
        tableList = ['XiCiNationalAnaymous', 'XiCiWesternAnanymous', 'controlTable', 'usefulProxyPool']
        for i in tableList:
            self.CreateTable(i)
        self.initControlTable()
        pass

    def CreateTable(self, TableName='XiCiProxyInfo'):
        # url_table
        sql = ''
        TablenameList = ['XiCiProxyInfo', 'XiCiNationalAnaymous', 'XiCiNationalTransparent', 'XiCiWesternAnanymous', 'XiCiWesternTransparent', 'XiCiSOCKET']
        if TableName in TablenameList:
            sql = """CREATE TABLE IF NOT EXISTS""" + " " + TableName + """(
                countryName varchar(100),
                ipAddr varchar(50),
                port varchar(20),
                hostAddr varchar(100),
                anonymousLevel varchar(20),
                Type varchar(20),
                transSpeed varchar(20),
                getConecTime varchar(20),
                survialTime varchar(20),
                lastTest datetime,
                primary key(ipAddr, lastTest)
            )default charset=utf8;
            """
        elif TableName == "controlTable":
            nowTime = str(datetime.date.today()-datetime.timedelta(weeks=1))
            sql = """CREATE TABLE IF NOT EXISTS CONTROLINFO(
            poolName varchar(50) primary key,
            startUrl varchar(200),
            lastUpdate datetime default""" + ' ' + '"' + nowTime + '", ' + """
            nextUrl varchar(200)
            )default charset=utf8;
            """
        elif TableName == "usefulProxyPool":
            sql = """CREATE TABLE IF NOT EXISTS USEFULPROXY(
            ipAddr varchar(50),
            lastTest datetime,
            primary key(ipAddr, lastTest)
            )default charset=utf8;
            """
            pass
        else:
            print "参数错误!"
            return False

        try:
            # print sql
            self.cursor.execute("DROP TABLE IF EXISTS " + TableName)
            self.cursor.execute(sql)
            self.db.commit()
        except:
            print '创建表格' + TableName + '失败！\n'
            print traceback.format_exc()
            self.db.rollback()


    def InsertIpInfo(self, urlList, TableName='XiCiProxyInfo'):
        sql = "INSERT IGNORE INTO" + " " + TableName + " " + "value(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"        # 占位符用%s没有问题, IGNORE根据ID查重
        pass
        try:
            self.cursor.executemany(sql, urlList)
            self.db.commit()
            return True
        except Exception as e:
            print e
            print traceback.format_exc()
            print '插入失败！\n'
            self.db.rollback()
            return False
        pass


    def InsertUsefulIp(self, urlList, TableName='USEFULPROXY'):
        sql = "INSERT IGNORE INTO" + " " + TableName + " " + "values(%s, %s)"        # 占位符用%s没有问题, IGNORE根据ID查重       
        print sql
        try:
            self.cursor.executemany(sql, urlList)
            self.db.commit()
            return True
        except Exception as e:
            print e
            print traceback.format_exc()
            print '插入失败！\n'
            self.db.rollback()
            return False
        pass

    def getlastDate(self, TableName="XiCiProxyInfo"):
        sql = "select max(lastTest) from" + " " + TableName + ";"
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()[0]
        except:
            print traceback.format_exc()
            print '获取最新日期失败...'
            return False
        pass

    def getSetUpData(self, poolName="XiCiProxyInfo"):
        sql = 'select * from CONTROLINFO where poolName=' + '"' + poolName + '";'
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except:
            print traceback.format_exc()
            print '获取控制信息失败...'
            return False
        pass

    def writebackSetup(self, poolName, lastUpdate, nextUrl):
        sql = 'update CONTROLINFO set lastUpdate="' + str(lastUpdate) + '", nextUrl="' + str(nextUrl) +\
              '" where poolName="' + str(poolName) + '";'
        # print sql
        try:
            self.cursor.execute(sql)
            self.db.commit()
            print "配置信息写回成功!"
            return True
        except:
            print traceback.format_exc()
            print "写回信息失败!"
            return False
        pass

    def getControlInfo(self, poolName="XiCiProxyInfo"):
        sql = 'select * from CONTROLINFO where poolName=' + '"' + poolName + '";'
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except:
            print traceback.format_exc()
            print '获取控制信息失败...'
            return False
        pass

    def clsOutofdateIp(self, lifeTime):
        """
            清除过期的有效ip数据库条目
        """
        # timeOfNow = self.getlastDate(poolName) - datetime.timedelta(minutes=lifeTime)
        # sql = 'select ipAddr, port, Type from' + ' ' + poolName + ' ' + 'where lastTest >' + ' "' + str(timeOfNow) \
        #       + '" ' + 'group by ipAddr;'
        # sql = ""

    def getFreshIpfromProxyPool(self, poolName="XiCiProxyInfo", timeRange=2):
        """
            功能:
                从指定的代理池中提取出最新的代理ip
            参数:
                poolName: 指定的代理池的名称
                timeRange: 时间域,指选取距离最新更新时间(lastTest)的前timeRange分钟内更新的所有ip
        """
        # timeOfNow = str(datetime.date.today())
        timeOfNow = self.getlastDate(poolName) - datetime.timedelta(minutes=timeRange)
        sql = 'select ipAddr, port, Type, lastTest from' + ' ' + poolName + ' ' + 'where lastTest >' + ' "' + str(timeOfNow) \
              + '" ' + 'group by ipAddr;'
        # print sql
        try:
            self.cursor.execute(sql)
            tmpTuple = self.cursor.fetchall()
            # print tmpTuple
            # self.indexCount += 1
            # return tmpTuple[self.indexCount % len(tmpTuple)]
            # mindex = random.randint(0, len(tmpTuple))
            # print mindex
            return tmpTuple
        except:
            print "从ip池获取代理ip失败!"
            print traceback.format_exc()
            return False
            pass

if __name__ == '__main__':
    #import requests
    #res = requests.get('https://www.baidu.com', proxies={'http': 'http://115.59.69.59:808'})
    #print res.status_code
    #print res.text

    import datetime
    tmpobj = xiciProxy("localhost", "root", "tw2016941017", "ProxyPool")
    tmplist = list(set([(u'111.76.133.16:808', datetime.datetime(2017, 1, 26, 20, 43)), (u'36.249.192.240:8118', datetime.datetime(2017, 1, 26, 20, 10)), (u'117.79.93.39:8808', datetime.datetime(2017, 1, 25, 18, 31)), (u'61.159.12.31:8118', datetime.datetime(2017, 1, 26, 20, 42)), (u'60.13.74.211:80', datetime.datetime(2017, 1, 26, 21, 10)), (u'60.169.78.218:808', datetime.datetime(2017, 1, 26, 2, 46))]))
    tmplist = [[x[0], str(x[1])] for x in tmplist]
    print tmplist
    tmpobj.InsertUsefulIp(tmplist)
    
    pass
