# model.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python基础-model模块

import time
import uuid

from orm import Model, StringField, BooleanField, FloatField, TextField

# 主键的缺�?


def next_id():
    # time.time 设置当前日期和时�?
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

# 建立数据库表 users


class User(Model):
    __table__ = 'users'

    # 数据-字段
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)

# 建立数据库表 blogs


class Blog(Model):
    # 数据-表名
    __table__ = 'blogs'

    # 数据-字段
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)

# 建立数据库表 comments


class Comment(Model):
    # 数据-表名
    __table__ = 'comments'

    # 数据-字段
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)
