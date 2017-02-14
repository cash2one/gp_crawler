#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: script/timeout_main.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/08/24 11:27:55
"""
import sys
import time
import argparse
import subprocess

import __init__
from lib import const
from lib import utils

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
    cmd = 'python %s/script/main.py --pack_name="%s" --source="%s" --task_name="%s" --job_id=%s '\
        '--force_update=%s --task_type=%s' % (const.ROOT_PATH, args.pack_name, args.source, 
        args.task_name, args.job_id, args.force_update, args.task_type)
    begin_time = utils.cur_time_secs()
    ret_code = -1
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pid = p.pid
    while True:
        if p.poll() is None:
            if utils.cur_time_secs() - begin_time > 30 * 60:
                utils.log('crawler timeout. package=[%s]' % (args.pack_name), 'WARNING')
                try:
                    p.kill()
                    time.sleep(2)
                except:
                    utils.log('failed to kill process. pid=[%d]' % (pid), 'WARNING')
                else:
                    utils.log('succeed to kill process. pid=[%d], state=[%s]' % (pid, p.poll()))
                finally:
                    break
        else:
            ret_code = p.wait()
            stdoutput, erroutput = p.communicate()
            utils.log('%s' % (stdoutput + erroutput))
            break
    return ret_code

if __name__ == '__main__':
    ret_code = local_main()
    sys.exit(ret_code)
