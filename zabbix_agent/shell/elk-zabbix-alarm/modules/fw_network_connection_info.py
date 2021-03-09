'''

Elasticsearch

'''

from elasticsearch import Elasticsearch
import re


class SotcbbFw:
    def __init__(self, host_list, es_username, es_passwd, index_name, fw_name, log_size, gte, lte, es_threshold):
        self.host_list = host_list
        self.es_username = es_username
        self.es_passwd = es_passwd
        self.index_name = index_name
        self.fw_name = fw_name
        self.log_size = log_size
        self.gte = gte
        self.lte = lte
        self.es_threshold = es_threshold

    def fw_network_conn_info(self):
        es_client = Elasticsearch(self.host_list, http_auth=(self.es_username, self.es_passwd), scheme='http',
                                  port=9200)
        es_response = es_client.search(
            index=self.index_name,
            body={
                "_source": {
                    "excludes": []
                },
                "aggs": {
                    "2": {
                        "aggs": {
                            "3": {
                                "aggs": {
                                    "5": {
                                        "aggs": {
                                            "4": {
                                                "terms": {
                                                    "field": "fw_name.keyword",
                                                    "include": self.fw_name,
                                                    "order": {
                                                        "_count": "desc"
                                                    },
                                                    "size": self.log_size
                                                }
                                            }
                                        },
                                        "terms": {
                                            "field": "dst_port.keyword",
                                            "order": {
                                                "_count": "desc"
                                            },
                                            "size": self.log_size
                                        }
                                    }
                                },
                                "terms": {
                                    "field": "dst_ip.keyword",
                                    "order": {
                                        "_count": "desc"
                                    },
                                    "size": self.log_size
                                }
                            }
                        },
                        "terms": {
                            "field": "src_ip.keyword",
                            "order": {
                                "_count": "desc"
                            },
                            "size": self.log_size
                        }
                    }
                },
                "docvalue_fields": [
                    "@timestamp",
                    "log_date"
                ],
                "query": {
                    "bool": {
                        "filter": [],
                        "must": [
                            {
                                "match_all": {}
                            },
                            {
                                "range": {
                                    "@timestamp": {
                                        "format": "epoch_millis",
                                        "gte": self.gte,
                                        "lte": self.lte
                                    }
                                }
                            }
                        ],
                        "must_not": [{
                            "match_phrase": {
                                "dst_port.keyword": {
                                    "query": "53"
                                }
                            }
                        }],
                        "should": []
                    }
                },
                "script_fields": {},
                "size": 0,
                "stored_fields": [
                    "*"
                ]
            }
        )

        return es_response

    def fw_network_conn_result(self):
        es_run = SotcbbFw.fw_network_conn_info(self)
        es_buckets = es_run['aggregations']['2']['buckets']

        re_pattern = re.compile(r'10\..*|192\.168\..*')
        result_dict = dict()

        for i in es_buckets:
            src_ip = i['key']
            if re_pattern.match(src_ip):
                pass
            else:
                dst_ip_list = []
                i_buckets = i['3']['buckets']
                i_sum = 0
                for j in i_buckets:
                    dst_ip_dict = dict()
                    dst_ip = j['key']
                    try:
                        i_count = j['5']['buckets'][0]['4']['buckets'][0]['doc_count']
                    except Exception:
                        pass
                    else:
                        dst_ip_dict[dst_ip] = i_count
                        dst_ip_list.append(dst_ip_dict)
                        i_sum += i_count
                    if i_sum >= self.es_threshold:
                        result_dict[src_ip] = dst_ip_list
                    else:
                        pass

        return result_dict
