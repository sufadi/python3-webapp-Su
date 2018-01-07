#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Python基础- Web 框架 coreweb 处理 URL 操作
'''

import asyncio
import os
import inspect
import logging
import functools
from urllib import parse
from aiohttp import web
from apis import APIError


def get(path):
    '''
    Define decorator @get('/path')
    '''
    def decorator(func):

        # 把一个函数映射为URL处理函数
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = "GET"
        wrapper.__route__ = path
        logging.info("get : %s" % path)
        return wrapper

    return decorator


def post(path):
    '''
    Define decorator @post('/path')
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
    params = inspect.signature(fn).parameters

    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)


def get_named_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters

    for name, param in params.items():
        logging.info("get_named_kw_args : name = %s, param = %s, kind = %s" % (
            name, param, param.kind))
        # 分别是POSITIONAL_ONLY、VAR_POSITIONAL、KEYWORD_ONLY、VAR_KEYWORD、POSITIONAL_OR_KEYWORD
        # 分别是位置参数�?�可变参数�?�命名关键字参数、关键字参数，最后一个是位置参数或命名关键字参数
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)


def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters

    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True


def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters

    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True


def has_request_arg(fn):
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    logging.info("has_request_arg : sig = %s, params = %s" % (sig, params))

    for name, param in params.items():
        if name == "request":
            found = True
            continue

        logging.info("has_request_arg : param.kind = %s" % param.kind)

        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError(
                "请求的参数必须the last named parameter in function:%s%s" % (fn.__name__), str(sig))

        logging.info("has_request_arg : found = %s" % found)
        return found


class RequestHandler(object):

    def __init__(self, app, fn):
        self._app = app
        self._func = fn

        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)
        logging.info("RequestHandler : _app = %s" % self._app)
        logging.info("RequestHandler : _func = %s" % self._func)
        logging.info("RequestHandler : _has_request_arg = %s" %
                     self._has_request_arg)
        logging.info("RequestHandler : _has_var_kw_arg = %s" %
                     self._has_var_kw_arg)
        logging.info("RequestHandler : _has_named_kw_args = %s" %
                     self._has_named_kw_args)
        #logging.info("RequestHandler : _named_kw_args = %s" % self._named_kw_args)
        #logging.info("RequestHandler : _required_kw_args = %s" % self._required_kw_args)

    # 异步
    async def __call__(self, request):
        logging.info("RequestHandler : __call__ = %s" % request)
        logging.info("RequestHandler : __call__ method = %s" % request.method)

        kw = None

        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            if request.method == "POST":
                if not request.content_type:
                    return web.HTTPBadRequest("Missing Content-Type")

                # 转换为小�?
                ct = request.content_type.lower()
                # JSON 格式
                if ct.startswith('application/json'):
                    params = await request.json()

                    if not isinstance(params, dict):
                        return web.HTTPBadRequest("JSON body must be object(dict)")
                    kw = params
                elif ct.startswith("application/x-www-form-urlencoded") or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest("不支持的 Content-Type: %s" % request.content_type)

            if request.method == 'GET':
                qs = request.query_string
                logging.info("request.method = get : %s" %
                             request.query_string)
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
            if kw is None:
                kw = dict(**request.match_info)

        else:
            if not self._has_var_kw_arg and self._named_kw_args:
                # 移除�?有未被命名的 kw
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        logging.info(
                            "call with _named_kw_args  name: %s" % name)
                        copy[name] = kw[name]
                kw = copy

            # �?�? kw
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning("arg �? kw arg重复命名�? %s" % k)
                kw[k] = v

        if self._has_request_arg:
            kw["request"] = request

        # �?�? required kw
        if self._required_kw_args:
            for name in self.required_kw_args:
                if not name in kw:
                    return web.HTTPBadRequest("Missing arg %s" % name)
        logging.info("call with args : %s" % str(kw))

        try:
            r = await self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    app.router.add_static("/static/", path)
    logging.info("add_static %s -> %s" % ('/static/', path))


def add_route(app, fn):
    method = getattr(fn, "__method__", None)
    path = getattr(fn, "__route__", None)

    if path is None or method is None:
        raise ValueError('@get or @post 未定�? in %s.' % str(fn))

    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('success add route 网络方法 = %s path = %s => 方法�? = %s(参数 %s)' % (
        method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))
    # app.router.add_route("GET", "/", index)


def add_routes(app, module_name):
    logging.info("add_routes module_name %s" % module_name)
    n = module_name.rfind(".")
    logging.info("add_routes n = %s" % n)

    if n == (-1):
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n + 1:]
        mod = getattr(
            __import__(module_name[:n], globals(), locals(), [name]), name)

    logging.info("add_routes mod = %s" % mod)
    for attr in dir(mod):
        if attr.startswith('_'):
            continue

        fn = getattr(mod, attr)
        #logging.info("add_routes fn = %s" % fn)

        if callable(fn):
            method = getattr(fn, "__method__", None)
            path = getattr(fn, "__route__", None)
            #logging.info("add_routes method = %s, path = %s" % (mod, path))

            if method and path:
                logging.info("add_routes mod = %s" % mod)
                logging.info("add_routes method = %s, path = %s" %
                             (method, path))
                logging.info("add_routes app = %s, fn = %s" % (app, fn))
                add_route(app, fn)
