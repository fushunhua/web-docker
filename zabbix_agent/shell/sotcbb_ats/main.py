import os
import subprocess
import sys

modbus_slave_id = sys.argv[1]
modbus_value_id = sys.argv[2]
modbus_value_format = int(sys.argv[3])
# modbus_value_range_id = int(sys.argv[4])

modbus_script = "/usr/local/bin/mbpoll -a " + modbus_slave_id + " -r " + modbus_value_id + " -1 192.168.56.16 2>/dev/null | grep '^\['"

tmp_file_path = sys.path[0] + '/.atx_zabbix.tmp'

# 判断临时文件是否存在
if os.path.exists(tmp_file_path):
    tmp_file_content = subprocess.Popen('/usr/bin/tail -n 1 ' + tmp_file_path, shell=True, stdout=subprocess.PIPE)
    tmp_file_content = tmp_file_content.stdout.readlines()
    tmp_file_content = tmp_file_content[0].decode().strip('\n')
    # tmp_file = open(tmp_file_path, 'r')
    # tmp_file_content = tmp_file.read()
    # tmp_file.close()
    tmp_file_content = eval(tmp_file_content)  # 字典化临时文件内容
else:
    tmp_file_content = None  # 若字典不存在则返回None


def check_tmp_value_exist(slave_id, item_id):
    if slave_id in tmp_file_content.keys():
        tmp_file_content_v1 = tmp_file_content[slave_id]
        if item_id in tmp_file_content_v1.keys():
            return True, tmp_file_content_v1[item_id]
        else:
            return False, False
    else:
        return None, 0


def get_modbus_value():
    while True:
        k = subprocess.Popen(modbus_script, shell=True, stdout=subprocess.PIPE)
        k = k.stdout.readlines()
        if len(k) == 1:
            k = k[0].decode().strip('\n').split()
            break
    return k


'''
def check_value(n, m):
    # 电压
    if m == 1:
        if 100 < n < 500:
            return True
        else:
            return False
    # 电流、无功功率等
    elif m == 2:
        if -50 < n < 300:
            return True
        else:
            return False
    # 功率因数等
    elif m == 3:
        if 700 < n <= 1100:
            return True
        else:
            return False
    # 频率
    elif m == 4:
        if 4500 < n < 5500:
            return True
        else:
            return False
    elif m == 5:
        if 0 < n < 300:
            return True
        else:
            return False
    elif m == 6:
        if 0 == n or n < 15000:
            return True
        else:
            return False
    elif m == 0:
        return True
        '''


def get_item_value():
    # loop_start = 0
    modbus_value = None
    if modbus_value_format == 1:
        modbus_value = get_modbus_value()[1]
        '''
        while not check_value(int(modbus_value), modbus_value_range_id):
            modbus_value = get_modbus_value()[1]
            loop_start += 1
            if loop_start == 4:
                break
                '''
    elif modbus_value_format == 2:
        modbus_value = get_modbus_value()[2].strip('(').strip(')')
        '''
        while not check_value(int(modbus_value), modbus_value_range_id):
            modbus_value = get_modbus_value()[2].strip('(').strip(')')
            loop_start += 1
            if loop_start == 4:
                break
                '''
    elif modbus_value_format == 3:
        modbus_value = get_modbus_value()[1]
        modbus_value = int(modbus_value) + 32768
        '''
        while not check_value(int(modbus_value), modbus_value_range_id):
            modbus_value = get_modbus_value()[1]
            modbus_value = int(modbus_value) + 32768
            loop_start += 1
            if loop_start == 4:
                break
                '''
    return modbus_value


def write_tmp_content(i_content):
    w_tmp_file = open(tmp_file_path, 'a+')
    w_tmp_file.write(str(i_content) + '\n')
    w_tmp_file.close()


tmp_file_content_dict = dict()
modbus_value_dict = dict()

if tmp_file_content is not None:
    old_value = check_tmp_value_exist(modbus_slave_id, modbus_value_id)
    output_modbus_value = get_item_value()
    loop_start = 0
    if old_value[0]:
        if old_value[1] is not False:
            old_value = int(old_value[1])
            while not old_value * 0.8 < int(output_modbus_value) < old_value * 1.2:
                output_modbus_value = get_item_value()
                loop_start += 1
                if loop_start > 3:
                    break
            modbus_value_dict = tmp_file_content[modbus_slave_id]
            modbus_value_dict[modbus_value_id] = output_modbus_value
            tmp_file_content[modbus_slave_id] = modbus_value_dict
            write_tmp_content(str(tmp_file_content))
    elif old_value[0] is False:
        modbus_value_dict = tmp_file_content[modbus_slave_id]
        modbus_value_dict[modbus_value_id] = output_modbus_value
        tmp_file_content[modbus_slave_id] = modbus_value_dict
        write_tmp_content(str(tmp_file_content))
    elif old_value[0] is None:
        modbus_value_dict[modbus_value_id] = output_modbus_value
        tmp_file_content[modbus_slave_id] = modbus_value_dict
        write_tmp_content(str(tmp_file_content))
else:
    output_modbus_value = get_item_value()
    modbus_value_dict[modbus_value_id] = output_modbus_value
    tmp_file_content_dict[modbus_slave_id] = modbus_value_dict
    write_tmp_content(str(tmp_file_content_dict))

print(output_modbus_value)
