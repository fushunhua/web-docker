#!/usr/bin/python3
# -*- coding=utf-8 -*-

import re
import subprocess
import sys

# 接收传入内容
msg = sys.argv[1]

# 企业ID
# 测试用
# corpid = 'wx472541934c494fe1'
# 联交所
corpid = 'wx5f6540f3d17f8695'

# 应用的凭证密钥
# 测试用
# corpsecret = 'CUktTkBmMbi6oCemQ6DNOix-ZSJAV6XRz2rY5GdaV_w'
# 联交所
corpsecret = '8c4-ivfgBrUbAEFmW3fjrnR3qghmvIy6XLyAO-BCKOg'

# 企业应用的id
# 测试用
# app_id = 1
# 联交所
app_id = 1000002

# 部门ID
# 测试用
# group_id = 1
# 联交所
group_id = 8889

# 脚本的相对路径
script_path = '/usr/local/shell/wechat_msg/main.py'

# 需要替换的内容
msg_description_mapping_dict = {
    'An abnormality has been detected. Please check the system!': '检测到异常，请检查系统！',
    'Alarm recovery, please continue to pay attention!': '异常已恢复，请持续关注！',
    'trigger': '触发器',
    'alert date:': '告警时间:',
    'alert status': '告警状态',
    'age:': '告警时长:',
    'item value': '触发项目',
    'alert event id': '告警事件ID',
    'recovery date': '恢复时间',
    'recovery status': '检测状态',
    'RESOLVED': '已恢复',
    'severity': '告警等级',
    'recovery event id': '恢复事件ID',
    'Not classified': '未归类',
    'Information': '通知',
    'Warning': '警告',
    'Average': '中等',
    'High': '严重',
    'Disaster': '灾难',
    'PROBLEM': '异常',
    'OK': '正常'
}

# 遍历字典，替换内容
for key, values in msg_description_mapping_dict.items():
    msg = msg.replace(key, values)

# 匹配unicode的正则
re_pattern = re.compile(r'\\u\w*')
# 找到所有unicode字符并编组
unicode_msg = re_pattern.findall(msg)

# 将unicode编码为中文并替换掉msg里的unicode
for i in unicode_msg:
    j = i[0:]
    j = j.encode('latin-1').decode('unicode_escape')
    msg = msg.replace(i, j)

# dict
script_parameter = dict()
script_parameter['corpid'] = corpid
script_parameter['corpsecret'] = corpsecret
script_parameter['msg'] = msg
script_parameter['app_id'] = app_id
script_parameter['group_id'] = group_id

# 定义shell命令
cmd = ['python3', script_path, str(script_parameter)]

# 定义调用shell命令的方法
send_msg = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

# 调用shell命令
send_msg_callback, send_msg_err = send_msg.communicate()

