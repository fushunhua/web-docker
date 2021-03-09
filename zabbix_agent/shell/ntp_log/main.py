#coding=utf-8
import json
import os
import sys
import time
from datetime import date, timedelta
from os import popen
import datetime

import httplib2
from IPy import IP

get_date_today = date.today()
get_date_yesterday = get_date_today - timedelta(days=1)

# start_time = sys.argv[1]
# end_time = sys.argv[2]

start_time = str(get_date_yesterday)
end_time = str(get_date_today)

req_addr = 'http://10.3.201.18:9200/ntp_log_alias/_search?scroll=1m'

req_body = {
    "_source": {
        "includes": ["time_difference", "result", "@timestamp", "client_ip"]
    },
    "size": "1000",
    "sort": {
        "@timestamp": {"order": "desc"}
    },
    "query": {
        "range": {
            "@timestamp": {
                "gte": start_time,
                "lte": end_time,
                "format": "yyyy-MM-dd"

            }
        }
    }
}


# 请求
def http_req(http_req_addr, http_req_pattern, http_req_body):
    http_req_body = json.dumps(http_req_body)
    http_req_h = httplib2.Http()
    http_req_h.add_credentials('elastic', 'Sotcbb@2018@elastic')
    if http_req_body is None:
        http_req_response, http_req_content = http_req_h.request(http_req_addr, http_req_pattern)
    else:
        http_req_response, http_req_content = http_req_h.request(http_req_addr, http_req_pattern, body=http_req_body, headers={'Content-Type':'application/json'})
    http_req_content = http_req_content.decode()
    http_req_content = json.loads(http_req_content)
    http_req_output = [http_req_response, http_req_content]
    return http_req_output


# 检查scroll_id
def check_scroll_id(check_scroll_id_content):
    if "_scroll_id" in check_scroll_id_content.keys():
        c_scroll_id = check_scroll_id_content["_scroll_id"]
        return c_scroll_id
    else:
        return None


# 日期转换为时间戳
def strptime_to_time_stamp(k):
    time_array = time.strptime(k, "%Y-%m-%dT%H:%M:%S.%fZ")
    time_stamp = int(time.mktime(time_array))
    return time_stamp


# 检查client ip是否已存在字典中
def log_result_ip_check(input_client_ip):
    if input_client_ip in log_result_dict.keys():
        return True
    else:
        return False


# 比对时间新旧
def log_result_update(input_client_ip, input_timestamp):
    old_stamp = log_result_dict[input_client_ip][0]
    old_stamp = strptime_to_time_stamp(old_stamp)
    if strptime_to_time_stamp(input_timestamp) > old_stamp:
        return True
    else:
        return False


main_req = http_req(req_addr, "POST", req_body)
main_req_response = main_req[0]
print(main_req)
main_req_content = main_req[1]['hits']['hits']
scroll_id = check_scroll_id(main_req[1])

log_result_dict = dict()


# 构造结果
def result_dict(k):
    for f in k:
        log_id = f['_id']
        f = f['_source']
        log_timestamp = f['@timestamp']
        log_client_ip = f['client_ip']
        log_result = f['result']
        log_time_difference = f['time_difference']
        if log_result_ip_check(log_client_ip):
            if log_result_update(log_client_ip, log_timestamp):
                log_result_dict[log_client_ip] = [log_timestamp, log_id, log_client_ip, log_result,
                                                  log_time_difference]
            else:
                pass
        else:
            log_result_dict[log_client_ip] = [log_timestamp, log_id, log_client_ip, log_result,
                                              log_time_difference]
    return log_result_dict


result_dict(main_req_content)

while scroll_id is not None:
    req_addr = 'http://10.3.201.18:9200/_search/scroll'
    req_body = {
        "scroll": "1m",
        "scroll_id": scroll_id
    }
    i = http_req(req_addr, "POST", req_body)
    j = i[1]['hits']['hits']
    if len(j) == 0:
        req_addr = 'http://10.3.201.18:9200/_search/scroll/_all'
        http_req(req_addr, "DELETE", None)
        break
    else:
        result_dict(j)

client_ip_list = []

# 生成IP列表
for i in log_result_dict.keys():
    client_ip_list.append(i)


# IP排序
def ip_list_sorted(k):
    l = [(IP(ip).int(), ip) for ip in k]
    l.sort()
    return [ip[1] for ip in l]


output_list = []
for i in ip_list_sorted(client_ip_list):
    output_list.append('"' + log_result_dict[i][0] + '","' + log_result_dict[i][
        1] + '","' + log_result_dict[i][2] + '","' + log_result_dict[i][3] + '","' + log_result_dict[i][4] + '",\n')
    # print(output_list)

# 获取日期
get_time_now = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

# 声明路径
local_path = sys.path[0]
daily_dir = local_path + '/log/' + str(datetime.datetime.now().strftime('%Y-%m'))

# 判断目录是否存在
verify_daily_dir = os.path.exists(daily_dir)

# 创建目录
if not verify_daily_dir:
    os.makedirs(daily_dir)

file_full_path = daily_dir + '/ntp_log_' + get_time_now + '.csv'
print(file_full_path)

# 写入文件
w = open(file_full_path, 'a')
w.write(
    'last sync time,' + 'ELK log ID,' + 'client IP,' + 'synchronize results,' + 'time difference,\n')
for i in output_list:
    w.write(i)

w.close()

# 判断竞价日
this_month = datetime.datetime.now().strftime('%Y-%m')
bid_day = this_month + '-25'


def check_weekend(i):
    i = datetime.datetime.strptime(i, '%Y-%m-%d')
    i_weekday = i.isoweekday()
    if i_weekday < 6:
        return i
    else:
        while i_weekday > 5:
            i = i + datetime.timedelta(days=1)
            i_weekday = i.isoweekday()
        return i


bid_day = str(check_weekend(bid_day)).split(' ')[0]

if str(get_date_today) == bid_day:
    mail_to = "'张瑞明<zhangruiming@sotcbb.com>'"
    mail_cc = "'全春祺<quanchunqi@sotcbb.com>'"
    # For DEBUG Start
    # mail_to = "'张瑞明<tc@c4.hk>'"
    # mail_cc = "'全春祺<quanchunqi@sotcbb.com>'"
    # For DEBUG End
    mail_subject = "NTP时间同步记录-" + start_time + "至" + end_time + "-生成日期：" + str(get_date_today)
    mail_content = "'NTP时间同步记录，请注意查收附件。\n计划竞价日当天早上9点整生成前一天报表并发送，其余时间仅存档不发送邮件。' "
    popen(
        'python3 ' + local_path + "/mail.py " + mail_to + ' ' + mail_cc + ' ' + mail_subject + ' ' + mail_content + ' '
        + file_full_path)
