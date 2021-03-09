#!/usr/bin/python3
# -*- coding=utf-8 -*-

import json
import requests


def post_content(division_id, app_id, msg_content):
    post_content = dict()
    post_msg_content = dict()
    post_msg_content['content'] = msg_content
    post_content['toparty'] = division_id
    post_content['msgtype'] = 'text'
    post_content['agentid'] = app_id
    post_content['text'] = post_msg_content
    return post_content


class wechat_send_msg_to_division:
    def __init__(self, access_token, division_id, app_id, msg_content):
        self.access_token = access_token
        self.division_id = division_id
        self.app_id = app_id
        self.msg_content = msg_content

    def send_msg(self):
        msg_content = post_content(self.division_id, self.app_id, self.msg_content)
        msg_content = json.dumps(msg_content, ensure_ascii=False)
        send_msg = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + str(self.access_token)
        r = requests.post(send_msg, msg_content.encode('utf-8'))
        content = r.content.decode()
        print(content)
