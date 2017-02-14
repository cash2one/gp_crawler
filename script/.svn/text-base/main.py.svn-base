#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: main.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/08/17 17:40:00
"""
import sys
import argparse

import __init__

from src import metadata
from src import googleplay_crawler

def local_main():
    """ 主入口
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack_name', help='package\'s name')
    parser.add_argument('--source', default='googleplay', 
        help='package\'s source, default: googleplay')
    parser.add_argument('--task_name', default='manual', help='task name, defalut: manual')
    parser.add_argument('--task_type', type=int, default=0, 
        help='task type, optional: [0, 1, 2], default: 0')
    parser.add_argument('--job_id', type=int, default=0, help='job id, default: 0')
    parser.add_argument('--force_update', type=int, default=0, 
        help='whether forced update or not, optional: [0, 1], default: 0')

    args = parser.parse_args()
    pack_name = args.pack_name
    source = args.source
    task_name = args.task_name
    task_type = args.task_type
    job_id = args.job_id
    force_update = args.force_update

    request = metadata.Request()
    request.package = pack_name
    request.task_name = task_name
    request.task_type = task_type
    request.job_id = job_id
    request.force_update = force_update

    if source.upper() == 'GOOGLEPLAY':
        crawler = googleplay_crawler.GoogleplayCrawler() 
        crawler.init()
        crawler.set_request(request)
        ret = crawler.do()
        return ret
if __name__ == '__main__':
    ret_code = local_main()
    sys.exit(ret_code)



