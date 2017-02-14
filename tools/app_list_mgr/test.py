#coding: utf-8

from impala.dbapi import connect

def connect_to_impala():
    return connect(
            host = "hkg02-i18n-cdh002.hkg02.baidu.com",
            port = 21050,
            database = "mobomarket",
            )

conn = connect_to_impala()
cur = conn.cursor()

#sql = "select * from i18n_googleplay_topcharts_raw limit 1"
#sql = "INSERT INTO i18n_googleplay_topcharts_raw VALUES('app', 'overall', 'test', 'gonghaotest', '444', '20001111', 'us')"

sql = 'insert into mobomarket.i18n_googleplay_topcharts_raw(category, sub_category, feeds, ' \
    'package, rank) partition(dt="20160127", country="tw") values ("zz", "xxx", "aaa", "zzz", "aaa")'

cur.execute(sql)
res = cur.fetchall()

print res

cur.close()
conn.close()
