#coding: utf-8
"""
query impala, get today channel update info, send email to pm
"""
import os
import sys
import time
import logging
import datetime
sys.path.append("..")

from impala.dbapi import connect

from lib import utils

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


def main():
    """
    send notice to pm, if channel package update
    """
    host = "hkg02-i18n-cdh000.hkg02.baidu.com"
    port = 21050
    database = "mobomarket"
    table = "mm_appcrawler_raw "
    items = list()

    yestdate = datetime.datetime.now() - datetime.timedelta(days=1)
    dt = yestdate.strftime("%Y%m%d")

    try:
        conn = connect(host=host, port=port, database=database)
        cur = conn.cursor()

        query="""select pack_name, pack_id, old_version_name,
                    new_version_name, old_version_code, new_version_code 
                    from %s where dt='%s' and channel=1""" % \
                            (table, dt)

        def cmp_version_name(v1, v2):
            return True if len(v1) >= len(v2) and cmp(v1, v2) >= 0 else False

        def cmp_version_code(v1, v2):
            return True if v1 >= v2 else False

        cur.execute(query)
        for item in cur.fetchall():
            _, _, old_version_name, new_version_name, old_version_code, new_version_code = item
            if not cmp_version_code(old_version_code, new_version_code) or \
                    not cmp_version_name(old_version_name, new_version_name):
                        line = '\t'.join(map(lambda x: str(x), item))
                        items.append(line)

        if len(items) > 0:
            content = '\n'.join(items)
            utils.send_mail(subject="渠道包更新通知", content=content, \
                receivers=["gonghao", "zhouyingzhi"], sender="gonghao")

        cur.close()
        conn.close()
    except Exception as e:
        logging.error("send notice to pm fail: %s" % e.message)
        utils.send_mail(subject="渠道包更新失败通知", content="更新失败", \
                receivers=["gonghao"], sender="gonghao")
        return -1
    else:
        logging.info("send notice to pm success, total:%d" % len(items))

    return 0

if __name__ == "__main__":
    set_log()
    sys.exit(main())
