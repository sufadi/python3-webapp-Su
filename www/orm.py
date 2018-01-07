�?  # !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python基础-编写 数据库增删改�? ORM
import logging
logging.basicConfig(level=logging.INFO)
import asyncio
import aiomysql


def log(sql, args=()):
    logging.info('SQL: %s' % sql)

# 创建连接�?
async def create_pool(loop, **kw):
    logging.info("建立数据库连接池")
    # 全局的连接池
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get("host", "localhost"),
        port=kw.get("port", 3306),
        user=kw["user"],
        password=kw["password"],
        db=kw["db"],
        # 防止乱码
        charset=kw.get("charset", "utf8"),
        # True 表示不需要在commit提交事务
        autocommit=kw.get("autocommit", True),
        maxsize=kw.get("maxsize", 10),
        minsize=kw.get("minsize", 1),
        loop=loop
    )

# Select 语句 查询语句
# sql 为sql语句�? args为占位符参数列表�? siez为查询数�?


def select(sql, args, size=None):
    log(sql, args)
    global __pool
    with (yield from __pool) as conn:
        cur = yield from conn.cursor(aiomysql.DictCursor)
        # SQL 语句的占位符�? ? ,�? MySQL 的占位符�? %s，股这里进行转换
        # yield form 将调用一个子协程（即�?个协程调用宁�?个协程），并直接获得子协程的返回结果
        yield from cur.execute(sql.replace("?", "%s"), args or ())

        if size:
            # 获取指定 size 的记�?
            rs = yield from cur.fetchmany(size)
        else:
            # 获取�?有记�?
            rs = yield from cur.fetchall()

        yield from cur.close()
        logging.info('rows returned %s' % len(rs))

        return rs


# 用于增，删，改的数据库操�?
@asyncio.coroutine
def execute(sql, args):
    log(sql)

    with (yield from __pool) as conn:
        try:
            cur = yield from conn.cursor()
            # SQL 语句的占位符�? ? ,�? MySQL 的占位符�? %s，股这里进行转换
            # yield form
            # 将调用一个子协程（即�?个协程调用宁�?个协程），并直接获得子协程的返回结果
            yield from cur.execute(sql.replace("?", "%s"), args)
            # 返回结果�?
            affected = cur.rowcount
            yield from cur.close()
        except BaseException as e:
            raise
        return affected


def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)


class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return "<%s, %s : %s>" % (self.__class__.__name__, self.column_type, self.name)


class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl="varchar(100)"):
        super().__init__(name, ddl, primary_key, default)


class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)


class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)


class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)


class TextField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)
# 定义基类


class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):
        # 排除 Model 类本�?
        if name == "Model":
            return type.__new__(cls, name, bases, attrs)
        # 获取 table 名称
        tableName = attrs.get("__table__", None) or name
        logging.info("found model : %s (table: %s)" % (name, tableName))
        # 获取�?有的Field和主键名

        mappings = dict()
        fields = []
        primaryKey = None

        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info("Found mapping: %s --> %s" % (k, v))
                mappings[k] = v
                if v.primary_key:
                    # 找到主键
                    if primaryKey:
                        raise StandardError(
                            'Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fields.append(k)

        if not primaryKey:
            raise StandardError('Primary key not found.')

        for k in mappings.keys():
            attrs.pop(k)

        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        # 保存属�?�和列的映射关系
        attrs['__mappings__'] = mappings
        attrs['__table__'] = tableName
        # 主键属�?�名
        attrs['__primary_key__'] = primaryKey
        # 除主键外的属性名
        attrs['__fields__'] = fields
    # 构�?�默认的SELECT, INSERT, UPDATE和DELETE语句:
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (
            primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(
            escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(
            map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (
            tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)


# 定义 Model
class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(
                    field.default) else field.default
                logging.debug("using default value for %s : %s" %
                              (key, str(value)))
                setattr(self, key, value)

        return value

    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        ' find objects by where clause. '
        logging.info('findAll: %s' % sql)
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)

        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)

        if orderBy:
            sql.append('order by')
            sql.append(orderBy)

        limit = kw.get('limit', None)

        if limit is not None:
            sql.append('limit')

            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)

            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))

        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        ' find number by select and where. '
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)

        rs = awaitselect(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None

        return rs[0]['_num_']

    @classmethod
    async def find(cls, pk):
        ' find object by primary key. '

        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None

        return cls(**rs[0])

    @asyncio.coroutine
    def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = yield from execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)

    @asyncio.coroutine
    def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = yield from execute(self.__update__, args)

        if rows != 1:
            logging.warn(
                'failed to update by primary key: affected rows: %s' % rows)

    @asyncio.coroutine
    def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = yield from execute(self.__delete__, args)

        if rows != 1:
            logging.warn(
                'failed to remove by primary key: affected rows: %s' % rows)
