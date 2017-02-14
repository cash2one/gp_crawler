#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: script/sync_to_hdfs.py
Authora: work(work@baidu.com)
Date: 2015/10/14 11:34:13
"""
import os
import sys
from lib import const

HADOOP_BIN = '/home/work/tools/cdh-client/bin/hadoop'
HDFS_DIR = '/flume/i18n_googleplay_topcharts_raw/'
IMPALA_SHELL_BIN = '/home/work/tools/cdh-client//lib/impala/bin/impala-shell'
IMPALA_HOST_PORT = 'hkg02-i18n-cdh003.hkg02.baidu.com:21000'

def sync_by_date(date):
    file_prefix = 'topcharts_%s' % (date)
    date_hdfs_path = '%s/dt=%s' % (HDFS_DIR, date)
    cmd = '%s fs -rmr %s' % (HADOOP_BIN, date_hdfs_path)
    print cmd
    os.system(cmd)
    for file in os.listdir(const.DATA_PATH):
        file_path = os.path.join(const.DATA_PATH, file)
        if os.path.isfile(file_path) and file.startswith(file_prefix):
            cmd = 'awk -F \'\\t\' \'{gsub(/application/, "app", $1); printf("%%s\\t%%s\\t%%s\\t%%s\\t%%s\\n", $1, $2, $3, $4, $5)}\' %s > %s1'  % (file_path, file_path)
            print cmd
            os.system(cmd)
            cmd = 'mv %s1 %s -f' % (file_path, file_path)
            print cmd
            os.system(cmd)
            country = file.split('_')[-1]
            country_hdfs_path = '%s/country=%s' % (date_hdfs_path, country)
            mkdir_cmd = '%s fs -mkdir -p %s' % (HADOOP_BIN, country_hdfs_path)
            print mkdir_cmd
            os.system(mkdir_cmd)
            put_cmd = '%s fs -put %s %s' % (HADOOP_BIN, file_path, country_hdfs_path)
            print put_cmd
            os.system(put_cmd)
            alter_cmd = '%s -i %s -q \'alter table mobomarket.i18n_googleplay_topcharts_raw add partition(dt="%s", country="%s")\'' % (IMPALA_SHELL_BIN, IMPALA_HOST_PORT, date, country)
            print alter_cmd
            os.system(alter_cmd)



    



