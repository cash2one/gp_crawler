#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: log.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/07/23 17:26:25
"""
import os
from lib import const
from lib import utils

class Log(object):
    """ 日志纪录
        对于抓取googleplay的app, 如果是多版本, 纪录成多条日志
    """
    def __init__(self):
        self.job_id = -1

        self.host = ''
        self.task_name = ''
        self.task_type = const.TaskType.DEFAULT
        self.package = ''
        self.packageid = 0
        self.is_channel = 0
        self.multiapk = const.MultiApkType.NO_MULTIAPK
        self.free = 1
        self.title = ''
        self.force_update = 0
        self.apk_source = ''

        self.account = ''
        self.password = ''
        self.android_id = ''
        self.proxies = ''
        self.old_version_code = 0
        self.old_version_name = ''
        self.new_version_code = 0
        self.new_version_name = ''
        self.action = const.Action.DEFAULT
        self.ret_code = const.RetCode.DEFAULT
        self.compatible_code = -1
        self.begin_time = utils.cur_time_secs()
        self.total_cost_time = 0
        self.detect_timestamp = ''
        self.download_cost_time = 0

    def __setattr__(self, name, value):
        if type(value) == unicode:
            value = value.encode('utf8')
        super(Log, self).__setattr__(name, value)

    def print_2_file(self):
        """ 打印单条日志
        """
        self.host = utils.get_local_host_name()
        self.task_name = self.task_name or 'manual'
        log_str = 'Time[%s],Host[%s],Task[%s],Account[%s],AndroidId[%s],Password[%s],' \
            'Proxies[%s],PackId[%d],PackName[%s],PackTitle[%s],RetCode[%d],CompatibleCode[%d],' \
            'CostTime[%d],Action[%s],TaskType[%d],ForceUpdate[%d],Channel[%d],Free[%d],' \
            'Multiapk[%d],OldVersionCode[%d],NewVersionCode[%d],OldVersionName[%s],' \
            'NewVersionName[%s],ApkSource[%s]' % (utils.time_stamp(), self.host, self.task_name, 
            self.account, self.android_id, self.password, self.proxies, self.packageid, 
            self.package, self.title, self.ret_code.value, self.compatible_code, 
            self.total_cost_time, self.action.value, self.task_type, self.force_update, 
            int(self.is_channel), self.free, self.multiapk, self.old_version_code, 
            self.new_version_code, self.old_version_name, self.new_version_name, self.apk_source)

        cur_date, cur_hour = utils.time_stamp('%Y%m%d'), utils.time_stamp('%H')
        if self.task_name == 'manual':
            log_file = os.path.join(const.LOG_PATH, 'appstat_manual.log.%s' % (cur_date))
        else:
            log_file = os.path.join(const.LOG_PATH, 'appstat_%s.log.%s.%s.%d' % (
                self.task_name, cur_date, cur_hour, self.job_id))
        with open(log_file, 'a') as fd:
            fd.write('%s\n' % (log_str))
            fd.flush()

if __name__ == '__main__':
    log = Log()
        
