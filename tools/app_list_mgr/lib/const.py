#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: lib/const.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/07/24 13:09:37
"""
import os

ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

DATA_PATH = os.path.join(ROOT_PATH, 'data')


COUNTRIES = (
    'id',
    'us',
    'th',
    'vn',
    'in',
    'eg',
    'pk',
    'ru',
    'ph',
    'my',
    'sa',
    'br',
    'de',
    'fr',
    'gb',
    'nl',
    'jp',
    'tw',
    'es',
    'ca',
    'mx',
)

GP_LIST_COUNTRIES = (
    'us', 
    'th',
    'vn',
    'jp'
)

CATES = [
    ('app', ''),
    ('app', 'books-and-reference'),
    ('app', 'business'),
    ('app', 'comics'),
    ('app', 'communication'),
    ('app', 'education'),
    ('app', 'entertainment'),
    ('app', 'finance'),
    ('app', 'health-and-fitness'),
    ('app', 'libraries-and-demo'),
    ('app', 'lifestyle'),
    ('app', 'app-wallpaper'),
    ('app', 'media-and-video'),
    ('app', 'medical'),
    ('app', 'music-and-audio'),
    ('app', 'news-magazines'),
    ('app', 'personalization'),
    ('app', 'photography'),
    ('app', 'productivity'),
    ('app', 'shopping'),
    ('app', 'social'),
    ('app', 'sports'),
    ('app', 'tools'),
    ('app', 'transportation'),
    ('app', 'travel-and-local'),
    ('app', 'weather'),
    ('app', 'app-widgets'),
    ('game', ''),
    ('game', 'game-action'),
    ('game', 'game-adventure'),
    ('game', 'game-arcade'),
    ('game', 'game-board'),
    ('game', 'game-card'),
    ('game', 'game-casino'),
    ('game', 'game-casual'),
    ('game', 'game-educational'),
    ('game', 'game-music'),
    ('game', 'game-puzzle'),
    ('game', 'game-racing'),
    ('game', 'game-role-playing'),
    ('game', 'game-simulation'),
    ('game', 'sports-games'),
    ('game', 'game-strategy'),
    ('game', 'game-trivia'),
    ('game', 'game-word'),
]

FEEDS = (
    (1, 'free'),
    (2, 'paid'),
    (3, 'grossing'),
    (4, 'new_free'),
    (5, 'new_paid')
)

GP_FEEDS = (
    ('apps_topselling_paid', 'top'), 
    ('apps_topselling_free', 'free'),
    ('apps_topgrossing', 'grossing'),
    ('apps_topselling_new_paid', 'new_top'),
    ('apps_topselling_new_free', 'new_free'),
    ('apps_movers_shakers', 'shakers')
)

PROXIES = [
    {'https': 'https://mobomarket:test123321@10.252.30.222:8008'},
  #  {'https': 'https://115.146.127.151:1234'},
  #  {'https': 'https://10.244.1.109:3128'},

  #  {'https': 'https://192.169.249.166:17991'},
  #  {'https': 'https://192.169.245.153:17991'},
  #  {'https': 'https://54.175.39.4:3128'}
]

USER_AGENTS = [
 #   'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)'
]





