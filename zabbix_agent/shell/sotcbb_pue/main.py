import os
import sys

get_main_power_active_power_script = '/usr/local/python3/bin/python3 /usr/local/shell/sotcbb_ats/main.py 2 1143 1'
get_main_power_active_power_value = os.popen(get_main_power_active_power_script).readlines()[0].strip('\\n')

get_ups_output_active_power_script = 'snmpwalk -v2c -c SZJJpublic 192.168.56.10 SNMPv2-SMI::enterprises.5528.100.4.1.10.1.7.1858510833'
get_ups_output_active_power_value = os.popen(get_ups_output_active_power_script).readlines()[0].split('"')
get_ups_output_active_power_value = get_ups_output_active_power_value[-2]
get_ups_output_active_power_value = float(get_ups_output_active_power_value) / 1000

pue = float(get_main_power_active_power_value) / float(get_ups_output_active_power_value)
pue = round(pue, 2)

if pue <= 1.2:
    msg = 'PUE-非常高效'
elif 1.5 >= pue > 1.2:
    msg = 'PUE-高效'
elif 2.0 >= pue > 1.5:
    msg = 'PUE-效率平均'
elif 3 >= pue > 2.0:
    msg = 'PUE-低效'
elif pue > 3.0:
    msg = 'PUE-非常低效'

i = sys.argv[1]


def zabbix_output(j):
    if int(j) == 1:
        return pue
    elif int(j) == 2:
        return msg


print(zabbix_output(i))

