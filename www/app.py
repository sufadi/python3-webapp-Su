#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python基础-Web App 骨架

import logging
logging.basicConfig(level=logging.INFO)

import asyncio
import os
import json
import time
from datetime import datetime

import orm
from aiohttp import web
from coreweb import add_routes, add_static
from jinja2 import Environment, FileSystemLoader
from model import User, Blog, Comment


def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env

async def logger_factory(app, handler):

    async def logger(request):
        logging.info('Request: %s %s' % (request.method, request.path))
        return (await handler(request))
    return logger

async def data_factory(app, handler):

    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                logging.info('request json: %s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = await request.post()
                logging.info('request form: %s' % str(request.__data__))

        return (await handler(request))
    return parse_data

async def response_factory(app, handler):

    async def response(request):
        logging.info('Response handler...request %s' % request)
        r = await handler(request)

        if isinstance(r, web.StreamResponse):
            logging.info('web.StreamResponse % r' % r)
            return r

        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            logging.info('isinstance bytes % resp' % resp)
            return resp

        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])

            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            logging.info('isinstance str % resp' % resp)
            return resp

        if isinstance(r, dict):
            logging.info('Response handler...__template__ %s' % r)
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(
                    r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                logging.info('isinstance dict None % resp' % resp)
                return resp
            else:
                resp = web.Response(
                    body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                logging.info('isinstance dict templating % resp' % resp)
                return resp

        if isinstance(r, int) and r >= 100 and r < 600:
            logging.info('isinstance int % r' % web.Response(r))
            return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                logging.info('isinstance tuple int % r' %
                             web.Response(t, str(m)))
                return web.Response(t, str(m))
        # default:
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        logging.info('default resp % r' % resp)
        return resp
    return response


def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟�?'
    if delta < 3600:
        return u'%s分钟�?' % (delta // 60)
    if delta < 86400:
        return u'%s小时�?' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s�?%s�?%s�?' % (dt.year, dt.month, dt.day)

async def init(loop):
    await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='root', password='', db='sufadi')
    app = web.Application(loop=loop, middlewares=[
        logger_factory, response_factory
    ])

    # 通过router的指定的方法可以把请求的链接和对应的处理函数关联在一�?
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    add_routes(app, 'handlers')
    add_static(app)
    # 运行web服务�?,服务器启动后,有用户在浏览器访�?,就可以做出对应的响应
    # 127.0.0.1 本机地址
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv

# 固定写法
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
