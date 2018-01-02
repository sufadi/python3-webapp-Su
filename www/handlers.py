# handlers.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, time, json, logging, hashlib, base64, asyncio
from coreweb import get, post
from model import User, Comment, Blog, next_id

'url handlers'
@get("/")
@asyncio.coroutine
def index(request):
	users = yield from User.findAll()
	return {
		"__template__":"home.html",
		'users': users
	}
