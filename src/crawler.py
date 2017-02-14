#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: crawler.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/07/23 15:45:26
"""
import os
import time
import urllib
import random
import base64
import ConfigParser
import commands
import StringIO
import shutil
import json

from proto import storage_pb2 as _storage_message
from proto import image_pb2 as _image_message

from lib import const
from lib import error
from lib import utils
from src import log
from src import db
from src import metadata
from src import manifest

class Crawler(object):
    """ 抓取类
        Attributes:
            request: 抓取请求参数
            session: 抓取临时数据对象
            log: 日志对象
            db: 数据库连接对象
            conf_parse: 配置文件操作对象. type: ConfigParser
            server_url_dict: 保存调用的外部服务. type: dict
            auth_dict: 权限校验. type: dict
            mttp_config_dict: 上传到存储平台, mttp参数配置
            tmp_dir: 当前抓取临时目录, 结束时一律清楚

            conf_file: 配置文件路径, 默认./conf/crawler.ini
            lang_list: app详情语言列表
            apk_source: app来源

    """
    def __init__(self, conf_file=None):
        self.request = metadata.Request()
        self.session = metadata.Session() 
        self.log = log.Log()

        self.db = None
        self.conf_parse = ConfigParser.SafeConfigParser()

        self.server_url_dict = {}
        self.auth_dict = {}
        self.mttp_config_dict = {}

        self.tmp_dir = os.path.join(const.TMP_PATH, '{0}_{1}_{1}'.format( \
            int(time.time()), utils.randint(0, 100)))
        utils.init_dir_path(self.tmp_dir)

        self.conf_file = conf_file or os.path.join(const.CONF_PATH, 'crawler.ini')

        self.lang_list = ('en_US', 'id_ID', 'pt_BR', 'ar', 'th', 'ru', 'vi', 'es', 
            'zh_TW', 'ms', 'hi', 'ja', 'de', 'fr', 'it', 'tr')

        self.apk_source = ''

    def __del__(self):
        if self.db is not None:
            del self.db
        if os.path.isdir(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def init(self):
        """ 加载配置文件, 并初始化相关属性
        """
        self.conf_parse.read(self.conf_file)
        host = self.conf_parse.get('db', 'host')
        port = self.conf_parse.getint('db', 'port')
        user = self.conf_parse.get('db', 'user')
        password = self.conf_parse.get('db', 'password')
        db_name = self.conf_parse.get('db', 'db_name')

        self.db = db.DbHelper(host=host, port=port, user=user, password=password,
            db_name=db_name)
        self.session.db_set = metadata.DbSet(self.db)

        self.server_url_dict = {
            'image_resize': self.conf_parse.get('server', 'image_resize_url'),
            'storage_upload': self.conf_parse.get('server', 'storage_upload_url'),
            'mm_app_detail': self.conf_parse.get('server', 'mm_app_detail_url'),
            'mm_apk_download': self.conf_parse.get('server', 'mm_apk_download_url'),
            'increment_system': self.conf_parse.get('server', 'increment_system_url'),
            'security_scan': self.conf_parse.get('server', 'security_scan_url'),
            'notice_91': self.conf_parse.get('server', 'notice_91_url'),
            'detect_lang': self.conf_parse.get('server', 'detect_lang_url')}

        self.auth_dict = {
            'image_server_name': self.conf_parse.get('auth', 'image_server_name'),
            'image_server_token': self.conf_parse.get('auth', 'image_server_token'),
            'storage_server_name': self.conf_parse.get('auth', 'storage_server_name'),
            'storage_server_token': self.conf_parse.get('auth', 'storage_server_token')}
        self.mttp_config_dict = {
            'port': int(self.conf_parse.get('mttp', 'port'))}

        self.sms_dict = {
            'receivers': self.conf_parse.get('sms', 'receivers').strip().strip('\n').split(';')
        }

    def set_request(self, request):
        """ 设置当前抓取参数
        """
        self.request = request

    def validate_request(self):
        """ 在抓取前检查请求:
            1.package必需, 长度大于0
        """
        utils.log('validate request...')
        if len(self.request.package) == 0:
            raise error.ParamError('empty package')
        self.log.package = self.request.package
        self.log.task_type = self.request.task_type
        self.log.force_update = self.request.force_update
        self.log.task_name = self.request.task_name
        self.log.job_id = self.request.job_id

        self.session.package = self.request.package
        utils.log('[request]: %s' % (self.request))

    def load_data_from_db(self):
        """ 加载app在db里的信息
        """
        utils.log('load data from db...')
        # load package table
        ret = self.session.db_set.load_package_table(self.session.package)
        if ret == 0:
            self.session.exist_in_db = False
            utils.log('find new package: [%s]' % (self.session.package))
        else:
            self.session.packageid = self.session.db_set.package.packageid
            self.session.exist_in_db = True
            self.session.multiapk = self.session.db_set.package.multiapk
            self.session.is_channel = (self.session.db_set.package.is_channel == 1)
            self.session.src_state = self.session.db_set.package.state
            self.session.all_download_pid = self.session.db_set.package.all_download_pid
            self.log.packageid = self.session.packageid
            self.log.multiapk = self.session.multiapk
            self.log.is_channel = self.session.db_set.package.is_channel

            # load doc table
            self.session.db_set.load_doc_table_list(self.session.packageid)
            self.session.db_lang_list = self.session.db_set.doc_list.keys()
            if len(self.session.db_lang_list) == 0:
                self.session.db_set.clear_package(self.session.packageid)
                self.session.exist_in_db = False
                utils.log('failed to get data from doc, delete and add, new package: [%s]' % (
                    self.session.package))
            else:
                doc = random.choice(self.session.db_set.doc_list.values())

                self.session.db_version = metadata.Version(
                    version_code=doc.version_code, version_name=doc.version_name)
                self.session.db_sname_list = map(lambda value: value.sname, \
                        self.session.db_set.doc_list.values())
                self.log.title = doc.sname
                self.log.old_version_code = doc.version_code
                self.log.old_version_name = doc.version_name
                self.log.title = doc.sname

                # load apk_version_info table
                self.session.db_set.load_apk_version_info_list(self.session.packageid)
                self.session.db_multi_version_list =  \
                    map(lambda x: metadata.Version(x.version_code, x.version_name), 
                    self.session.db_set.apk_version_info_list.values())
                utils.log('[data in db]: packageid: %d, src_state:%d, multiapk: %d, ' \
                    'is_channel: %d, version_code: %d, version_name: %s, multi version: %s' % (
                    self.session.packageid, self.session.src_state, self.session.multiapk, 
                    self.session.is_channel, self.session.db_version.code, 
                    self.session.db_version.name, self.session.db_multi_version_list))
        if self.request.task_type == const.TaskType.DEFAULT:
            self.session.task_type =  const.TaskType.state_2_type(self.session.db_set.package.state)
        else:
            self.session.task_type = self.request.task_type
        utils.log('task_type: %d' % (self.session.task_type))

    def pre_process(self):
        """ 预处理
        """
        pass
        
    def check_update(self):
        """ 与db内信息对比确认抓取行为, 比如新增, 更新等
        """
        pass

    def get_multi_lang_detail(self, package):
        """ 获取多种语言的详情
        """
        pass

    def download_apk(self, download_info):
        """ 下载apk文件
            Args:
                download_info: _app_message.DownloadInfo
        """
        pass

    def parse_apk(self, apk_file_path):
        """ 解析apk文件 
            Raises:
                ParseApkError
        """
        apk_unzip_dir = os.path.join(self.tmp_dir, '%d_%d.unzip' % (
            utils.randint(), utils.randint()))
        utils.init_dir_path(apk_unzip_dir)
        cmd = 'unzip -o %s -d %s' % (apk_file_path, apk_unzip_dir)
        status, output = commands.getstatusoutput(cmd)
        #if not status == 0:
        #    raise error.ParseApkError('unzip apk error. file=%s, status=%d' % (apk_file_path, status))
        decompile_xml = os.path.join(apk_unzip_dir, 'decompile.xml')
        cmd = 'java -jar %s %s/AndroidManifest.xml > %s ' % (
            const.APK_DECOMPILE_BIN_PATH, apk_unzip_dir, decompile_xml)
        status, output = commands.getstatusoutput(cmd)
        if not status == 0:
            raise error.ParseApkError('deserialize error. err=%s' % (output))
        manifest_parser = manifest.ManifestParser(xml_file=decompile_xml)
        manifest_parser.do()
        rsa_file = os.path.join(apk_unzip_dir, 'META-INF', 'CERT.RSA')
        if os.path.isfile(rsa_file):
            manifest_parser.set_signmd5(self.get_apk_signmd5(rsa_file))
        lib_dir = os.path.join(apk_unzip_dir, 'lib')
        if os.path.isdir(lib_dir):
            manifest_parser.set_support_cpu(';'.join(os.listdir(lib_dir)))
        return manifest_parser.app_feature

    def get_apk_signmd5(self, rsa_file):
        """ 根据rsa文件获取apk签名
        """
        shell_cmd = 'openssl pkcs7 -in %s -inform DER -print_certs' % (rsa_file)
        status, output = commands.getstatusoutput(shell_cmd)
        if not status == 0:
            raise error.ParseApkError('get apk signmd5 error. err=%s' % (output))
        else:
            sign_base64_string_io = StringIO.StringIO()
            flag = False
            for line in output.splitlines():
                if cmp('-----BEGIN CERTIFICATE-----', line) == 0:
                    flag = True
                    continue
                elif cmp('-----END CERTIFICATE-----', line) == 0:
                    flag = False
                    continue
                if flag:
                    sign_base64_string_io.write(line)
        sign_string_io = StringIO.StringIO()
        sign_base64_string_io.seek(0)
        base64.decode(sign_base64_string_io, sign_string_io)
        return utils.md5sum(sign_string_io.getvalue())
        
    def upload_apk(self, apk_file_path):
        """ 上传apk文件, 返回其在存储平台的相对地址
        """
        upload_req = _storage_message.UploadRequest()
        upload_req.product = self.auth_dict.get('storage_server_name')
        upload_req.token = self.auth_dict.get('storage_server_token')
        upload_req.mode = _storage_message.MTTP
        upload_req.mttpDetail.host = utils.get_local_host_name()
        upload_req.mttpDetail.port = self.mttp_config_dict.get('port')
        upload_req.mttpDetail.receiveTimeout = 600
        upload_req.compressMultiFiles = False
        apk_md5 = utils.get_file_md5(apk_file_path)
        apk_remote_dir = 'store_%d/%s/%s/%s' % (int(apk_md5, 16) % 10,
            apk_md5[0], apk_md5[1], apk_md5[2])
        remote_file = _storage_message.File(directory=apk_remote_dir, name='%s.apk' % (apk_md5))
        src_dir, src_name = os.path.split(apk_file_path)
        src_file = _storage_message.File(directory=src_dir, name=src_name, md5=apk_md5)
        trans_file = upload_req.files.add()
        trans_file.CopyFrom(_storage_message.TransferFile(srcFile=src_file, destFile=remote_file))
        upload_res = self.upload_2_storage(upload_req)
        upload_apk = upload_res.files[0]
        return (os.path.join(upload_apk.directory, upload_apk.name), upload_apk.md5)

    def upload_2_storage(self, upload_req):
        """ 上传到存储平台
            Args:
                upload_req: _upload_message.UplaodRequest
        """
        url = self.server_url_dict.get('storage_upload')
        try:
            res = utils.requests_ex(url, data=upload_req.SerializeToString(), timeout=600)
        except Exception as err:
            raise error.UploadFileError(url=url, msg=err, extra='request exception')
        if not res.status_code == const.HttpStatusCode.OK:
            raise error.UploadFileError(url=url, msg=res.content, 
                extra='status_code=%d' % (res.status_code))
        upload_res = _storage_message.UploadResponse()
        try:
            upload_res.MergeFromString(res.content)
        except Exception as err:
            raise error.UploadFileError(url=url, msg=err, extra='deserialize error')
        return upload_res

    def resize_image(self, resize_req):
        """ 裁剪图片
            Args:
                resize_req: _image_message.ResizeRequest
        """
        image_auth_name = self.auth_dict.get('image_server_name')
        image_auth_token = self.auth_dict.get('image_server_token')
        resize_req.product = image_auth_name
        resize_req.token = image_auth_token
        url = self.server_url_dict.get('image_resize')
        utils.log('url: %s, resize_req: %s' % (url, utils.message_2_dict(resize_req)))
        try:
            res = utils.requests_ex(url=url, data=resize_req.SerializeToString(), timeout=600)
        except Exception as err:
            raise error.ProcessImageError(url=url, msg=err, extra='request exception')
        if not res.status_code == const.HttpStatusCode.OK:
            raise error.ProcessImageError(url=url, msg=res.content, 
                extra='status_code=%d' % (res.status_code))
        resize_res = _image_message.ResizeResponse()
        try:
            resize_res.MergeFromString(res.content)
        except Exception as err:
            raise error.ProcessImageError(url=url, msg=err, extra='deserialize error')
        return resize_res

    def update_db(self):
        """ 更新db
        """
        utils.log('update db...')
        time_stamp = utils.time_stamp()
        
        if self.session.action == const.Action.INSERT:
            self.session.db_set.package.create_time = time_stamp
            self.session.packageid = self.session.db_set.insert_package_table()
            utils.log('insert package. package=[%s], packageid=[%s]' % (self.session.package,
                self.session.packageid))
        else:
            if self.session.is_channel:
                self.session.db_set.update_package_table_by_channel()
            else:
                self.session.db_set.update_package_table()
            utils.log('update package.  package=[%s], packageid=[%s]' % (self.session.package,
                self.session.packageid))
        if const.Action.filter_update_doc(self.session.action):
            common_langs = list(set(self.session.db_lang_list) & \
                set(self.session.lang_details.langs))
            add_langs = list(set(self.session.lang_details.langs) - set(self.session.db_lang_list))
            del_langs = list(set(self.session.db_lang_list) - set(self.session.lang_details.langs))
            for lang in self.session.lang_details.langs:
                lang_detail = self.session.lang_details.get_detail_by_lang(lang)
                if lang in common_langs:
                    doc = self.session.db_set.doc_list.get(lang)
                elif lang in add_langs:
                    doc = metadata.DocTable()
                doc.packageid = self.session.packageid
                doc.lang = lang
                doc.build_time = time_stamp
                doc.version_code = self.session.new_db_version.code
                doc.version_name = self.session.new_db_version.name
                doc.sname = lang_detail.sname
                doc.brief = lang_detail.brief
                doc.whatsnew = lang_detail.whatsnew
                doc.icon = lang_detail.icon
                doc.icon65 = lang_detail.icon65
                doc.iconlow = lang_detail.iconlow
                doc.iconhigh = lang_detail.iconhigh
                doc.iconhdpi = lang_detail.iconhdpi
                doc.icon256 = lang_detail.icon256
                doc.screenshot = lang_detail.screenshot
                doc.screenshotlow = lang_detail.screenshotlow
                doc.screenshothigh = lang_detail.screenshothigh
                doc.banner = lang_detail.banner
                doc.iconalading = lang_detail.iconalading
                doc.sname_lang = self.detect(lang_detail.sname)

                apk_detail = self.session.apks.get_detail_by_version_code(doc.version_code)
                doc.signmd5 = apk_detail.feature.sign_md5
                doc.cpu = apk_detail.feature.support_cpu
                doc.min_sdk = apk_detail.feature.min_sdk
                doc.max_sdk = apk_detail.feature.max_sdk
                doc.apk_md5 = apk_detail.apk_md5
                doc.download_inner = apk_detail.download_inner
                doc.size = apk_detail.apk_size
                doc.permission = apk_detail.permission
                doc.update_time = apk_detail.src_updatetime
                doc.source = self.apk_source

                if lang in add_langs:
                    self.session.db_set.insert_doc_table(doc)
                    utils.log('insert doc. packageid=[%d], lang=[%s]' % (self.session.packageid, 
                        lang))
                elif lang in common_langs:
                    self.session.db_set.update_doc_table(doc)
                    utils.log('update doc. packageid=[%d], lang=[%s]' % (self.session.packageid, 
                        lang))
            for lang in del_langs:
                doc = self.session.db_set.doc_list.get(lang)
                self.session.db_set.delete_doc_table(doc)
                utils.log('delete doc. packageid=[%d], lang=[%s]' % (self.session.packageid, lang))
        if not self.session.multiapk == const.MultiApkType.NO_MULTIAPK and \
            const.Action.filter_update_multi_version(self.session.action):
            apk_version_code_list = self.session.apks.version_code_list
            db_multi_version_code_list = map(lambda x: x.code, self.session.db_multi_version_list)
            common_version_code_list = \
                list(set(db_multi_version_code_list) & set(apk_version_code_list))
            add_version_code_list = \
                list(set(apk_version_code_list) - set(db_multi_version_code_list))
            for version_code in self.session.apks.version_code_list:
                apk_detail = self.session.apks.get_detail_by_version_code(version_code)
                if version_code in common_version_code_list:
                    multi_version_info = self.session.db_set.apk_version_info_list.get(version_code)
                elif version_code in add_version_code_list:
                    multi_version_info = metadata.ApkVersionInfoTable()
                multi_version_info.package = self.session.package
                multi_version_info.packageid = self.session.packageid
                multi_version_info.version_code = apk_detail.version_code
                multi_version_info.version_name = apk_detail.version_name
                multi_version_info.download_inner = apk_detail.download_inner
                multi_version_info.apk_md5 = apk_detail.apk_md5
                multi_version_info.size = apk_detail.apk_size
                multi_version_info.sign_md5 = apk_detail.feature.sign_md5
                multi_version_info.min_sdk = apk_detail.feature.min_sdk
                multi_version_info.max_sdk = apk_detail.feature.max_sdk
                multi_version_info.targe_sdk = apk_detail.feature.target_sdk
                multi_version_info.library = apk_detail.feature.uses_library_str
                multi_version_info.compatible_screens = apk_detail.feature.compatible_screens_str
                multi_version_info.small_screen = apk_detail.feature.small_screens
                multi_version_info.normal_screen = apk_detail.feature.normal_screens
                multi_version_info.large_screen = apk_detail.feature.large_screens
                multi_version_info.xlarge_screen = apk_detail.feature.xlarge_screens
                multi_version_info.gl_version = apk_detail.feature.gl_es_version
                multi_version_info.cpu = apk_detail.feature.support_cpu
                multi_version_info.source = self.apk_source
                multi_version_info.update_time = time_stamp

                if version_code in common_version_code_list:
                    self.session.db_set.update_apk_version_info_table(multi_version_info)
                    utils.log('update apk_version_info. packageid=[%d], version_code=[%d]' % (
                        self.session.packageid, apk_detail.version_code))
                elif version_code in add_version_code_list:
                    multi_version_info.create_time = time_stamp
                    self.session.db_set.insert_apk_version_info_table(multi_version_info)
                    utils.log('insert apk_version_info. packageid=[%d], version_code=[%d]' % (
                        self.session.packageid, apk_detail.version_code))

    def clear_cache(self):
        """ 更新缓存
        """
        utils.log('clear cache...')
        self.clear_app_detail(self.session.package, self.session.packageid)

    def clear_app_detail(self, package, packageid):
        """ 更新app详情缓存
        """
        url = '%s?package=%s&packageid=%d' % (self.server_url_dict.get('mm_app_detail'),
            package, packageid)
        utils.log('url: %s' % (url))
        try:
            res = utils.requests_ex(url, timeout=20)
        except Exception as err:
            utils.log('failed to clear app detail, url=[%s], err=[%s]' % (
                url, err), 'WARNING')

    def anti_scan(self, apk_url, md5):
        """ 安全扫描
        """
        utils.log('anti scan...')
        url = '%s/%s' % (self.server_url_dict.get('mm_apk_download'), apk_url)
        request_param = {'scanlist': [{'md5': md5, 'url': url}],
                         'priority': '0'}
        req_str = utils.json_decode(request_param)
        security_key = self.auth_dict.get('security_key')
        # 计算参数签名
        tmp = 'request=%stpl=%s%s' % (req_str, 'mobomarket', security_key)
        sign = utils.md5sum(tmp)
        scan_url = '%s?tpl=mobomarket&sign=%s' % (self.server_url_dict.get('security_scan'), sign)
        scan_request_param = urllib.urlencode({'request': req_str})
        try:
            res = utils.requests_ex(url=scan_url, data=scan_request_param, timeout=300)
        except Exception as err:
            utils.log('failed to security scan, url=[%s], err=[%s]' % (scan_url, err), 
                level='WARNING')
            return
        if not res.status_code == const.HttpStatusCode.OK:
            utils.log('failed to security scan, url=[%s], err=[%s]' % (scan_url, res.content),
                level='WARNING')

    def notice(self):
        """ 处理完通知一系列监控、或者其他相关系统
            1.通知增量系统
            2.保存apk关键时间点, 用作监控
        """
        # 与apk文件有关, 确定有下载apk行为才通知 
        if self.session.task_type == const.TaskType.DOWNLOAD and \
            const.Action.filter_download_apk(self.session.action):

            # 通知增量系统
            self.notice_increment_system(self.session.packageid)
            #通知91
            self.notice_91(self.session.package)
            # 对于所有下载的apk, 保存关键时间点
            self.save_transition()

    def notice_increment_system(self, packageid):
        """ 更新增量更新系统
        """
        utils.log('notice increment system')
        url = '%s/packageid/%d' % (self.server_url_dict.get('increment_system'), packageid)
        utils.log('url: %s' % (url))
        try:
            res = utils.requests_ex(url, timeout=20)
        except Exception as err:
            utils.log('failed to notice increment system, url=[%s], err=[%s]' % (
                url, err), 'WARNING')

    def notice_91(self, package):
        """ 通知91有更新
        """
        utils.log('notice 91')
        url = self.server_url_dict.get('notice_91')
        utils.log('url: %s' % (url))
        try:
            res = utils.requests_ex(url, data=package, timeout=30)
        except Exception as err:
            utils.log('failed to notice 91. url=[%s], data=[%s], err=[%s]' % (url, package, err), 
                'WARNING')

    def save_transition(self):
        """ 保存app关键时间点
        """
        to_db_time = utils.time_stamp()
        for apk_detail in self.session.apks.details:
            cmd = """
                INSERT INTO apk_crawler_transition(packageid, version_code, action, detect_time, 
                    download_cost_time, to_db_time)
                VALUES(%d, %d, '%s', '%s', %d, '%s')
            """  % (self.session.packageid, apk_detail.version_code, self.session.action.value, 
                self.session.detect_time, apk_detail.download_cost_time, to_db_time)
            self.db.execute(cmd)

    def detect(self, msg):
        """对msg进行语种检测
        """
        lang = "UNKNOWN"
        url = self.server_url_dict.get("detect_lang")
        data = json.dumps({"query": msg})
        try:
            res = utils.requests_ex(url, data = data)
            status_code, content = res.status_code, res.content
            if status_code == const.HttpStatusCode.OK:
                lang = json.loads(content)["lang"]
        except Exception as err:
            utils.log("failed to detect lang: %s, error:%s" % (msg, err))
        return lang

    def print_log(self):
        """ 日志打印
        """
        self.log.print_2_file()

