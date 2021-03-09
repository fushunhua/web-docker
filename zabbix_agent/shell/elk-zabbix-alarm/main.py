from modules.fw_network_connection_info import SotcbbFw
from modules.msg_output import WechatMsg, PushToWechat
from datetime import datetime, timedelta
import sys

# 载入配置文件
config_path = sys.path[0] + '/config.json'

try:
    r = open(config_path)
except Exception as e:
    print('error: ')
    print(e)
    sys.exit(0)
else:
    config_content = r.read()
    r.close()
    config_content = eval(config_content)

    # 定义elasticsearch 基本信息
    es_conf = config_content['es_info']
    es_host = es_conf['es_host']
    es_username = es_conf['es_username']
    es_passwd = es_conf['es_passwd']

    # 定义企业微信基本信息
    msg_dict = dict()

    wechat_info = config_content['wechat_info']
    msg_dict['corpid'] = wechat_info['corpid']
    msg_dict['corpsecret'] = wechat_info['corpsecret']
    msg_dict['app_id'] = wechat_info['app_id']
    msg_dict['group_id'] = wechat_info['group_id']

    query_func = config_content['query_list']


# 从ES中搜索日志并处理后再输出
def es_get_data(es_server, es_user, es_pwd, es_idx, fw, log_limit, es_gte, es_lte, access_limit):
    es_config = SotcbbFw(es_server, es_user, es_pwd, es_idx, fw, log_limit, es_gte, es_lte, access_limit)

    es_run = es_config.fw_network_conn_result()
    wc_output = WechatMsg(es_run).fw_msg_output()

    return wc_output


# 处理列表，整合数据，实现逐行显示
def push_to_wechat(msg_content, es_gte, es_lte, access_limit):
    msg = '防火墙连接数告警，请注意以下来源IP及其所访问的系统！\n' \
          + '统计开始时间: ' + es_gte + '\n' \
          + '统计结束时间: ' + es_lte + '\n' \
          + '当统计时间内的访问总数超过阈值: ' + str(access_limit) + ' 将触发告警\n\n'
    for i in msg_content:
        for j in i:
            msg += j + '\n'
        msg += '\n'

    return msg


'''
处理时间，输入后以下格式的内容：
('2018-07-19 16:15:00', '1531988143483', '2018-07-19 16:13:00', '1531988023483')
'''


def datetime_handler(time_difference):
    datetime_now = datetime.now()
    datetime_before = datetime_now - timedelta(minutes=time_difference)

    datetime_now_formatted = datetime_now.strftime('%Y-%m-%d %H:%M:00')
    datetime_before_formatted = datetime_before.strftime('%Y-%m-%d %H:%M:00')

    datetime_now_timestamp = str(datetime_now.timestamp() * 10000)[0:13]
    datetime_before_timestamp = str(datetime_before.timestamp() * 10000)[0:13]

    return datetime_now_formatted, datetime_now_timestamp, datetime_before_formatted, datetime_before_timestamp


# 处理推送请求

def processing_push(es_index, fw_name, datetime_list, query_limit, request_limit):
    gte = datetime_list[3]
    lte = datetime_list[1]

    es_output = es_get_data(es_host, es_username, es_passwd, es_index, fw_name, query_limit, gte, lte, request_limit)

    if len(es_output) == 0:
        pass
    else:
        msg_dict['msg'] = push_to_wechat(es_output, datetime_list[2], datetime_list[0], request_limit)
        push = PushToWechat('/usr/local/shell/wechat_msg/main.py', msg_dict).push()
        return push


# 定义运行函数
def main_run():
    for i in query_func:
        query_limit = i['query_limit']
        request_limit = i['request_limit']
        datetime_list = datetime_handler(i['time_interval'])
        es_index = i['es_index']
        fw_name = i['fw_name']

        processing_push(es_index, fw_name, datetime_list, query_limit, request_limit)


if __name__ == '__main__':
    main_run()
