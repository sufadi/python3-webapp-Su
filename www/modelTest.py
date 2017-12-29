# model.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python基础-model模块

import orm
import asyncio
from model import User, Blog, Comment

def test(loop):
	yield from orm.create_pool(loop = loop, user = "root", password="", database = "sudfadi")

	u = User(name = "Test", email = "test@sufadi.com", passwd = "123", image = "about:blank")

	yield from u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()