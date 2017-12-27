#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python基础-编写 ORM
import logging; logging.basicConfig(level = logging.INFO)
import asyncio

# 创建连接池
@asyncio.coroutine
def create_pool(loop, **kw):
	logging.info("建立数据库连接池")
	# 全局的连接池
	global __pool
	__pool = yield from aiomysql.create_pool(
		host = kw.get("host", "localhost"),
		port = kw.get("port", 3306),
		user = kw["user"],
		password = kw["123456"],
		db = kw["db"],
		charset = kw.get("charset", "utf8"),
		autocommit = kw.get("autocommit", True),
		maxsize = kw.get("maxsize", 10),
		minsize = kw.get("minsize", 1),
		loop = loop
	)

# Select 语句
# 异步注释句
def select(sql, args, size = None):
	log(sql, args)
	global __pool
	with (yield from __pool) as conn:
		cur = yield from conn.cursor(aiomysql.DictCursor)
		yield from cur.execute(sql.replace("?", "%s"), args or ())
		pass