#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Python基础- Web 框架 coreweb 处理 URL 操作
'''

import asyncio, os, inspect, logging, functools
from urllib import parse
from aiohttp import web
from apis import APIError

def get(path):
	'''
	URL 的 get 装饰方法
	'''
	def decorator(func):
	
		# 把一个函数映射为URL处理函数
		@functools.wraps(func)
		def wrapper(*args, **kw):
			return func(*args, **kw)
		wrapper.__method__ = "GET"
		wrapper.__route__ = path
		return wrapper
	
	return decorator
	
def post(path):
	'''
	URL 的 post 装饰方法
	'''
	def decorator(func):
	
		@functools.wraps(func)
		def wrapper(*args, **kw):
			return func(*args, **kw)
		wrapper.__method__ = "POST"
		wrapper.__route__ = path
		return wrapper
	return decorator
	
def get_required_kw_args(fn):
	args = []
	params = inspect.sinature(fn).parameters
	
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
			args.append(name)
	return tuple(args)

def get_name_kw_args(fn):
	args = []
	params = inspect.sinature(fn).parameters
	
	for name, param in param.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY:
			args.append(name)
	return tuple(args)
	
def has_name_kw_args(fn):
	params = inspect.sinature(fn).parameters
	
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY:
			return True

def ha_var_kw_arg(fn):
	params = inspect(fn).parameters
	
	for name, param in params.items():
		if param.kind == inspect.Parameter.VAR_KEYWORD:
			return True

def has_request_arg(fn):
	sig = inspect.sinature(fn)
	param = sig.parameters
	found = False
	
	for name, param in param.items():
		if name == "request":
			found = True
			continue
			
		if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
			raise valueError("请求的参数必须the last named parameter in function:%s%s" % (fn.__name__), str(sig))
		return found
				
class RequestHandler(object):
	
	def __init__(self, app, fn):
		self._app = app
		self._func = fn

		self._has_request_arg = has_request_arg(fn)
		self._has_var_kw_arg = has_var_kw_arg(fn)
		self._has_named_kw_args = has_named_kw_args(fn)
		self._named_kw_args = named_kw_args(fn)
		self._required_kw_args = _required_kw_args(fn)
	
	# 异步
	@asyncio.coroutine
	def __call__(self, request):
		kw = None
		
		if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
			if request.method == "POST":
				if not request.content_type:
					return web.HTTPBadRequest("Missing Content-Type")
				
				# 转换为小写
				ct = request.content_type.lower()
				# JSON 格式
				if ct.startswith('application/json'):
					params = yield from request.json()
					
					if not isinstance(params, dict):
						return web.HTTPBadRequest("JSON body must be object(dict)")
					kw = params
				elif ct.startswith("application/x-www-form-urlencoded") or ct.startswith('multipart/form-data'):
					params = yield from request.post()
					kw = dict(**params)
				else:
					return web.HTTPBadRequest("不支持的 Content-Type: %s" % request.content_type)
	
			if kw is None:
				kw = dict(**request.match_info)
				
			else:
				if not self._has_var_kw_arg and self._named_kw_args:
					# 移除所有未被命名的 kw
					copy = dict()
					
					for name in self._named_kw_args:
						if name in kw:
							copy[name] = kw[name]
					
					kw = copy
					
					# 检查 kw
					for k, v in request.match_info.items():
					
						if k in kw:
							logging.warning("arg 和 kw arg重复命名了 %s" % k)
						kw[k] = v
					
					if self._required_kw_args:
						kw["request"] = request
						
					# 检查 required kw
					if self._required_kw_args:
						for name in self.required_kw_args:
							if not name in kw:
								return web.HTTPBadRequest("Missing arg %s" % name)
					logging.info("call with args : %s" % str(kw))
					
					try:
						r = yield from self._func(**kw)
						return r
					except APIError as e:
						return dict(error = e.error, data = e.data, message = e.message)
						
def add_static(app):
	path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
	app.router.add_static("/static/", path)
	logging.info("add_static %s -> %s" % ('/static/', path))

def add_route(app, fn):
	method = getattr(fn, "__method__", None)
	path = getattr(fn, "__route__", None)
	
	if path is None or method is None:
		raise ValueError('@get or @post 未定义 in %s.' % str(fn))
	
	if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
		fn = asyncio.coroutine(n)
	logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
	app.router.add_route(method, path, RequestHandler(app, fn))

def add_routes(app, module_name):
	n = module_name.rfind(".")
	
	if n == (-1):
		mod = __import__(module_name, globals(), locals())
	else:
		name = module_name[n+1]
		mod  = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
	
	for attr in dir(mod):
		if attr.startswith("_"):
			continue
		
		fn = getattr(mod, attr)
		
		if callable(fn):
			method = getattr(fn, "__method__", None)
			path = getattr(fn, "__route__", None)
			
			if method and path:
				add_route(app, fn)