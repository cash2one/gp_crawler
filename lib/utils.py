#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: utils.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/07/23 15:14:54
"""
import os
import time
import json
import socket
import datetime
import requests
import random
import hashlib
import protobuf_to_dict

import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage

try:
    requests.packages.urllib3.disable_warnings()
except Exception as e:
    pass

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
    timeout = 600
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


def randint(start=0, end=100):
    """ 随机整数
    """
    return random.randint(start, end)


def md5sum(content):
    """ 计算内容md5
    """
    return hashlib.md5(content).hexdigest()


def json_decode(json_dict):
    """ 从json转换为字符串
    """
    return json.dumps(json_dict, encoding='utf8')


def json_encode(json_str):
    """ 从字符串转换为json
    """
    return json.loads(json_str, encoding='utf8')


def message_2_dict(message):
    """ 从protobuf message转换到dict
    """
    return protobuf_to_dict.protobuf_to_dict(message)


def cur_time_secs():
    """ 获取当前时间秒数
    """
    return time.time()


def get_local_host_name():
    """ 获取本机hostname
    """
    return socket.gethostname()

def time_stamp(formatter='%Y-%m-%d %H:%M:%S'):
    """ 按照特定格式返回当前时间
    """
    return time.strftime(formatter)


def convert_time_formatter(time_str, from_formatter, to_formatter):
    """ 时间格式转化
    """
    return datetime.datetime.strptime(time_str, from_formatter).strftime(to_formatter)


def init_dir_path(dir_path):
    """ 初始化目录
    """
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)


def init_file_path(file_path):
    """ 初始化文件所在目录
    """
    dir_path = os.path.dirname(file_path)
    init_dir_path(dir_path)


def get_file_md5(file_path):
    """ 获取文件md5
    """
    return md5sum(open(file_path).read())


def log(log_str, level='INFO'):
    """ 日志打印
    """
    try:
        print '[%s]-%s- %s' % (time_stamp(), level, log_str)
    except:
        pass


def send_mail(subject, content, receivers, sender):
    """
    subject:邮件标题
    content:邮件内容
    receivers:邮件接受者 type: list
    sender:邮件发送者
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    receivers = \
            map(lambda x: (x.strip()+'@baidu.com') if x.find('@')<0 else x.strip(), receivers)
    msg['To'] = (", ").join(receivers)
    msg.attach(MIMEText(content))

    s = smtplib.SMTP(timeout=300)
    s.connect('mail2-in.baidu.com')
    s.sendmail(sender, receivers, msg.as_string())
    s.quit()



