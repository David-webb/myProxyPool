# 代理池

## 功能说明
	提供实时验证可用的高匿代理

## 接口(python)
1. 模块介绍:
	+ 名称: UsefulProxyPool
	+ 导入: from UsefulProxyPool import runningPool
	+ 使用:

			tp = runningPool(
			SourcePath, 		# 数据库所在主机的ip
			User, 			# 数据库用户名
			Password,		# 数据库密码
			databaseName, 		# 数据库名称(可省, 程序指定为ProxyPool2)
			National=True, 		# 国内代理的标志
			highLevel=True, 		# 高匿代理的标志
			timeout=10)		# 超时设置
			)

			tp.run(
			mode='M', 		# 验证模式:单线程('S') / 多线程('M')
			multiNum=10, 		# 多线程模式下, 设置多线程的个数, 默认: 10个
			timeRange=2880	# 指定提取该时间范围内代理, 单位:分钟, 默认: 2880 分钟(两天内)
			)

			print tp.pool        	# 提取到的代理ip池, 集合(set)类型


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


