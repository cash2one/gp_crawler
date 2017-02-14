#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: error.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/07/23 19:03:53
"""

class ParamError(Exception):
    """ 请求参数错误
    """
    pass 


class ImpossibleError(Exception):
    """ 防御编程, 不可能出现的场景
    """
    pass


class DbError(Exception):
    """ db相关错误
    """ 
    pass


class UnknownCategory(Exception):
    """ 未知的gp分类
    """
    pass


class HttpServerError(Exception):
    """ http请求出现错误
        Attributes:
            url: http请求地址
            msg: http请求出现错误
            extra: 附加信息
    """
    def __init__(self, url='', msg='', extra=''):
        self.url = url
        self.msg = msg
        self.extra = extra

    def __str__(self):
        return 'url=%s, msg=%s, %s' % (self.url, self.msg, self.extra)


class PreScanError(HttpServerError):
    """ 预扫描错误
    """
    pass


class MultiVersionScanError(HttpServerError):
    """ 多版本扫描错误
    """
    pass


class GetMultiContentRatingError(HttpServerError):
    """ 获取内容分级错误
    """
    pass


class GetPaidInfoError(HttpServerError):
    """ 获取付费信息错误
    """
    pass


class GetDetailError(HttpServerError):
    """ 获取app详情错误
    """
    pass


class DownloadApkError(HttpServerError):
    """ 下载apk错误
    """
    pass


class ProcessImageError(HttpServerError):
    """ 处理图片错误
    """
    pass


class UploadFileError(HttpServerError):
    """ 上传文件错误
    """
    pass


class ItemNotFound(Exception):
    """ app在gp不存在
    """
    pass


class ChannelApp(Exception):
    """ 渠道app
    """
    pass


class NoCompatibleAccount(Exception):
    """ 无适配账号
    """
    pass


class ParseApkError(Exception):
    """ 解析apk文件错误
    """
    pass

class VersionError(Exception):
    """
    Version code equal 0
    """
    pass
