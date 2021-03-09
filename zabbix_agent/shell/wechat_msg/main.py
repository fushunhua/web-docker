#!/usr/bin/python3
# -*- coding=utf-8 -*-

import os
import sys
import time

import script.get_access_token as wc_token
import script.send_msg_to_division as send_msg

# 接收传入内容
script_parameter = sys.argv[1]

# 定义为字典
script_parameter = eval(script_parameter)

# 定义变量
corpid = script_parameter['corpid']
corpsecret = script_parameter['corpsecret']
msg = script_parameter['msg']
group_id = script_parameter['group_id']
app_id = script_parameter['app_id']

# 定义临时文件目录
temp_file = sys.path[0] + '/.config.conf'


# 写入临时文件
def write_to_file(timestamp_now, new_token):
    temp_file_content = str(timestamp_now) + "," + new_token
    i = open(temp_file, 'wt')
    i.write(temp_file_content)
    i.close()


# 判断文件是否存在并不为空
def check_file(file_path):
    if os.path.exists(file_path):
        if os.path.getsize(file_path):
            return True
        else:
            return False
    else:
        return False


# 获取当前的时间戳
get_timestamp_now = round(time.time() * 1000)

# 判断token是否有效
if check_file(temp_file):
    config_in_file = open(temp_file, 'r')
    try:
        old_config = config_in_file.readline()
    finally:
        config_in_file.close()
    old_config = old_config.split(',')
    old_config_timestamp = old_config[0]
    if int(get_timestamp_now) - int(old_config_timestamp) > 6600000:
        content = wc_token.wechat_token(corpid, corpsecret)
        token = content.get_token()
        write_to_file(get_timestamp_now, token)
    else:
        token = old_config[1]
else:
    content = wc_token.wechat_token(corpid, corpsecret)
    token = content.get_token()
    write_to_file(get_timestamp_now, token)

# 发送内容
send_msg = send_msg.wechat_send_msg_to_division(token, group_id, app_id, msg)
send_msg.send_msg()
