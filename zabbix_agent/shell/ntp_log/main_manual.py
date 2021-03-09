import datetime
import json
import os
import re
import sys
from datetime import date, timedelta

import httplib2

get_date_today = date.today()
get_date_yesterday = get_date_today - timedelta(days=1)

# start_time = sys.argv[1]
# end_time = sys.argv[2]

start_time = str(get_date_yesterday)
end_time = str(get_date_today)

req_addr = 'http://10.3.201.18:9200/array_alias/_search?scroll=1m'

req_body = {
    "_source": {
        "includes": [
            "@timestamp",
            "time_difference",
            "result",
            "rui",
            "back_end_host",
            "http_response",
            "remote_ip",
            "geoip.city_name",
            "error_msg",
            "error_log",
            "error_data"
        ]
    },
    "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "http_response": "200"
                    }
                }
            ],
            "filter": {
                "range": {
                    "@timestamp": {
                        "format": "yyyy-MM-dd HH:mm:ss",
                        "gte": "2018-03-27 00:00:00",
                        "lte": "2018-03-28 00:00:00"
                    }
                }
            }
        }
    },
    "size": "100",
    "sort": {
        "@timestamp": {
            "order": "desc"
        }
    }
}


# 请求
def http_req(http_req_addr, http_req_pattern, http_req_body):
    http_req_body = json.dumps(http_req_body)
    http_req_h = httplib2.Http()
    if http_req_body is None:
        http_req_response, http_req_content = http_req_h.request(http_req_addr, http_req_pattern)
    else:
        http_req_response, http_req_content = http_req_h.request(http_req_addr, http_req_pattern, body=http_req_body)
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


main_req = http_req(req_addr, "POST", req_body)
main_req_response = main_req[0]
main_req_content = main_req[1]['hits']['hits']
scroll_id = check_scroll_id(main_req[1])


# 构造结果
def result_output(k):
    log_result_list = []
    for f in k:
        log_id = f['_id']
        f = f['_source']
        log_timestamp = f['@timestamp']
        log_client_ip = f['remote_ip']

        if 'geoip' in f.keys():
            city_name = f['geoip']['city_name']
        else:
            city_name = '-'

        if 'back_end_host' in f.keys():
            back_end_host = f['back_end_host']
            re_pattern = re.compile(r"10\.3\.101")
            re_match = re_pattern.match(back_end_host)
            if re_match:
                continue
        else:
            back_end_host = '-'

        if 'rui' in f.keys():
            uri = f['rui']
        else:
            uri = '-'

        error_msg = '-'
        error_log = '-'
        error_data = '-'

        if 'http_response' in f.keys():
            http_response = f['http_response']
        else:
            http_response = '-'
            error_msg = 'Invalid Request'
            error_log = f['error_log']
            error_data = f['error_data']

        re_pattern = re.compile('(\.png|\.ico|\.js|\.css|getcurrenttimelong)')
        re_findall = re_pattern.findall(uri)
        if len(re_findall) == 0:
            print(log_timestamp, http_response, uri)
            log_result_list.append(
                '"' + log_timestamp + '","' + log_id + '","' + log_client_ip + '","' + city_name + '","' +
                back_end_host + '","' + http_response + '","' + uri + '","' + error_msg + '","' + error_log +
                '","' + error_data + '",\n')
        else:
            continue

    return log_result_list


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


def write_to_file(content, count):
    file_full_path = daily_dir + '/ntp_log_' + get_time_now + '.csv'
    w = open(file_full_path, 'a')
    if count == 0:
        w.write(
            'log timestamp,' + 'ELK log ID,' + 'client IP,' + 'city name,' + 'back_end_host,' + 'http response,' + 'URL,' +
            'error_msg,' + 'error_log,' + 'error_data' + '\n')
        for i in content:
            w.write(i)
    else:
        for i in content:
            w.write(i)
    w.close()


count = 0
result_output(main_req_content)
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
        result_content = result_output(j)
        write_to_file(result_content, count)
        count += 1
