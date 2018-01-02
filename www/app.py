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
from model import User, Blog, Comment

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

@asyncio.coroutine
def logger_factory(app, handler):

	@asyncio.coroutine
	def logger(request):
		logging.info('Request: %s %s' % (request.method, request.path))
		return (yield from handler(request))
	return logger

@asyncio.coroutine
def data_factory(app, handler):

	@asyncio.coroutine
	def parse_data(request):
		if request.method == 'POST':
			if request.content_type.startswith('application/json'):
				request.__data__ = yield from request.json()
				logging.info('request json: %s' % str(request.__data__))
			elif request.content_type.startswith('application/x-www-form-urlencoded'):
				request.__data__ = yield from request.post()
				logging.info('request form: %s' % str(request.__data__))

		return (yield from handler(request))
	return parse_data

@asyncio.coroutine
def response_factory(app, handler):

	@asyncio.coroutine
	def response(request):
		logging.info('Response handler...')
		r = yield from handler(request)
		if isinstance(r, web.StreamResponse):
			return r

		if isinstance(r, bytes):
			resp = web.Response(body=r)
			resp.content_type = 'application/octet-stream'
			return resp

		if isinstance(r, str):
			if r.startswith('redirect:'):
				return web.HTTPFound(r[9:])

			resp = web.Response(body=r.encode('utf-8'))
			resp.content_type = 'text/html;charset=utf-8'
			return resp

		if isinstance(r, dict):
			template = r.get('__template__')
			if template is None:
				resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
				resp.content_type = 'application/json;charset=utf-8'
				return resp
			else:
				resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
				resp.content_type = 'text/html;charset=utf-8'
				return resp

		if isinstance(r, int) and r >= 100 and r < 600:
			return web.Response(r)
		if isinstance(r, tuple) and len(r) == 2:
			t, m = r
			if isinstance(t, int) and t >= 100 and t < 600:
				return web.Response(t, str(m))
		# default:
		resp = web.Response(body=str(r).encode('utf-8'))
		resp.content_type = 'text/plain;charset=utf-8'
		return resp
	return response

@asyncio.coroutine
def init(loop):
	yield from orm.create_pool(loop = loop, host = "127.0.0.1", port = 3306, user = "root", password = "", database = "sufadi")

	u = User(name = "Test", email = "test@sufadi.com", passwd = "123")
	u.save()

	#创建一个web服务器对象
	app = web.Application(loop=loop, middlewares=[
		logger_factory, response_factory
    ])

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
loop.run_forever()