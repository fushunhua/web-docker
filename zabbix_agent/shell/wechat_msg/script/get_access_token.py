#!/usr/bin/python3
# -*- coding=utf-8 -*-

import requests


class wechat_token:
    def __init__(self, corpid, corpsecret):
        self.corpid = corpid
        self.corpsecret = corpsecret

    def get_token(self):
        get_access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + self.corpid + '&corpsecret=' + self.corpsecret
        r = requests.get(get_access_token_url)
        content = r.content.decode()
        content_dirt = eval(content)
        errcode = content_dirt['errcode']
        errmsg = content_dirt['errmsg']
        access_token = content_dirt['access_token']
        if errcode == 200:
            return errmsg
        else:
            return access_token
