#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: metadata.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/07/23 16:51:45
"""
import copy
import re
import _mysql
import HTMLParser
from lib import const
from lib import utils

class Request(object):
    """ 抓取请求
    """
    def __init__(self):
        self.package = ''
        self.task_type = const.TaskType.DEFAULT
        self.force_update = 0
        self.task_name = ''
        self.job_id = 0

    def __str__(self):
        content = 'package:%s, task_type:%d, force_update:%d, task_name:%s, job_id:%d' % (
            self.package, self.task_type, self.force_update, self.task_name, self.job_id)
        return content


class Session(object):
    """ 爬取过程中临时保存的变量
        package: 用户指定的app包名
        packageid: 该package在db中对应保存的唯一id
        task_type: 当前任务类型, 包括默认、下载apk、只下载详情
    """
    def __init__(self):
        self.package = ''
        self.packageid = 0
        self.task_type = const.TaskType.DEFAULT

        self.action = const.Action.DEFAULT
        # 用来标识, 只更新详情, 不更新doc, 且不更改state
        self.fix_action = const.Action.DEFAULT
        self.exist_in_db = False
        self.multiapk = 0
        self.is_channel = False
        self.all_download_pid = 0
        self.free = True
        self.src_state = -1
        self.db_lang_list = []
        self.db_version = None
        self.db_multi_version_list = []
        self.db_sname_list = []
        self.new_db_version = None
        self.detect_time = ''

        self.lang_details = LangDetails()
        self.apks = Apks()

        self.db_set = None
        self.pre_scan_res = None
        self.multi_version_scan_res = []


class DbSet(object):
    """ db里数据集合
    """
    def __init__(self, db_fd):
        self.package = None
        self.doc_list = {}
        self.apk_version_info_list = {}

        self.db = db_fd

    def __del__(self):
        if self.db is not None:
            del self.db

    def clear_package(self, packageid):
        """ 清理app数据
        """
        cmd = 'delete from package where packageid=%d' % (packageid)
        self.db.execute(cmd)
        cmd = 'delete from package_ext where packageid=%d' % (packageid)
        self.db.execute(cmd)
        cmd = 'delete from app_purchase_info where packageid=%d' % (packageid)
        self.db.execute(cmd)
        cmd = 'delete from doc where packageid=%d' % (packageid)
        self.db.execute(cmd)
        cmd = 'delete from apk_version_info where packageid=%d' % (packageid)
        self.db.execute(cmd)

    def load_package_table(self, package_name):
        """ 返回获取的行数
        """
        pt = PackageTable.get_instance()
        pt.package = package_name

        cmd = """
            SELECT package, packageid, multiapk, state, isChannel, all_download_pid
            FROM package
            WHERE package='%s'
        """ % (package_name)
        self.db.execute(cmd)
        row = self.db.fetchone()
        if row is not None:
            pt.package, pt.packageid, pt.multiapk, pt.state, pt.is_channel, pt.all_download_pid = row
            cmd = 'SELECT source_online, free FROM package_ext WHERE packageid=%d' % (pt.packageid)
            self.db.execute(cmd)
            ext_row = self.db.fetchone()
            if ext_row is not None:
                pt.source_online, pt.free = ext_row
        self.package = pt
        return 0 if row is None else 1

    def insert_package_table(self):
        """ 新增package纪录, 返回自增的packageid
        """
        self.db.execute(self.package.insert())
        cmd = 'SELECT packageid FROM package where package="%s"' % (self.package.package)
        self.db.execute(cmd)
        row = self.db.fetchone()
        if row is None:
            raise error.DbError('package not in db, [%s]' % (self.package.package))
        self.package.packageid = row[0]

        self.upsert_package_ext_table()
        self.upsert_paid_info_table()
        return self.package.packageid

    def update_package_table(self):
        """ 更新package
        """
        self.db.execute(self.package.update())
        self.upsert_package_ext_table()
        self.upsert_paid_info_table()

    def update_package_table_by_channel(self):
        """ 更新渠道包的package表
        """
        self.db.execute(self.package.update_by_channel())
        self.upsert_package_ext_table()
        self.upsert_paid_info_table()

    def upsert_package_ext_table(self):
        """ 新增或更新package_ext
        """
        self.db.execute(self.package.search_ext())
        row = self.db.fetchone()
        if row is not None:
            self.db.execute(self.package.update_ext())
        else:
            self.db.execute(self.package.insert_ext())

    def upsert_paid_info_table(self):
        """ 新增或更新app_purchase_info
            先删除再新增
        """
        self.db.execute(self.package.delete_paid_info())
        for cmd in self.package.insert_paid_info():
            self.db.execute(cmd)

    def load_doc_table_list(self, packageid):
        """ 加载packageid对应的所有doc纪录
        """
        cmd = """
            SELECT packageid, lang, versioncode, versionname, sname, man_edit, webp,
                url, signmd5, apkmd5, download_inner, minsdk, maxsdk, cpu, size,
                permission, updatetime, buildtime, source, platform_version, 
                src_size, dirty, sname_lang
            FROM doc
            WHERE packageid=%d
        """ % (packageid)
        self.db.execute(cmd)
        for row in self.db.fetchall():
            dt = DocTable.get_instance()
            dt.packageid, dt.lang, dt.version_code, dt.version_name, dt.sname, \
                man_edit, dt.webp, dt.url, dt.sign_md5, dt.apk_md5, dt.download_inner, \
                dt.min_sdk, dt.max_sdk, dt.cpu, dt.size, dt.permission, dt.update_time, \
                dt.build_time, dt.source, dt.platform_version, \
                dt.src_size, dt.dirty, dt.sname_lang = row
            dt.man_edit = man_edit.splitlines()
            self.doc_list.update({dt.lang: dt})
        return len(self.doc_list)

    def insert_doc_table(self, doc):
        """ 新增doc纪录
        """
        self.db.execute(doc.insert())

    def update_doc_table(self, doc):
        """ 更新doc纪录
        """
        self.db.execute(doc.update())

    def delete_doc_table(self, doc):
        """ 删除doc纪录
        """
        self.db.execute(doc.delete())

    def load_apk_version_info_list(self, packageid):
        """ 加载多版本信息
        """
        cmd = """
            SELECT package, packageid, versioncode, versionname
            FROM apk_version_info
            WHERE packageid=%d
        """ % (packageid)
        self.db.execute(cmd)
        for row in self.db.fetchall():
            avi = ApkVersionInfoTable()
            avi.package, avi.packageid, avi.version_code, avi.version_name = row
            self.apk_version_info_list.update({avi.version_code: avi})
        return len(self.apk_version_info_list)

    def insert_apk_version_info_table(self, apk_version_info):
        """ 新增多版本纪录
        """
        self.db.execute(apk_version_info.insert())

    def update_apk_version_info_table(self, apk_version_info):
        """ 更新多版本纪录
        """ 
        self.db.execute(apk_version_info.update())


class PackageTable(object):
    """ package db操作类
    """
    @classmethod
    def get_instance(cls):
        """ 获取PacakageTable实例
        """
        return PackageTable()

    def __init__(self):
        self.package = ''
        self.packageid = 0
        self.type = ''
        self.cate_id = 0
        self.app_cate = ''
        self.state = 0
        self.all_download_pid = 0
        self.score = 0
        self.score_count = 0
        self.video_url = ''
        self.score_detail = ''
        self.content_rating = 0
        self.comment_count = 0
        self.creator = ''
        self.develop_email = ''
        self.develop_website = ''
        self.multi_content_rating = ''
        self.source_online = 1
        self.free = 1
        self.uptime = ''
        self.full_type = 0
        self.multiapk = 0
        self.is_channel = 0
        self.create_time = ''

        self.paid_info = []

    def __setattr__(self, name, value):
        if type(value) == unicode:
            value = value.encode('utf8')
        if type(value) == str:
            value = _mysql.escape_string(value)
        super(PackageTable, self).__setattr__(name, value)

    def search_ext(self):
        """ 查询package_ext
        """
        cmd = 'SELECT * FROM package_ext WHERE packageid=%d' % (self.packageid)
        return cmd

    def insert(self):
        """ 新增package
        """
        cmd = """
            INSERT INTO package(package, type, cateid, app_cate, state, 
                all_download_pid, score, score_count, video_url, score_detail,
                content_rating, creator, multi_content_rating, comment_count, uptime,
                createtime, full_type, multiapk)
            VALUES('%s', '%s', %d, %d, %d,
                %d, %d, %d, '%s', '%s',
                %d, '%s', '%s', %d, '%s',
                '%s', %d, %d)
        """ % (self.package, self.type, self.cate_id, self.app_cate, self.state, 
            self.all_download_pid, self.score, self.score_count, self.video_url, self.score_detail,
            self.content_rating, self.creator, self.multi_content_rating, self.comment_count,
            self.uptime, self.create_time, self.full_type, self.multiapk)
        return cmd

    def insert_ext(self):
        """ 新增package_ext
        """
        cmd = """
            INSERT INTO package_ext(package, packageid, source_online, free, dev_email, dev_website)
            VALUES('%s', %d, %d, %d, '%s', '%s')
        """ % (self.package, self.packageid, self.source_online, self.free, self.develop_email,
            self.develop_website)
        return cmd

    def insert_paid_info(self):
        """ 新增付费信息
        """
        cmds = []
        for currency_code, formatted_amount in self.paid_info: 
            cmd = """
                INSERT INTO app_purchase_info(packageid, currency_code, formatted_amount)
                VALUES(%d, '%s', %.2f) 
            """ % (self.packageid, currency_code, formatted_amount)
            cmds.append(cmd)
        return cmds

    def update(self):
        """ 更新package
        """
        cmd = """
            UPDATE package
            SET type='%s', cateid=%d, app_cate=%d, state=%d, all_download_pid=%d,
                score=%d, score_count=%d, video_url='%s', score_detail='%s', content_rating=%d,
                creator='%s', multi_content_rating='%s', comment_count=%d, uptime='%s',
                full_type=%d, multiapk=%d
            WHERE package="%s"
        """ % (self.type, self.cate_id, self.app_cate, self.state, self.all_download_pid, 
            self.score, self.score_count, self.video_url, self.score_detail, self.content_rating,
            self.creator, self.multi_content_rating, self.comment_count, self.uptime, 
            self.full_type, self.multiapk, self.package)
        return cmd

    def update_by_channel(self):
        """ 渠道包更新package, 不更新full_type
        """
        cmd = """
            UPDATE package
            SET type='%s', cateid=%d, app_cate=%d, state=%d, all_download_pid=%d,
                score=%d, score_count=%d, video_url='%s', score_detail='%s', content_rating=%d,
                creator='%s', multi_content_rating='%s', comment_count=%d, uptime='%s',
                multiapk=%d
            WHERE package="%s"
        """ % (self.type, self.cate_id, self.app_cate, self.state, self.all_download_pid, 
            self.score, self.score_count, self.video_url, self.score_detail, self.content_rating,
            self.creator, self.multi_content_rating, self.comment_count, self.uptime, 
            self.multiapk, self.package)
        return cmd

    def update_ext(self):
        """ 更新package_ext
        """
        cmd = """
            UPDATE package_ext 
            SET packageid=%d, source_online=%d, free=%d, dev_email='%s', dev_website='%s'
            WHERE package='%s'
        """ % (self.packageid, self.source_online, self.free, self.develop_email,
            self.develop_website, self.package)
        return cmd

    def delete_ext(self):
        """ 删除package_ext
        """
        cmd = 'DELETE FROM package_ext WHERE packageid=%d' % (self.packageid)

    def delete_paid_info(self):
        """ 删除app_purchase_info
        """
        cmd = 'DELETE FROM app_purchase_info WHERE packageid=%d' % (self.packageid)
        return cmd


class DocTable(object):
    """ Doc表操作类
    """
    @classmethod
    def get_instance(cls):
        """ 获取DocTable实例
        """
        return DocTable()

    def __init__(self):
        self.packageid = 0
        self.lang = ''
        self.url = ''
        self.version_code = 0
        self.version_name = 0
        self.sname = ''
        self.whatsnew = ''
        self.brief = ''
        self.icon = ''
        self.icon65 = ''
        self.iconlow = ''
        self.iconhigh = ''
        self.iconhdpi = ''
        self.icon256 = ''
        self.screenshot = ''
        self.screenshotlow = ''
        self.screenshothigh = ''
        self.iconalading = ''
        self.sname_lang = ''
        self.banner = ''

        self.sign_md5 = ''
        self.apk_md5 = ''
        self.download_inner = ''
        self.min_sdk = 1
        self.max_sdk = 10000
        self.cpu = ''
        self.size = 0
        self.permission = ''
        self.update_time = ''
        self.build_time = ''

        self.source = ''
        self.platform_version = '2.2'
        self.man_edit = []
        self.webp = 1

        self.src_size = 0
        self.dirty = 0

    def __setattr__(self, name, value):
        if not hasattr(self, name) or name == 'man_edit':
            super(DocTable, self).__setattr__(name, value)
        else:
            if name not in self.man_edit:
                if type(value) == unicode:
                    value = value.encode('utf8')
                if type(value) == str:
                    value = _mysql.escape_string(value)
                if name == 'sname':
                    try:
                        html_parser = HTMLParser.HTMLParser()
                        value =  html_parser.unescape(value)
                    except:
                        pass
                super(DocTable, self).__setattr__(name, value)

    def insert(self):
        """ 新增命令
        """  
        cmd = """
            INSERT INTO doc(packageid, lang, url, sname, whatsnews, brief, 
                apkmd5, signmd5, versioncode, versionname, minsdk, 
                maxsdk, source, platform_version, updatetime, 
                buildtime, size, download_inner, permission, icon, 
                icon65, iconlow, iconhigh, icon256, iconhdpi, screenshot, 
                screenshotlow, screenshothigh, iconalading, cpu, webp, banner,
                src_size, dirty, sname_lang)
            VALUES(%d, '%s', '%s', '%s', '%s', '%s', 
                '%s', '%s', %d, '%s', %d, 
                 %d, '%s', '%s', '%s', 
                '%s', %d, '%s', '%s', '%s', 
                '%s', '%s', '%s', '%s', '%s', '%s',
                '%s', '%s', '%s', '%s', %d, '%s',
                '%s', %d, '%s')
        """ % (self.packageid, self.lang, self.url, self.sname, self.whatsnew, self.brief,
            self.apk_md5, self.sign_md5, self.version_code, self.version_name, self.min_sdk,
            self.max_sdk, self.source, self.platform_version, self.update_time,
            self.build_time, self.size, self.download_inner, self.permission, self.icon, 
            self.icon65, self.iconlow, self.iconhigh, self.icon256, self.iconhdpi, self.screenshot,
            self.screenshotlow, self.screenshothigh, self.iconalading, self.cpu, self.webp, self.banner,
            self.src_size, self.dirty, self.sname_lang)
        return cmd

    def update(self):
        """ 更新命令
        """
        cmd = """
            UPDATE doc 
            SET sname='%s', whatsnews='%s', brief='%s', apkmd5='%s', signmd5='%s',
                versioncode=%d, versionname='%s', minsdk=%d, maxsdk=%d, source='%s',
                platform_version='%s', updatetime='%s', buildtime='%s', size=%d, 
                download_inner='%s', permission='%s', icon='%s', icon65='%s', iconlow='%s',
                iconhigh='%s', icon256='%s', iconhdpi='%s', screenshot='%s', screenshotlow='%s',
                screenshothigh='%s', iconalading='%s', cpu='%s', webp=%d, sname_lang='%s', banner='%s'
            WHERE packageid=%d AND lang='%s'
        """ % (self.sname, self.whatsnew, self.brief, self.apk_md5, self.sign_md5, 
            self.version_code, self.version_name, self.min_sdk, self.max_sdk, self.source,
            self.platform_version, self.update_time, self.build_time, self.size, 
            self.download_inner, self.permission, self.icon, self.icon65, self.iconlow, 
            self.iconhigh, self.icon256, self.iconhdpi, self.screenshot, self.screenshotlow,
            self.screenshothigh, self.iconalading, self.cpu, self.webp, self.sname_lang, self.banner,
            self.packageid, self.lang)
        return cmd

    def delete(self):
        """ 删除命令
        """
        cmd = 'DELETE FROM doc WHERE packageid=%d AND lang="%s"' % (self.packageid, self.lang)
        return cmd


class ApkVersionInfoTable(object):
    """ 多版本
    """
    def __init__(self):
        self.pacakge = ''
        self.packageid= 0
        self.version_code = 0
        self.version_name = ''
        self.whatsnew = ''
        self.download_inner = ''
        self.apk_md5 = ''
        self.sign_md5 = ''
        self.size = 0
        self.min_sdk = 1
        self.max_sdk = 10000
        self.target_sdk = 0
        self.library = ''
        self.compatible_screens = ''
        self.small_screen = 1
        self.normal_screen = 1
        self.large_screen = 1
        self.xlarge_screen = 1
        self.gl_version = 0
        self.cpu = ''
        self.deleted = 0
        self.source = ''
        self.create_time = ''
        self.update_time = ''

    def insert(self):
        """ 新增命令
        """
        cmd = """
            REPLACE INTO apk_version_info(package, packageid, versioncode, versionname,
                whatsnews, download_inner, apkmd5, signmd5, size, minsdk, maxsdk, 
                targetsdk, library, compatible_screens, small_screen,
                normal_screen, large_screen, xlarge_screen, gl_version, cpu, deleted,
                source, createtime, updatetime)
            VALUES('%s', %d, %d, '%s', '%s', '%s', '%s', '%s', %d, %d, %d, %d, '%s',
                '%s', %d, %d, %d, %d, %d, '%s', %d, '%s', '%s', '%s')
        """ % (self.package, self.packageid, self.version_code, self.version_name, 
            self.whatsnew, self.download_inner, self.apk_md5, self.sign_md5, self.size, 
            self.min_sdk, self.max_sdk, self.target_sdk, self.library, self.compatible_screens, 
            self.small_screen, self.normal_screen, self.large_screen, self.xlarge_screen, 
            self.gl_version, self.cpu, self.deleted, self.source, self.create_time,
            self.update_time)
        return cmd

    def update(self):
        """ 更新命令
        """
        cmd = """
            UPDATE apk_version_info
            SET versionname='%s', download_inner='%s', apkmd5='%s', signmd5='%s', size=%d, 
                minsdk=%d, maxsdk=%d, targetsdk=%d, library='%s', compatible_screens='%s',
                small_screen=%d, normal_screen=%d, large_screen=%d, xlarge_screen=%d,
                gl_version=%d, cpu='%s', deleted=%d, source='%s', updatetime='%s'
            WHERE packageid=%d AND versioncode=%d
        """ % (self.version_name, self.download_inner, self.apk_md5, self.sign_md5, self.size, 
            self.min_sdk, self.max_sdk, self.target_sdk, self.library, self.compatible_screens, 
            self.small_screen, self.normal_screen, self.large_screen, self.xlarge_screen, 
            self.gl_version, self.cpu, self.deleted, self.source, self.update_time, self.packageid,
            self.version_code)
        return cmd


class Version(object):
    """ 封装版本
    """
    def __init__(self, version_code=0, version_name=''):
        self.code = version_code
        self.name = version_name
        if type(self.name) == unicode:
            self.name = self.name.encode('utf8')

    def __str__(self):
        return '(%s, %s)' % (str(self.code), str(self.name))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.code == other.code and self.name == other.name

    def __cmp__(self, other):
        return cmp(self.code, other.code) or \
            (len(self.name) >= len(other.name) and cmp(self.name, other.name))


class CompatibleDetail(object):
    """ app适配详情
        Args:
            compatible_datail: 预扫描返回的适配详情. type: _scan_message.CompatibleDetail
            scan_app_detail: app相关的详情
    """
    @classmethod
    def get_instance(cls, data):
        """ 获取CompatibleDetail实例
        """
        return CompatibleDetail(data)

    def __init__(self, compatible_detail):
        self.res = compatible_detail
        self.scan_app_detail = self.res.scanAppDetail

    def __str__(self):
        content = 'account: %s_%s, proxies: %s, version_code: %d, version_name: %s, ' \
            'uptime: %s, varies_by_account: %d' % (str(self.account.email), 
            str(self.account.androidId), str(self.proxies), self.version.code, self.version.name, 
            self.src_updatetime, int(self.varies_by_account))
        return content

    @property
    def titles(self):
        """
        sname：type:scan_app_detail.detail.langDetails[index].appDescription.title
        """
        def handle_title(lang_detail):
            """
            handle scan reponse to match mysql, see:
            http://cenalulu.github.io/linux/character-encoding/
            """
            try:
                sname = re.sub(u"[^\u0000-\uD7FF\uE000-\uFFFF]", \
                        "", lang_detail.appDescription.title, re.UNICODE)
            except Exception as err:
                sname = lang_detail.appDescription.title
            if type(sname) == unicode:
                sname = sname.encode('utf-8')
            if type(sname) == str:
                sname = _mysql.escape_string(sname)
            try:
                html_parser = HTMLParser.HTMLParser()
                sname =  html_parser.unescape(sname)
            except:
                pass
            return sname

        return map(handle_title, self.scan_app_detail.detail.langDetails)

    @property
    def account(self):
        """ 账号. type: _app_message.Account
        """
        return self.res.account

    @property
    def proxies(self):
        """ 代理
        """
        return self.res.proxies

    @property
    def app_details(self):
        """ app详情. type: _app_message.Detail
        """ 
        return self.scan_app_detail.detail

    @property
    def download_info(self):
        """ 下载信息. type: _app_message.DownloadInfo
        """
        return self.scan_app_detail.downloadInfo

    @property
    def version(self):
        """ 当前适配信息版本. type: Version
        """
        return Version(self.scan_app_detail.detail.appDetail.versionCode,
            self.scan_app_detail.detail.appDetail.versionName)

    @property
    def size(self):
        """ 当前适配信息apk大小. type: int64
        """
        return self.scan_app_detail.detail.appDetail.installationSize

    @property
    def permission(self):
        """ apk申请注册的权限
        """
        return '|'.join(self.scan_app_detail.detail.appDetail.permission)

    @property
    def src_updatetime(self):
        """ apk在源站更新时间
        """
        try:
            return utils.convert_time_formatter(
                self.scan_app_detail.detail.appDetail.uploadDate, '%b %d, %Y', '%Y-%m-%d')
        except:
            return ''

    @property
    def offer(self):
        """ offer信息
        """
        return self.scan_app_detail.detail.appDetail.offer

    @property
    def varies_by_account(self):
        """ app因版本而已. type: boolean
        """
        return self.scan_app_detail.detail.appDetail.variesByAccount

    @property
    def compatible_code(self):
        """ app与当前账号适配情况. type: int
        """
        return self.scan_app_detail.detail.appDetail.availability.restriction


class LangDetails(object):
    """ 多语言详情
    """
    class Detail(object):
        """ 单个语言详情
        """ 
        def __init__(self):
            self.lang = ''
            self.sname = ''
            self.brief = ''
            self.whatsnew = ''
            self.src_icon = ''
            self.src_screenshots = []
            self.src_banners = []
            self.videos = []

            self.icon65 = ''
            self.icon = ''
            self.iconlow = ''
            self.iconhigh = ''
            self.icon256 = ''
            self.iconhdpi = ''

            self.screenshotlow = ''
            self.screenshot = ''
            self.screenshothigh = ''
            self.iconalading = ''

            self.banner = ''

        def __str__(self):
            content = 'lang:%s\nsname:%s\nbrief:%s\nwhatsnew:%s\nicon65:%s\nicon:%s\n' \
                'iconlow:%s\niconhigh:%s\nicon256:%s\niconhdpi:%s\nscreenshotlow:%s' \
                'screenshot:%s\nscreenshothigh:%s\niconaldaing:%s' % (self.lang, self.sname,
                self.brief, self.whatsnew, self.icon65, self.icon, self.iconlow, self.iconhigh,
                self.icon256, self.iconhdpi, self.screenshotlow, self.screenshot,
                self.screenshothigh, self.iconalading)
            return content.encode('utf8')

        @property
        def images(self):
            """ 所有图片
            """
            images = copy.deepcopy(self.src_screenshots)
            images.append(self.src_icon)
            return images

    def __init__(self):
        self._details = {}

    def add(self, detail):
        """ 增加一种语言详情
        """
        if detail.lang == 'pt':
            detail.lang = 'br'
        self._details.update({detail.lang: detail})

    def delete(self, lang):
        """ 删除一种语言详情
        """
        if lang in self.langs:
            del self._details[lang]

    @property
    def langs(self):
        """ 所有语言列表. type: list
        """
        return self._details.keys()

    @property
    def details(self):
        """ 所有语言列表. type: list
        """
        return self._details.values()

    @property
    def images(self):
        """ 所有图片. type: list
        """
        return list(set(reduce(lambda x, y: x.images + y.images, self._details.values())))

    @property
    def icons(self):
        """ 所有icon. type: list
        """
        return list(set(map(lambda x: x.src_icon, self._details.values())))

    @property
    def banners(self):
        """返回所有banner
        """
        images = []
        for detail in self.details:
            images.extend(detail.src_banners)
        return list(set(images))

    @property
    def screenshots(self):
        """ 所有截屏. type: list
        """
        images = []
        for detail in self.details:
            images.extend(detail.src_screenshots)
        return list(set(images))

    def get_detail_by_lang(self, lang):
        """ 根据语言获取对应详情. type: LangDetails.Details
        """
        return self._details.get(lang)


class ApkFeature(object):
    """ apk文件的信息
    """
    def __init__(self):
        self.parse_manifest_fail = False
        # basic information
        self.pack_name = ""
        self.version_code = 0
        self.version_name = ""
        # uses-sdk
        self.min_sdk = 1            # 最小支持的sdk版本
        self.max_sdk = 10000        # 最大支持的sdk版本
        self.target_sdk = 0         # 目标sdk，缺省值未min_sdk
        # screen
        self.small_screens  = 1      # 小屏幕
        self.normal_screens = 1      # 中等屏幕
        self.large_screens  = 1      # 大屏幕
        self.xlarge_screens = 1      # 超大屏幕（pad）
        self.compatible_screens = []
        # uses-configuration
        self.req_five_way_nav  = 0   # 需要五向导航控制
        self.req_hard_keyboard = 0   # 需要硬键盘
        self.req_keyboard_type = 0   # 键盘类型
        self.req_navigation = 0      # 导航设备
        self.req_touch_screen = 0    # 触摸屏
        # uses-feature
        self.uses_feature_list = []     # feature列表
        # opengl
        self.gl_es_version = 0
        # uses-library
        self.uses_library = [
            ["com.google.android.maps", 0],
            ["android.test.runner", 0],
            ["com.sec.android.app.multiwindow", 0],
            ["com.google.android.gcm.maps", 0],
            ["com.sony.smallapp.framework", 0],
            ["com.amazon.device.home", 0],
            ["com.sonymobile.camera.addon.api", 0],
            ["com.android.future.usb.accessory", 0],
            ["com.google.android.media.effects", 0],
            ["com.google.android.gms.maps.SupportMapFragment", 0]]
        self.support_cpu = ''
        self.sign_md5 = ''

    @property
    def uses_library_str(self):
        """ 返回所依赖lib. type: str
        """
        return ';'.join(x[0] for x in self.uses_library if x[1] == 1)

    @property
    def compatible_screens_str(self):
        """ 返回兼容屏幕. type: str
        """
        return ';'.join(map(lambda x: '%s,%s' % (x[0], x[1]), self.compatible_screens))

    def dump(self):
        """ 字符串输出apk feature
        """
        output_str = ";".join([
            "pack_name: %s" % self.pack_name,
            "version_code: %s" % self.version_code,
            "version_name: %s" % self.version_name,
            "min_sdk: %s" % self.min_sdk,
            "target_sdk: %s" % self.target_sdk,
            "max_sdk: %s" % self.max_sdk,
            "small_screens: %s" % self.small_screens,
            "normal_screens: %s" % self.normal_screens,
            "large_screens: %s" % self.large_screens,
            "xlarge_screens: %s" % self.xlarge_screens,
            "compatible_screens: %s" % self.compatible_screens,
            "gl_es_version: %s" % self.gl_es_version,
            "uses_library: %s" % self.uses_library,
            'sign_md5: %s' % self.sign_md5,
            'support_cpu: %s' % (self.support_cpu)
            ])
        return output_str


class Apks(object):
    """ 所有下载的apk文件
    """
    class Detail(object):
        """ 单个apk文件的详情
        """
        def __init__(self):
            self.version_code = 0
            self.version_name = ''
            self.download_inner = ''
            self.download_cost_time = 0
            self.apk_md5 = ''
            self.apk_size = 0
            self.permission = ''
            self.src_updatetime = ''
            self.feature = ApkFeature()

        def __str__(self):
            content = 'version_code: %d, version_name: %s, download_inner: %s, ' \
                'apk_md5: %s, apk_size: %d, feature: %s' % (self.version_code, 
                self.version_name, self.download_inner, self.apk_md5, self.apk_size,
                self.feature.dump())
            return content

    def __init__(self):
        self._details = {}

    def __str__(self):
        content = '\n'.join(map(lambda x: x.__str__(), self._details.values()))
        return content

    @property
    def details(self):
        """ 所有apk的详情. type: list
        """
        return self._details.values()

    @property
    def version_code_list(self):
        """ 所有apk对应的版本号列表. type: list
        """
        return self._details.keys()

    def add(self, detail):
        """ 增加一个apk
        """
        self._details.update({detail.version_code: detail})

    def get_detail_by_version_code(self, version_code):
        """ 根据版本号获取对应apk的详情
        """
        return self._details.get(version_code)

if __name__ == '__main__':
    doc = DocTable()
    doc.sname = '1'
    print doc.sname
    doc.man_edit = ['sname']
    doc.sname = '2'
    print doc.sname

    version1 = [Version(1, '2')]
    version2 = [Version(1, '2')]
    print list(set(version1) - set(version2))
