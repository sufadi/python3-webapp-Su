�?  # !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python基础- 配置文件[�?发环境的标准配置]

'''
缺省配置
'''

configs = {
    'debug': True,
    'db': {
        'host': "127.0.0.1",
        "port": 3306,
                "user": "root",
                "password": "",
                "db": "sufadi"
    },
    "session": {
        "secret": "sufadi"
    }
}
