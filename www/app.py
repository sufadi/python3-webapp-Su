#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python基础-Web App 骨架

import logging; logging.basicConfig(level = logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web

def index(request):
	# 网页显示 Web App
	return web.Response(body = b"Web App")

@asyncio.coroutine
def init(loop):
	#创建一个web服务器对象
	app = web.Application(loop = loop)
	#通过router的指定的方法可以把请求的链接和对应的处理函数关联在一起
	app.router.add_route("GET", "/", index)
	#运行web服务器,服务器启动后,有用户在浏览器访问,就可以做出对应的响应
	# 127.0.0.1 本机地址
	srv = yield from loop.create_server(app.make_handler(), "127.0.0.1", 9000)
	logging.info("服务端 http://127.0.0.1:9000....")
	return srv

# 固定写法
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()