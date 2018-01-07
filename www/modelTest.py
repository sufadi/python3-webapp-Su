# model.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python基础-model模块

import orm
import asyncio
from model import User, Blog, Comment


@asyncio.coroutine
def test(loop):
    yield from orm.create_pool(loop=loop, host="127.0.0.1", port=3306, user="root", password="", database="sufadi")

    u = User(name="Test", email="test@sufadi.com", passwd="123")
    u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()
