#!/usr/bin/python3
# -*- coding=utf-8 -*-

import requests


class wechat_division:
    def __init__(self, access_token):
        self.access_token = access_token

    def get_division(self):
        get_wechat_division = 'https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token=' + str(
            self.access_token)
        r = requests.get(get_wechat_division)
        content = r.content.decode()
        content_dirt = eval(content)
        print(content_dirt)
