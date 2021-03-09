import json
import subprocess


class WechatMsg:
    def __init__(self, org_msg):
        self.org_msg = org_msg

    def fw_msg_output(self):
        if type(self.org_msg) is dict:
            org_msg = self.org_msg
        else:
            try:
                org_msg = json.load(self.org_msg)
            except Exception as e:
                return e
            else:
                pass
        output_list = list()

        for k, v in org_msg.items():
            msg_content = list()
            msg_content.append('来源IP: ' + k)
            for i in v:
                for k2, v2 in i.items():
                    msg_content.append('受访IP:' + k2 + ' 访问次数: ' + str(v2))
            output_list.append(msg_content)

        return output_list


class PushToWechat:
    def __init__(self, script_path, msg_dict):
        self.msg_dict = msg_dict
        self.script_path = script_path

    def push(self):
        # 定义shell命令
        cmd = ['python3', self.script_path, str(self.msg_dict)]
        # 定义调用shell命令的方法
        send_msg = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        # 调用shell命令
        send_msg_callback, send_msg_err = send_msg.communicate()
        return send_msg_callback, send_msg_err
