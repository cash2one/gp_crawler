#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: db.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/07/30 13:42:00
"""
import os
import sys
import MySQLdb

from lib import error
from lib import utils

class DbHelper(object):
    """ 封装db处理接口
        Args:
            host: 机器地址
            port: 机器端口
            user: 用户名
            password: 密码
            db_name: 连接database名称
    """
    def __init__(self, host, port, user, password, db_name):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name

        self.db = None
        self.cursor = None

    def __del__(self):
        if self.db is not None:
            del self.db
        if self.cursor is not None:
            del self.cursor

    def connect(self):
        """ 连接db
        """
        if self.db is None:
            self.db = MySQLdb.connect(host=self.host, 
                                    port=self.port,
                                    user=self.user,
                                    passwd=self.password,
                                    charset='utf8',
                                    db=self.db_name)
            self.cursor = self.db.cursor()

    def reconnect(self):
        """ 重连db
        """
        self.db = None
        self.connect()

    def execute(self, cmd):
        """ 运行sql, 出现异常时重连db再运行. 默认60s自动断开连接
        """
        try:
            self.connect()
            self.cursor.execute(cmd)
            self.db.commit()
        except Exception as err:
            try:
                self.reconnect()
                self.cursor.execute(cmd)
                self.db.commit()
            except Exception as err:
                raise error.DbError('cmd=[%s], err=[%s]' % (cmd, err))

    def fetchone(self):
        """ 获取单行
        """
        try:
            return self.cursor.fetchone()
        except Exception as err:
            raise error.DbError(err)

    def fetchall(self):
        """ 获取所有结果
        """
        try:
            return self.cursor.fetchall()
        except Exception as err:
            raise error.DbError(err)

if __name__ == '__main__':
    a = DbHelper.get_instance('./conf/db.ini')
    a.execute('select * from package limit 1')
    print a.fetchall()

