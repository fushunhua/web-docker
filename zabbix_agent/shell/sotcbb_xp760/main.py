import subprocess
import xml.etree.ElementTree as ET

import requests

xml_url = 'http://192.168.56.16/monitor.xml'
zabbix_sender_path = '/usr/bin/zabbix_sender'

r = requests.get(xml_url)

xml_content = r.content.decode().strip('\n')

xml_tree = ET.fromstring(xml_content)

content_dict = dict()
content_dict['available_connections'] = xml_tree[1].text
content_dict['queued_mb_requests'] = xml_tree[6].text
content_dict['busy_error'] = xml_tree[7].text

for key, value in content_dict.items():
    zabbix_sender_script = zabbix_sender_path + ' -z 127.0.0.1 -s APC-XP760 -k ' + key + ' -o ' + value
    k = subprocess.Popen(zabbix_sender_script, shell=True, stdout=subprocess.PIPE)
    k.communicate()

