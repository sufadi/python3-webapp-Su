# handlers.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import json
import logging
import hashlib
import base64
import asyncio
from coreweb import get, post
from model import User, Comment, Blog, next_id

'url handlers'


@get('/')
def index(request):
    summary = 'Python学习小组-王大锤，谌铁柱，凌二蛋，苏总'
    blogs = [
        Blog(id='1', name='王大锤和美美的爱情故事', summary=summary,
             created_at=time.time() - 120),
        Blog(id='2', name='凌二蛋到底什么时候结婚', summary=summary,
             created_at=time.time() - 3600),
        Blog(id='3', name='谌铁柱的期权变现走向人生巅峰', summary=summary,
             created_at=time.time() - 7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }


@get('/api/users')
def api_get_users():
    users = yield from User.findAll(orderBy='created_at desc')
    for u in users:
        # 浏览器显示 ******
        u.passwd = '******'
    return dict(users=users)
