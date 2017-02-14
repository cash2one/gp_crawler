#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: manifest.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/08/10 23:27:04
"""
import re
from src import metadata

class XmlNode(object):
    """ 按照字符串匹配的方式解析xml
        首先整个xml文件的内容可以看做一个XmlNode, 然后:
        1. 支持从XmlNode的内容按照node_name匹配节点, 返回XmlNode对象
        2. 支持从XmlNode的内容按照key查找value, 返回字符串
    """
    def __init__(self, text):
        """ text: 当前节点的文本内容
        """
        self.text = text

    def __repr__(self):
        return str(self.text)

    def findall(self, node_name):
        """ 按照名称查找所有节点
            Returns:
                [XmlNode]
        """
        text_list = re.findall('\<%s(.*?)\<\/%s>' % (node_name, node_name), self.text)
        if text_list is not None:
            return map(lambda x: XmlNode(text=x), text_list)

    def find(self, node_name):
        """ 按照名称查找单个节点
            Returns:
                XmlNode
        """
        text_list = self.findall(node_name)
        if text_list is None or len(text_list) == 0:
            return
        return text_list[0]

    def get(self, key):
        """ 从XmlNode.text中匹配(key, value)
            默认Manifest.xml节点满足格式key="value"
        """
        text = re.findall('%s=\"(.*?)\"' % (key), self.text)
        if text is None or len(text) == 0:
            return
        return text[0]


class ManifestParser(object):
    """ 解析apk获取想信息
        Attributes:
            xml_file: app AndroidManifest文件
            root: xml解析对象
            app_feture: apk解析结果对象
    """
    URI = 'http://schemas.android.com/apk/res/android'
    SCREEN_SIZE = {'200': 'small',
                   '300': 'normal',
                   '400': 'large',
                   '500': 'xlarge'}
    SCREEN_DENSITY = {'120': 'ldpi',
                      '160': 'mdpi',
                      '240': 'hdpi',
                      '320': 'xhdpi',
                      '480': 'xxhdpi',
                      '640': 'xxxhdpi'}

    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.root = None
        self.app_feature = metadata.ApkFeature()

    def set_signmd5(self, sign_md5):
        """ 设置apk签名
        """
        self.app_feature.sign_md5 = sign_md5

    def set_support_cpu(self, support_cpu):
        """ 设置apk支持的cpu类型
        """
        self.app_feature.support_cpu = support_cpu

    def do(self):
        """ 主入口
        """
        self.read_xml()
        self.load_basic_information()
        self.load_uses_sdk()
        self.load_screen()
        self.load_uses_configuration()
        self.load_uses_feature()
        self.load_uses_library()
        
    def read_xml(self):
        """ 加载manifest文件，并过滤与兼容性无关的信息
            ElementTree加载失败的情况下使用字符串匹配的方式尝试解析manifest.xml
        """
        try:
            ET.register_namespace("android", ManifestParser.URI)
            xml_text = self.get_clean_xml_text(self.xml_file)
            self.root = ET.fromstring(xml_text)
        except Exception as err:
            self.app_feature.parse_manifest_fail = True
            with open(self.xml_file, 'r') as fd:
                text = fd.read().replace('android:', '{%s}' % ManifestParser.URI).replace('\n', '')
                self.root = XmlNode(text=text)

    def load_basic_information(self):
        """ 读取基本信息 
        """
        self.app_feature.pack_name = self.root.get("package")
        self.app_feature.version_code = self.root.get("{%s}versionCode" % ManifestParser.URI)
        self.app_feature.version_name = self.root.get("{%s}versionName" % ManifestParser.URI)
        
    def load_uses_sdk(self):
        """ min_sdk, max_sdk, target_sdk
        """
        us_node = self.root.find("uses-sdk")
        if us_node is None:
            return
        min_sdk = us_node.get("{%s}minSdkVersion" % ManifestParser.URI)
        if min_sdk:
            self.app_feature.min_sdk = int(min_sdk)
        else:
            if self.app_feature.parse_manifest_fail:
                res = re.search('<uses-sdk="([0-9]+)"', 
                    self.root.text.replace('\n', '').replace(' ', '').replace('\t', ''))
                if res is not None:
                    self.app_feature.min_sdk = int(res.group(1))
        max_sdk = us_node.get("{%s}maxSdkVersion" % ManifestParser.URI)
        if max_sdk:
            self.app_feature.max_sdk = int(max_sdk)
        else:
            if self.app_feature.parse_manifest_fail:
                res = re.search('<uses-sdk="([0-9]+)"="([0-9]+)"', 
                    self.root.text.replace('\n', '').replace(' ', '').replace('\t', ''))
                if res is not None:
                    self.app_feature.max_sdk = int(res.group(2))
        target_sdk = us_node.get("{%s}targetSdkVersion" % ManifestParser.URI)
        if target_sdk:
            self.app_feature.target_sdk = int(target_sdk)
        else:
            target_sdk = self.app_feature.min_sdk

    def load_screen(self):
        """ 屏幕属性
        """
        screen_node = self.root.find("supports-screens")
        if screen_node is not None:
            is_support = screen_node.get("{%s}smallScreens" % ManifestParser.URI)
            if is_support == "false":
                self.app_feature.small_screens = 0
            is_support = screen_node.get("{%s}normalScreens" % ManifestParser.URI)
            if is_support == "false":
                self.app_feature.normal_screens = 0
            is_support = screen_node.get("{%s}largeScreens" % ManifestParser.URI)
            if is_support == "false":
                self.app_feature.large_screens = 0
            is_support = screen_node.get("{%s}xlargeScreens" % ManifestParser.URI)
            if is_support == "false":
                self.app_feature.xlarge_screens = 0

        screen_node = self.root.find("compatible-screens")
        if screen_node is not None:
            screens = screen_node.findall("screen")
            for screen in screens:
                sc_size = screen.get("{%s}screenSize" % ManifestParser.URI)
                sc_dpi  = screen.get("{%s}screenDensity" % ManifestParser.URI)
                if sc_size in ManifestParser.SCREEN_SIZE:
                    sc_size = ManifestParser.SCREEN_SIZE[sc_size]
                elif sc_size not in ManifestParser.SCREEN_SIZE.values():
                    continue
                if sc_dpi in ManifestParser.SCREEN_DENSITY:
                    sc_dpi = ManifestParser.SCREEN_DENSITY[sc_dpi]
                elif sc_dpi not in ManifestParser.SCREEN_DENSITY.values():
                    continue
                self.app_feature.compatible_screens.append((sc_size, sc_dpi))
            # 需要对屏幕信息排序
            sorted_screens = sorted(self.app_feature.compatible_screens, key=lambda x:(x[1]+x[0]))
            self.app_feature.compatible_screens = sorted_screens

    def load_uses_configuration(self):
        """ 解析uses-configuration
        """
        uc_node = self.root.find("uses-configuration")
        if uc_node:
            value = uc_node.get("{%s}reqFiveWayNav" % ManifestParser.URI)
            if value == "true":
                self.app_feature.req_five_way_nav = True
            value = uc_node.get("{%s}reqHardKeyboard" % ManifestParser.URI)
            if value == "true":
                self.app_feature.req_five_way_nav = True

    def load_uses_feature(self):
        """ 解析uses-feature
        """
        uf_nodes = self.root.findall("uses-feature")
        for node in uf_nodes:
            gl_es_version = node.get("{%s}glEsVersion" % ManifestParser.URI)
            if gl_es_version:
                required = node.get("{%s}required" % ManifestParser.URI)
                if required != "false":
                    gl_es_version = int(gl_es_version, 16)
                    self.app_feature.gl_es_version = gl_es_version
                continue
            name = node.get("{%s}name" % ManifestParser.URI)
            if not name:
                continue
            value = node.get("{%s}required" % ManifestParser.URI)
            if not value:
                continue
            if value == "true":
                self.app_feature.uses_feature_list.append([name, True])

    def load_uses_library(self):
        """ 解析apk依赖的lib
        """
        lib_node = self.root.findall("application/uses-library")
        for node in lib_node:
            name = node.get("{%s}name" % ManifestParser.URI)
            required = node.get("{%s}required" % ManifestParser.URI)
            if not name:
                continue
            if required == "false":
                continue
            for lib in self.app_feature.uses_library:
                if name == lib[0]:
                    lib[1] = 1

if __name__ == '__main__':
    xml_file = './test/decompile.xml'
    manifest_parser = ManifestParser(xml_file)
    manifest_parser.do()
    print manifest_parser.app_feature.dump()

