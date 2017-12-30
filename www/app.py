#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python基础-Web App 骨架

import logging; logging.basicConfig(level = logging.INFO)

import asyncio, os, json, time
from datetime import datetime

import orm
from aiohttp import web
from coreweb import add_routes, add_static
from jinja2 import Environment, FileSystemLoader

def init_jinja2(app, **kw):
	logging.info("初始化 jinja2")
	options = dict(
		autoescape = kw.get("autoescape ", True),
		block_start_string = kw.get("block_start_string","{%"),
		block_end_string = kw.get("block_end_string", "%}"),
		variable_start_string = kw.get("variable_start_string", '{{'),
		variable_end_string = kw.get("variable_end_string", '}}'),
		auto_reload = kw.get("auto_reload", True)
	)

	path = kw.get("path", None)
	if path is None:
		# templates文件夹 放置 html 文件
		path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
	logging.info("设置 jinja2 templates 地址为 %s" % path)

	env = Environment(loader = FileSystemLoader(path), **options)
	filters = kw.get("filters", None)
	
	if filters is not None:
		for name, f in  filters.items():
			env.filters[name] = f
	
	app['__templating__'] = env

def datetime_filter(t):
	# 时间差
	delta = int(time.time() - t)
	
	if delta < 60:
		return u'1分钟前'
	if delta < 3600:
		return u'%s分钟前' % (delta // 60)
	if delta < 86400:
		return u'%s小时前' % (delta // 3600)
	if delta < 604800:
		return u'%s天前' % (delta // 86400)
	
	dt = datetime.fromtimestamp(t)
	return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)

def index(request):
	# 网页显示 Web App
	return web.Response(body = b"Web App")

@asyncio.coroutine
def init(loop):
	yield from orm.create_pool(loop = loop, host = "127.0.0.1", port = 9000, user = "root", password = "", database = "sufadi")

	#创建一个web服务器对象
	app = web.Application(loop = loop)
	#通过router的指定的方法可以把请求的链接和对应的处理函数关联在一起
	init_jinja2(app, filters=dict(datetime = datetime_filter))
	add_routes(app, "handlers")
	add_static(app)
	#运行web服务器,服务器启动后,有用户在浏览器访问,就可以做出对应的响应
	# 127.0.0.1 本机地址
	srv = yield from loop.create_server(app.make_handler(), "127.0.0.1", 9000)
	logging.info("服务端 http://127.0.0.1:9000....")
	return srv

# 固定写法
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
#loop.run_forever()