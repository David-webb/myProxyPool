# 代理池

## 功能说明
	提供实时验证可用的高匿代理

## 接口(python)
1. 模块介绍:
	+ 名称: UsefulProxyPool
	+ 导入: from mainProcess import *
 	+ 使用:

			tp = Timer_ProxyPool(
			Host, 			# 数据库所在主机的ip
			User, 			# 数据库用户名
			Password,		# 数据库密码
			databaseName, 		# 数据库名称(可省, 程序指定为ProxyPool2)
			National=True, 		# 国内代理的标志
			highLevel=True, 	# 高匿代理的标志
			timeout=10)		# 超时设置
			)

			tp.getOneProxyIp()	# 从数据库获取一个ip
						# 返回值是字符串，直接用

## 安装说明
1. 系统环境:
	+ ubuntu 14.04
	+ 需要本地安装mysql数据库(开发使用的版本为: 5.5.47)
                  版本信息: mysql  Ver 14.14 Distrib 5.5.47, for debian-linux-gnu (x86_64) using readline 6.3)       
2. 安装流程:
	+ 将项目clone到本地后. 命令行进入目录
	+ 运行以下命令:

	 		python setup.py sdist 
			sudo python setup.py install  --record files.txt
			(record 前是两个连续-)

3. 卸载安装包:
	+ 进入项目主目录,运行以下命令:

			sudo cat files.txt | sudo  xargs rm -rf

4. 注意:
***mysql装好后, 可以直接按照接口调用说明, 在程序中调用, 程序会自动创建数据库和相关表, 并初始化相关数据, 数据库固定使用名为ProxyPool2, 如有重名, 不会更改原来的数据, 但无法使用系统(待改进)***

5. 后续开发:
	+ 添加更多的提取源, 能够同时提供更多的代理
	+ 提供国外的高匿代理
	+ 分布式的验证，提高验证效率，保证验证数量
	+ 安装包的标准化和接口结构的优化
6. 使用实例参考
	+ 参考库中的NGACSpider（多线程使用代理的版本）
