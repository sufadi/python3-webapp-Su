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
async def index(request):
    logging.info('handlers.py handlers index: %s' % request)
    users = await User.findAll()
    return {
        "__template__": "home.html",
        'users': users
    }
