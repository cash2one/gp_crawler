#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: lib/utils.py
Author: work(work@baidu.com)
Date: 2015/07/24 12:59:37
"""
import datetime
import requests

try:
    requests.packages.urllib3.disable_warnings()
except Exception as e:
    pass


def log(log_str, level='INFO'):
    """ 日志
    """
    timestamp = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    log_str = '[%s][%s] %s' % (timestamp, level, log_str)
    print log_str


def timestamp(formatter='%Y%m%d'):
    """ 获取特定格式的当前时间
    """
    return datetime.datetime.today().strftime(formatter)

def requests_ex(url, data=None, headers=None, cookies=None, proxies=None, timeout=100,
                verify=False, retry_times=3):
    """ Requests封装避免抛未知异常, 且支持超时重试
        Args:
            data: string, If None, get; then post
            headers: dict, 请求头部, 默认None
            cookies: dict, 请求cookies, 默认None
            proxies: dict, 请求使用代理, 默认None
            timeout: int, 持续未接收到数据的最大时间间隔. 默认100
            verify: bool, 请求认证, 默认False
            retry_times: int. 超时重试次数, 默认3
    """
    idx = 0
    while idx < retry_times:
        try:
            if data is not None:
                res = requests.post(url=url, data=data, headers=headers, timeout=timeout,
                    proxies=proxies, verify=verify, cookies=cookies)
            else:
                res = requests.get(url=url, headers=headers, timeout=timeout, proxies=proxies,
                    verify=verify, cookies=cookies)
            return res
        except requests.exceptions.Timeout:
            idx += 1
    if idx >= retry_times:
        raise requests.exceptions.Timeout('timeout')


