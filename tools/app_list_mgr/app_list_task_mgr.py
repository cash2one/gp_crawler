#coding: utf-8

import os
import sys
import time
import logging
import traceback
from urllib import urlencode
from multiprocessing.dummy import Pool

from impala.dbapi import connect

sys.path.append("../..")
import sync_to_hdfs
from lib import utils
from lib import const

def set_log():
    """
    set log format
    """
    if not os.path.exists('log'):
        os.mkdir('log')

    logging.basicConfig(level=logging.INFO,
            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S',
            filename='log/notice.log',
            filemode='a')

class Items(object):
    def __init__(self, country, category, feeds, items, sub_category="overall"):
        self.country = country
        self.category = category
        self.feeds = feeds
        self.sub_category = sub_category
        self.items = items


class AppListMgr(object):
    def __init__(self):
        self.impala_client = None
        self.countrys = [
                "id", "us",
                ]
        self.sub_category = [
                #"apps_topselling_new_paid",
                "apps_topselling_new_free",
                ]
        self.category = [
                #"app",
                #"overall",
                "game"
                ]
        self.results = {}
        self.result_dir = "./data/"

        if not os.path.exists(self.result_dir):
            os.mkdir(self.result_dir)

        self.result_file = self.result_dir + "result.list"
        self.url = "http://127.0.0.1:8812/api/googleplay/list"

    #def connect_to_impala(self):
    #    return connect(
    #            host = "hkg02-i18n-cdh000.hkg02.baidu.com",
    #            port = 21050,
    #            database = "mobomarket",
    #            )

    def worker(self, country, category, sub_category):
        paras = {
                "country": country,
                "category": category.upper(),
                "subCategory": sub_category
                }
        qs = urlencode(paras)

        url = "%s?%s" % (self.url, qs)

        try:
            res = utils.requests_ex(url)
        except Exception as e:
            logging.error("send request to googly2 fail: %s, error:%s" % (url, e.message))
            return

        print url

        if res.status_code != 200:
            logging.error("googleplay2 return %d, error:%s" % (res.status_code, res.text))
            self.send_mail_to_gonghao()
            return

        apps = res.text.split(';')
        items = Items(
                country = country,
                category = category,
                feeds = sub_category,
                items = apps
                )

        try:
            self.dump_results_to_impala(items)
        except Exception as e:
            logging.error("dump result to impala fail, error:%s" % (e.message))
            self.send_mail_to_gonghao()

    def send_mail_to_gonghao(self):
        utils.send_mail(
                subject="获取榜单信息失败",
                content=url,
                receivers=["gonghao"],
                sender="gonghao"
                )

    def dump_results_to_impala(self, data):
        timestamp = utils.timestamp()
        topcharts_local = os.path.join(const.DATA_PATH, "topcharts_%s_%s" % (timestamp, data.country))
        items = [(data.category, data.sub_category, data.feeds, pkg, idx + 1) for idx, pkg in enumerate(data.items)]
        with open(topcharts_local, 'w') as fd:
            def print_to_hdfs(item):
                return '\t'.join(map(lambda x: str(x), item))
            fd.write('\n'.join(map(lambda x: print_to_hdfs(x), items)))
        sync_to_hdfs.sync_by_date(timestamp)

    def worker_helper(self, args):
        return self.worker(*args)

    def do(self):
        """
        send request to googleplay2 to get list
        """
        pool = Pool(5)
        app_lists = []
        app_lists = [
                (x, y, z)
                for x in self.countrys for y in self.category for z in self.sub_category
                ]

        pool.imap_unordered(self.worker_helper, app_lists)

        pool.close()
        pool.join()

def main():
    """
    generate app list file for crawler
    """

    obj = AppListMgr()
    obj.do()


if __name__ == "__main__":
    set_log()
    sys.exit(main())
