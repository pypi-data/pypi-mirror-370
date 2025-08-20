# -*- coding: utf-8 -*-
"""
jf-ext.cacheExt.py
~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import sqlite3
import json
import hashlib
import functools
from typing import Callable

DB_PATH = "cache.db"

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

# 生成参数哈希作为缓存 key
def make_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    data = {
        "func": func.__module__ + "." + func.__name__,
        "args": args,
        "kwargs": kwargs
    }
    key_raw = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(key_raw.encode()).hexdigest()

# 装饰器定义
def jf_local_cache(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        init_db()
        key = make_cache_key(func, args, kwargs)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # 查询缓存
        c.execute("SELECT value FROM cache WHERE key=?", (key,))
        row = c.fetchone()
        if row:
            return json.loads(row[0])  # 返回缓存值

        # 计算结果并写入缓存
        result = func(*args, **kwargs)
        value = json.dumps(result, ensure_ascii=False, default=str)
        c.execute("REPLACE INTO cache (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()
        return result
    return wrapper


# pragma mark -
# --------------------------------------------------------------------------------
if __name__ == '__main__':
    @jf_local_cache
    def slow_func(x, y):
        print("执行函数...")
        return x + y
    print(slow_func(3, 4))  # 第一次执行，会打印“执行函数...”
    print(slow_func(3, 4))  # 第二次执行，直接读取缓存
    print(slow_func(3, 4))  # 第二次执行，直接读取缓存
