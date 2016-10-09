# -*- coding:utf-8 -*-
__author__ = 'Tengwei'
import MySQLdb
import traceback
import datetime
# import random

class xiciProxy():
    def __init__(self, SourcePath, User, Password, databaseName="ProxyPool2"):
        self.databaseName = "ProxyPool2"
        self.db = MySQLdb.connect(SourcePath, User, Password, charset='utf8')
        self.cursor = self.db.cursor()
        if databaseName != self.databaseName:
            print "数据库名称固定为:ProxyPool..."
        try:
            self.cursor.execute('use' + ' ' + self.databaseName)
        except:
            self.initProxyPoolDatabase()
        # if self.isDatabaseReady():
        #     print "数据库已准备好..."
        #     self.cursor.execute('use ProxyPool2')
        # else:
        #     self.initProxyPoolDatabase()
        pass

    def __del__(self):
        self.cursor.close()
        self.db.commit()
        pass

    def isDatabaseReady(self):
        sql = 'show databases'
        self.cursor.execute(sql)
        dbList = [x[0] for x in self.cursor.fetchall()]
        return True if self.databaseName in dbList else False

    def initProxyPoolDatabase(self):
        """ 初始化数据库 """
        print "初始化数据库..."
        # 创建数据库
        self.cursor.execute('CREATE DATABASE IF NOT EXISTS' + ' ' + self.databaseName)
        self.cursor.execute('use' + ' ' + self.databaseName)
        # 创建XA, WA, CONTROLINFO 三张表
        tableList = ['XiCiNationalAnaymous', 'XiCiWesternAnanymous', 'controlTable']
        for i in tableList:
            self.CreateTable(i)
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
            lastUpdate datetime default""" + '"' + nowTime + '", ' + """
            nextUrl varchar(200)
            )default charset=utf8;
            """
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
        sql = 'select ipAddr, port, Type from' + ' ' + poolName + ' ' + 'where lastTest >' + ' "' + str(timeOfNow) \
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
    # tp = xiciProxy("localhost", "root", "tw2016941017", "ProxyPool")
    # tp.CreateTable()
    # sql = 'select * from XiCiProxyInfo limit 1;'
    # tp.cursor.execute(sql)
    # tmpstr = tp.cursor.fetchone()[9]
    # import datetime
    # t1 = datetime.datetime.strptime("16-08-29 16:02", "%y-%m-%d %H:%M")  # 16-08-29 16:02
    # t2 = datetime.datetime.strptime("16-09-29 16:02", "%y-%m-%d %H:%M")  # 16-08-29 16:02
    # print t2 - t1

    # import datetime
    # print datetime.datetime.now()
    # print tp.getoneIpProxy(datetime.datetime.now())
    # print tp.getoneIpfromProxyPool()
    # for i in ['XiCiNationalTransparent', 'XiCiWesternAnanymous', 'XiCiWesternTransparent', 'XiCiSOCKET']:
    #     tp.CreateTable(i)

    # tp.CreateTable('XiCiNationalAnaymous')

    # print tp.getControlInfo()
    # print tp.getlastDate()
    # tp.writebackSetup("", "", "")
    # print tp.getSetUpData()
    # tp.writebackSetup("XiCiProxyInfo", tp.getlastDate(), "http://www.xicidaili.com/nn/2")

    # print tp.getFreshIpfromProxyPool("XiCiNationalAnaymous", 1)

    # tp = xiciProxy("localhost", "root", "tw2016941017", "ququDB")
    # tp.CreateTable('controlTable')

    # milliseconds, microseconds, seconds, minutes, hours, days(默认), weeks
    # timeOfNow = tp.getlastDate("XiCiNationalAnaymous") - datetime.timedelta(weeks=1440)
    # print timeOfNow

    # try:
    #     db = MySQLdb.connect("localhost", "root", "tw2016941017", charset='utf8')
    # except:
    #     print traceback.format_exc()
    # cur = db.cursor()
    # cur.execute('show databases;')
    # cur.execute('create database testDb')
    # cur.execute('drop database testDb')
    # print cur.fetchall()

    tp = xiciProxy("localhost", "root", "tw2016941017")
    # print tp.isDatabaseReady()

    pass
