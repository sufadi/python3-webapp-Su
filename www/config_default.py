#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python基础- 配置文件[开发环境的标准配置]

'''
缺省配置
'''

configs = {
	'debug': True,
	'database': {
		'host':"127.0.0.1",
		"port":3306,
		"user": "root",
		"password":"",
		"database":"sufadi"
	},
	"session":{
		"secret": "sufadi"
	}
}