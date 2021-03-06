#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: const.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/07/23 17:55:29
"""
import os
import enum

ROOT_PATH = os.path.join(os.path.dirname(__file__), '..')
CONF_PATH = os.path.join(ROOT_PATH, 'conf')
DATA_PATH = os.path.join(ROOT_PATH, 'data')
TMP_PATH = os.path.join(DATA_PATH, 'tmp')
LOG_PATH = os.path.join(ROOT_PATH, 'log')

GP_CATEGORY = os.path.join(DATA_PATH, 'googleplay_category.dat')
GP_2_MM_CATEGORY = os.path.join(DATA_PATH, 'googleplay_2_mm_category.dat')

APKS_MAIL = os.path.join(CONF_PATH, 'aps_mail_list.txt')

APK_DECOMPILE_BIN_PATH = os.path.join(ROOT_PATH, 'thirdparty', 'apk_decompile', 'AXMLPrinter2.jar')

DEFAULT_LANG = 'en_US'

# 从android版本映射到sdk
AndroidVer2Sdk = {
    '1.6': 4,
    '2.0': 5,
    '2.0.1': 6,
    '2.1.x': 7,
    '2.2.x': 8,
    '2.2': 8,
    '2.3': 9,
    '2.3.1': 9,
    '2.3.2': 9,
    '2.3.3': 10, 
    '2.3.4': 10, 
    '2.3.4': 10, 
    '3.0': 11,
    '3.0.x': 11, 
    '3.1': 12,
    '3.1.x': 12, 
    '3.2': 13, 
    '4.0': 14, 
    '4.0.1': 15, 
    '4.0.2': 16, 
    '4.2': 17, 
    '4.2.2': 17, 
    '4.3': 18, 
    '4.4': 19, 
    '4.4W': 20, 
    '5.0': 21, 
}

class TaskType(object):
    """ 任务类型, 现在主要用来区分是否下载apk文件还是只需要详情
    """
    DEFAULT = 0       # 默认, 在db存在则有state决定, 否则默认DOWNLOAD
    DOWNLOAD = 1      # 需要下载apk文件
    DETAIL = 2        # 只需要app详情

    @classmethod
    def state_2_type(cls, state):
        """ 根据db package state字段判断任务类型
            state:
                0: 有apk, 在线
                1: 有apk, 下线
                2: 无apk, 在线
        """
        return cls.DETAIL if state == 2 else cls.DOWNLOAD

    @classmethod
    def type_2_state(cls, type):
        """ 从任务类型判断db package state字段
        """
        return 2 if type == TaskType.DETAIL else 0
            

class RetCode(enum.Enum):
    """ 抓取app状态列表
    """
    DEFAULT = -1                          # 默认状态码
    OK = 0                                # 成功
    REQUEST_ERROR = 10                    # 请求错误
    MUTEX = 1                             # 获取app锁失败
    DB_ERROR = 4                          # 读写db失败
    ITEM_NOT_FOUND = 6                    # app在源站不存在
    NO_COMPATIBLE_ACCOUNT = 11            # 没有适配可下载账号
    APK_DECOMPILER_ERROR = 12             # apk解析失败
    DOWNLOAD_APK_ERROR = 13               # 下载apk失败
    CLEAR_MEMCACHE = 14                   # 清理cache失败

    PRE_SCAN_ERROR = 40                   # 预处理服务失败
    MULTI_VERSION_SCAN_ERRRO = 41         # 多版本扫描服务失败
    GET_MULTI_CONTENT_RATING_ERROR = 42   # 获取详情失败
    GET_PAID_INFO_ERROR = 43              # 获取付费信息失败
    GET_DETAIL_ERROR = 44                 # 获取详情失败
    PROCESS_IMAGE_ERROR = 45              # 图片处理失败
    DOWNLOAD_APK_ERROR = 46               # 下载apk失败
    PARSE_APK_ERROR = 47                  # 反解apk失败
    UPLOAD_STORAGE_ERROR = 48             # 上传文件到存储平台失败
    VERSION_CODE_EQ_ZERO_ERROR = 49       # 详情的versioncode为0，实质是没有可用帐号

    RESOURCE_LOST_ERROR = 50              # 资源缺失
    UNKNOWN_ERROR = 101                   # 未知错误


class Action(enum.Enum):
    """ 通过对比db里的app信息判断抓取行为
    """
    DEFAULT = 'NO_NEED'                      # 不做任何处理
    INSERT = 'INSERT'                        # 新增app
    UPDATE_DETAIL = 'UPDATE_DETAIL'          # 更新动态详情
    UPDATE_APK = 'UPDATE'                    # 更新apk文件
    UPDATE_MULTIAPK = 'UPDATE_MULTIAPK'      # 更新多版本

    @classmethod
    def filter_download_apk(cls, action):
        """ 是否需要下载apk文件
        """
        return action in [cls.INSERT, cls.UPDATE_APK, cls.UPDATE_MULTIAPK]

    @classmethod
    def filter_update_doc(cls, action):
        """ 是否需要更新doc表
        """
        return action in [cls.INSERT, cls.UPDATE_APK]

    @classmethod
    def filter_update_multi_version(cls, action):
        """ 是否有可能更新apk_version_info表
        """
        return action in [cls.INSERT, cls.UPDATE_APK, cls.UPDATE_MULTIAPK]


class MultiApkType(object):
    """ 多版本类型
    """
    NO_MULTIAPK = 0      # 非多版本
    MULTIAPK = 1         # 多版本
    FOR_CRALWER = 2      # 多版本, 用作爬虫标识更新, 线上识别为非多版本


class Cpu(enum.Enum):
    """ cpu类型
    """
    ARMEABI = 'armeabi'
    ARMEABI_V7A = 'armeabi-v7a'
    MIPS = 'mips'
    X86 = 'x86'

    @classmethod
    def get_all_values(cls):
        """ 获取所有的cpu名称
        """
        return cls.values()


class AppCategory(enum.Enum):
    """ app大分类, 比如application, game, family
        存储时从googleplay到mm有映射关系
    """
    APPLICATION = 'soft'
    GAME = 'game'

    @classmethod
    def has_gp_category(cls, category):
        """ 是否支持当前googleplay分类
        """
        return hasattr(cls, category)

    @classmethod
    def get_mm_category(cls, gp_category):
        """ 从googleplay分类映射到mm分类
        """
        return getattr(cls, gp_category).value.lower()


class HttpStatusCode(object):
    """ http状态码
    """
    OK = 200
    BAD_REQUEST = 400
    AUTH_ERROR = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
    NOT_IMPLEMENTED = 501
    
if __name__ == '__main__':

    import pdb
    pdb.set_trace()
    #AppCategory.get_mm_app_category('APPLICATION')
    action = Action.DEFAULT
