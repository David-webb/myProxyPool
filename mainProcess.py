# -*- coding:utf-8 -*-
__author__ = "TengWei"

import threading
import time
import os

# instance 2
class Timer(threading.Thread):
    def __init__(self, fn, args=(), sleep=0, lastDo=True):
        threading.Thread.__init__(self)
        self.args = args       # 定时器定时执行的操作的参数
        self.sleep = sleep     # 计时的时间
        self.lastDo = lastDo   # 定时器生命周期结束时执行操作标志
        self.setDaemon(True)   # 设置子线程与主线程一起结束
        self.fn = fn
        self.isPlay = True
        self.fnPlay = False

    def __do(self):
        self.fnPlay = True
        apply(self.fn, self.args)
        self.fnPlay = False

    def getisPlay(self):
        """
            用作交互式终止程序脚本调用，也可以直接用ctrl+c终止运行
        """
        with open('Timersettings.txt', 'r') as rd:
            rd.read()
        pass

    def run(self):
        while self.isPlay:
            self.__do()
            time.sleep(self.sleep)


    def stop(self):
        # stop the loop
        self.isPlay = False
        while True:
            if not self.fnPlay: break
            time.sleep(0.01)
        # if lastDo, di it again
        if self.lastDo:
            self.__do()


def easyprint(Msg):
    print Msg

def runproxypool():
    os.system("python UsefulProxyPool.py")    

if __name__ == '__main__':
    t = Timer(runproxypool, sleep=60)
    t.run()
    
    #import  datetime
    #tmpset = set([(u'111.76.133.16:808', datetime.datetime(2017, 1, 26, 20, 43)), (u'36.249.192.240:8118', datetime.datetime(2017, 1, 26, 20, 10)), (u'117.79.93.39:8808', datetime.datetime(2017, 1, 25, 18, 31)), (u'61.159.12.31:8118', datetime.datetime(2017, 1, 26, 20, 42)), (u'60.13.74.211:80', datetime.datetime(2017, 1, 26, 21, 10)), (u'60.169.78.218:808', datetime.datetime(2017, 1, 26, 2, 46))])
    #print list(tmpset)

    pass
