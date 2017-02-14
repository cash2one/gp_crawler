#!/usr/bin/env python
# coding: utf-8

"""
crawler task 
"""

import sys
sys.path.append("../..")
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import Queue
import threading
import time
import shutil
import subprocess
import pymongo
import socket
from lib import utils

work_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')

class ThreadInfo(object):
    """
    task thread info
    """
    def __init__(self):
        self.id = 0
        self.scan_num = 0
        self.suc_num = 0
        self.fail_num = 0
        self.current = ""
        self.is_stop = False


class TaskInfo(object):
    """
    task info
    """
    def __init__(self, task_name):
        self.name = task_name      # 任务名
        # 任务文件的路径
        self.task_dir = os.path.join(work_root, "./data/task/")
        self.files = {
            # task.desc 任务描述文件
            "desc": "%s/%s.desc" % (self.task_dir, self.name),
            # task.data 数据文件
            "data": "%s/%s.data" % (self.task_dir, self.name),
            # task.proc 进度文件
            "proc": "%s/%s.proc" % (self.task_dir, self.name),
            # task.proc_tmp 临时进度文件
            "proc_tmp": "%s/%s.proc_tmp" % (self.task_dir, self.name),
            # task.stop 停止任务的文件标记
            "stop": "%s/%s.stop" % (self.task_dir, self.name),
            }
        # 任务信息
        self.desc_dict = None
        self.thread_num = 0    # 工作进程数
        self.job_id = 0
        self.thread_info_list = []
        self.history_thread_info = ThreadInfo() # 停止再继续任务后保存的历史信息
        self.queue = Queue.Queue() # 任务队列
        self.beg_time = time.strftime("%Y%m%d")  # 任务开始时间
        self.total_app_num = 0  # 要爬取的app总数
        # 爬取的参数
        self.accounts = ""  # 爬取使用的账号列表，以;分隔


class JobThread(threading.Thread):
    """ 工作线程 """
    def __init__(self, thread_id, task_info):
        threading.Thread.__init__(self)
        self.task_info = task_info
        # thread_id从0开始
        self.thread_info = task_info.thread_info_list[thread_id]
        self.thread_id = thread_id

    def is_stop(self):
        """
        is stop?
        """
        if os.path.exists(self.task_info.files["stop"]):
            utils.log("stop flag exists, stopping...")
            return True
        return False

    def run(self):
        os.chdir(work_root)
        log_file = "%s/log/appinfo_%s.log.%s" % (work_root, self.task_info.name, 
            self.thread_id)
        desc_dict = self.task_info.desc_dict
        while not self.is_stop():
            try:
                self.thread_info.current = self.task_info.queue.get(False)
                # 这里是与特定业务有关的参数

                force_update  = int(desc_dict.get('force_update', '0') or 0)
                task_type = int(desc_dict.get('task_type', '0') or 0)
                # crawler_mgr.py 参数：
                # 1. 包名，如：com.tencent.mm
                # 2. 是否强制更新，1：强制更新；0：不强制更新
                # 3. 任务名称，如：top1
                # 4. 线程id，主要用于爬取时把日志写不同的文件中
                # 5. 爬取使用的gp账号列表，以分号分隔
                # 6. 代理
                # 7. 是否cdn预充
                cmd = 'python ./script/main.py --pack_name="%s" --task_name="%s" ' \
                        '--job_id=%d --force_update=%d --task_type=%d' % (
                                self.thread_info.current, self.task_info.name, 
                                int(self.thread_id), int(force_update), int(task_type))

                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE)
                # 设置超时时间
                timeout = 60 * 60
                beg_time = time.time()
                while True:
                    time.sleep(1)
                    # 是否正常结束
                    ret = p.poll()
                    if ret is None:
                        # 超时
                        if int(time.time() - beg_time) > timeout:
                            utils.log("fail to run command[%s], timeout!" % cmd, "ERROR")
                            self.thread_info.fail_num += 1
                            try:
                                p.kill()
                                time.sleep(2)
                                stat = p.poll()
                                utils.log("kill state: [%d]" % stat)
                            except Exception as e:
                                utils.log("fail to kill process, msg[%s]" % e, "ERROR")
                            break
                    else:
                        output = p.communicate()
                        output = output[0] + output[1]
                        out_handle = open(log_file, 'a')
                        out_handle.write(output)
                        out_handle.close()
                        if ret == 0:
                            self.thread_info.suc_num += 1
                        else:
                            self.thread_info.fail_num += 1
                        break
                self.thread_info.scan_num += 1
            except Queue.Empty:
                utils.log("queue empty!")
                break
            time.sleep(2)
        self.thread_info.is_stop = True
        utils.log("thread_id:[%s] exit!" % self.thread_id)


class StatThread(threading.Thread):
    """ 统计线程 """
    def __init__(self, task_info):
        threading.Thread.__init__(self)
        self.task_info = task_info
        # TODO: 对于重连及连接断开异常需要进行捕获
        # 连接mongodb
        self.client = pymongo.MongoClient(
            "mongodb://work:work@hkg02-appmarket-crawler01.hkg02.baidu.com:27017",
            socketTimeoutMS=10000, 
            connectTimeoutMS=10000, 
            waitQueueTimeoutMS=10000)
        self.mon_db = self.client.crawler
        self.mon_collect = self.mon_db.proc
        self.mon_collect.ensure_index("task_name", unique=True, dropDups=True)

    def __del__(self):
        self.client.close()

    def is_stop(self):
        """
        is stop ?
        """
        for thread_info in self.task_info.thread_info_list:
            if thread_info.is_stop == False:
                return False
        return True

    def init_job_in_mongodb(self):
        """ 初始化该job在mongodb中的状态 """
        # 格式：{"task_name":"top3", "status": "running", "beg_time":"2014-05-09 10:08:43", "source_data":"gp_top3.list.20140702",
        #     "thread_num": 2, 
        #     "jobs": [{"status":"running", "job_id": 0, "mac": "us01-web18.us01", "total_num": 50, "scan_num":30, "suc_num":20, 
        #     "fail_num":10, "current":"com.tencent.mm", "uptime": "2014-05-10 10:10:12"}]
        res = self.mon_collect.find_one({"task_name": self.task_info.name})
        if not res:
            return
        # 如果job信息在mongodb中已存在，则不能再push，否则会出现重复的记录
        for job_info in res["jobs"]:
            if job_info["job_id"] == self.task_info.job_id:
                return
        kv_dict = {}
        kv_dict["status"] = "running"
        kv_dict["job_id"] = self.task_info.job_id
        kv_dict["mac"] = socket.gethostname().rstrip(".baidu.com")
        kv_dict["total_num"] = self.task_info.total_app_num
        kv_dict["scan_num"] = self.task_info.history_thread_info.scan_num
        kv_dict["suc_num"] = self.task_info.history_thread_info.suc_num
        kv_dict["fail_num"] = self.task_info.history_thread_info.fail_num
        kv_dict["current"] = ""
        kv_dict["uptime"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.mon_collect.update(
                {"task_name": self.task_info.name},
                {"$push": {"jobs": kv_dict}})

    def do_stat(self):
        """ 统计进度信息 """
        history_thread_info = self.task_info.history_thread_info
        scan_num = sum([v.scan_num for v in self.task_info.thread_info_list]) + \
                history_thread_info.scan_num
        suc_num  = sum([v.suc_num  for v in self.task_info.thread_info_list]) + \
                history_thread_info.suc_num
        fail_num = sum([v.fail_num for v in self.task_info.thread_info_list]) + \
                history_thread_info.fail_num
        current  = ';'.join([v.current for v in self.task_info.thread_info_list])
        current = current.replace(".", "_")
        return scan_num, suc_num, fail_num, current

    def update_proc_file(self, scan_num, suc_num, fail_num, current):
        """
        update proc file
        """
        proc_file = self.task_info.files["proc"]
        proc_tmp_file = self.task_info.files["proc_tmp"]
        out_str = \
            "total_num=%d\n" \
            "scan_num=%d\n"  \
            "suc_num=%d\n"   \
            "fail_num=%d\n"  \
            "current=%s" % (
            self.task_info.total_app_num, scan_num, suc_num, fail_num, current)
        out_handle = open(proc_tmp_file, 'w')
        out_handle.write(out_str)
        out_handle.close()
        shutil.move(proc_tmp_file, proc_file)

    def update_job_in_mongodb(self, scan_num, suc_num, fail_num, current):
        """ 更新job在mongodb中的状态 """
        # 注意：mongodb中.$是特殊字符
        proc_info = self.mon_collect.find_one(
            {"task_name": self.task_info.name})
        if not proc_info:
            pass
        else:
            if scan_num == self.task_info.total_app_num:
                status = "finish"
            else:
                status = "running"
            # 格式：{"task_name":"top3", "status": "running", "beg_time":"2014-05-09 10:08:43", "source_data":"gp_top3.list.20140702",
            #     "job_num": 2, 
            #     "jobs": [{"status":"running", "job_id": 0, "mac": "us01-web18.us01", "total_num": 50, "scan_num":30, "suc_num":20, 
            #     "fail_num":10, "current":"com.tencent.mm", "uptime": "2014-05-10 10:10:12"}]
            # } 
            # 说明，任务状态有几种，running：正在执行；finish：执行完毕；fail：执行失败
            self.mon_collect.update(
                {
                    "task_name": self.task_info.name,
                    "jobs.job_id": self.task_info.job_id
                },
                {"$set": {
                    "jobs.$.total_num": self.task_info.total_app_num,
                    "jobs.$.scan_num" : scan_num,
                    "jobs.$.suc_num"  : suc_num,
                    "jobs.$.fail_num" : fail_num,
                    "jobs.$.current"  : current.replace(".", "<_>"),
                    "jobs.$.status"     : status,
                    "jobs.$.uptime"   : time.strftime("%Y-%m-%d %H:%M:%S")} 
                })

    def retry(self, func, times, *params):
        """
        retry func 'times' times
        """
        for i in range(times):
            try:
                func(*params)
            except Exception as e:
                utils.log("Error:%s,%s" % (Exception, e)) 
                time.sleep(5)
                continue
            return True
        return False

    def run(self):
        # 初始化mongodb
        ret = self.retry(self.init_job_in_mongodb, 10)
        if ret == False:
            utils.log("Error: fail to init mongodb!", "ERROR")
            sys.exit(1)
        while True:
            # 只有当所有工作线程都退出以后，统计线程才会退出，退出前会输出统计信息
            exit_flag = self.is_stop()
            # 统计进度信息
            scan_num, suc_num, fail_num, current = self.do_stat()
            # 更新进度文件
            self.update_proc_file(scan_num, suc_num, fail_num, current)
            # 更新mongodb
            ret = self.retry(self.update_job_in_mongodb, 10, 
                scan_num, suc_num, fail_num, current)
            if ret == False:
                utils.log("Error: fail to update mongodb!", "ERROR")
                sys.exit(1)
            if exit_flag:
                break
            time.sleep(1)


class Task(object):
    """
    task manager
    """
    def __init__(self, task_name):
        self.task_info = TaskInfo(task_name)
        self.threads = []
        self.stat_thread = None

    def load_task(self):
        """
        load task from db
        """
        desc_file = self.task_info.files["desc"]
        data_file = self.task_info.files["data"]
        if not (os.path.exists(desc_file) and os.path.exists(data_file)):
            return False
        # 读取任务描述文件中的所有(key, value)
        self.task_info.desc_dict = self.file_to_dict(desc_file)
        self.task_info.thread_num = int(self.task_info.desc_dict["thread_num"])
        self.task_info.job_id = int(self.task_info.desc_dict["job_id"])
        for i in range(self.task_info.thread_num):
            thread_info = ThreadInfo()
            self.task_info.thread_info_list.append(thread_info)
        # 读取app列表到队列中
        for line in file(data_file):
            self.task_info.queue.put(line.strip())
        self.task_info.total_app_num = self.task_info.queue.qsize()
        return True

    def load_proc_info(self):
        """
        读取进度文件
        """
        proc_file = self.task_info.files["proc"]
        if not os.path.exists(proc_file):
            return
        proc_dict = self.file_to_dict(proc_file)
        if int(proc_dict["scan_num"]) == 0:
            return
        if self.task_info.total_app_num != int(proc_dict["total_num"]):
            err = "Error: app_num of proc_file and data_file is different!"
            utils.log(err, 'ERROR')
        history_thread_info = self.task_info.history_thread_info
        history_thread_info.total_num = int(proc_dict["total_num"])
        history_thread_info.scan_num = int(proc_dict["scan_num"])
        history_thread_info.suc_num = int(proc_dict["suc_num"])
        history_thread_info.fail_num = int(proc_dict["fail_num"])
        if history_thread_info.scan_num > history_thread_info.total_num or \
           history_thread_info.suc_num  > history_thread_info.total_num or \
           history_thread_info.fail_num > history_thread_info.total_num:
            err = "Error: task.proc num error!"
            utils.log(err, 'ERROR')
            raise Exception(err)
        # 将旧的爬取数据从队列中清除
        for i in range(history_thread_info.scan_num):
            self.task_info.queue.get()

    def start_task(self, cmd):
        """
        删除任务停止的文件标记
        """
        stop_file = self.task_info.files["stop"]
        if os.path.exists(stop_file):
            os.remove(stop_file)
        if cmd == "start":
            pass
        elif cmd == "continue":
            # 继续上一次的任务
            self.load_proc_info()
        else:
            err = "Error: invalid cmd:[%s]" % cmd
            utils.log(err, 'ERROR')
            raise Exception(err)

        utils.log("total:[%d], beg:[%d]" % (self.task_info.total_app_num,
            self.task_info.history_thread_info.scan_num + 1))
        # 启动工作线程
        for i in range(self.task_info.thread_num):
            utils.log("starting thread:[%d]" % i)
            t = JobThread(i, self.task_info)
            # True表示父线程结束时，子线程立即结束
            t.setDaemon(True)
            t.start()
            self.threads.append(t)

        utils.log("starting statistics thread...")
        # 启动统计线程
        stat = StatThread(self.task_info)
        stat.setDaemon(False)
        stat.start()

    def file_to_dict(self, conf_file):
        """
        读取配置文件的信息到字典中
        """
        kv_dict = {}
        for line in file(conf_file):
            line = line.strip()
            if line == "" or line[0] == "#":
                continue
            fields = line.split("=")
            if len(fields) != 2:
                continue
            kv_dict[fields[0]] = fields[1]
        return kv_dict

    def do(self, cmd):
        """
        cmd: start, 从头执行; continue, 从上次结束位置开始执行
        1. 读取任务配置和数据
        """
        utils.log("loading task_info...")
        self.load_task()

        # 2. 启动任务
        utils.log("starting task...")
        self.start_task(cmd)

        # 3. 等待任务结束
        for t in self.threads:
            t.join()

        queue_size = self.task_info.queue.qsize()
        if queue_size == 0:
            utils.log("task:[%s], mission complete!" % self.task_info.name)
        else:
            utils.log("task:[%s] has been stop, queue size[%d]!" % (
                self.task_info.name, queue_size))


def local_main():
    """
    local main
    """
    arg_num = len(sys.argv)
    if arg_num < 2:
        print "usage: %s task_name [cmd]" % sys.argv[0]
        print "cmd: start|continue"
        sys.exit(1)
    elif arg_num == 2:
        task_name = sys.argv[1]
        cmd = "start"
    else:
        task_name = sys.argv[1]
        cmd = sys.argv[2]

    obj = Task(task_name)
    obj.do(cmd)


if __name__ == "__main__":
    local_main()


