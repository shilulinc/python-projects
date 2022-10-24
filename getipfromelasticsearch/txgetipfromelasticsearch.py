import os
import json
import datetime
from elasticsearch import  Elasticsearch

def getipfromelasticsearch():
    es = Elasticsearch(
        ['xxx'],
        http_auth=('xxx', 'xxx'),
        sniff_on_start=False,
        sniff_on_connection_fail=False,
        sniffer_timeout=None
    )

    # 获取当前时间索引
    index_date = (datetime.datetime.now() + datetime.timedelta(hours = -8)).strftime('%Y.%m.%d.%H')
    es_index = 'xxx' + index_date

    # 获取当前时间整分钟时间戳和往前1分钟时间戳
    time_format = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    time_datetime = datetime.datetime.strptime(time_format, '%Y-%m-%d %H:%M')
    start_time = int(time_datetime.timestamp()) - 600
    end_time = int(time_datetime.timestamp())

    # qbody_client_ip
    # qbody_client_ip = {"aggs":{"2":{"terms":{"field":"client_ip","size":100,"order":{"_count":"desc"}}}},\
    #     "size":0,"_source":{"excludes":[]},"stored_fields":["*"],"script_fields":{},\
    #         "docvalue_fields":[{"field":"@timestamp","format":"date_time"}],\
    #             "query":{"bool":{"must":[{"match_all":{}},{"match_all":{}},\
    #                 {"range":{"@timestamp":{"gte":str(start_time) + "000","lte":str(end_time) + "000","format":"epoch_millis"}}}],\
    #                     "filter":[],"should":[],"must_not":[]}}}

    # http_host
    # qbody_http_host = {"aggs":{"3":{"terms":{"field":"http_host","size":100,"order":{"_count":"desc"}}}},\
    #     "size":0,"_source":{"excludes":[]},"stored_fields":["*"],"script_fields":{},\
    #         "docvalue_fields":[{"field":"@timestamp","format":"date_time"}],\
    #             "query":{"bool":{"must":[{"match_all":{}},{"match_all":{}},\
    #                 {"range":{"@timestamp":{"gte":str(start_time) + "000","lte":str(end_time) + "000","format":"epoch_millis"}}}],\
    #                     "filter":[],"should":[],"must_not":[]}}}

    # client_ip_and_http_host
    qbody_client_ip_and_http_host = {"aggs":{"3":{"terms":{"field":"client_ip","size":100,\
        "order":{"_count":"desc"}},"aggs":{"5":{"terms":{"field":"http_host","size":1,\
            "order":{"_count":"desc"}}}}}},"size":0,"_source":{"excludes":[]},\
                "stored_fields":["*"],"script_fields":{},\
                    "docvalue_fields":[{"field":"@timestamp","format":"date_time"}],\
                        "query":{"bool":{"must":[{"match_all":{}},{"match_all":{}},\
                            {"range":{"@timestamp":{"gte":str(start_time) + "000","lte":str(end_time) + "000","format":"epoch_millis"}}}],\
                                "filter":[],"should":[],"must_not":[]}}}

    # qbody_client_ip
    # res_client_ip = es.search(index=es_index, body=json.dumps(qbody_client_ip))
    # http_host
    # res_http_host = es.search(index=es_index, body=json.dumps(qbody_http_host))
    # client_ip_and_http_host
    res_client_ip_and_http_host = es.search(index=es_index, body=json.dumps(qbody_client_ip_and_http_host))

    # 白名单ip
    ipinfo_list = ['xxx']

    # 获取不在白名单里的访问数量排名前10个ip
    # access_ip_list = []
    # for ip_dict in res_client_ip['aggregations']['2']['buckets']:
    #     if ip_dict['key'] not in ipinfo_list:
    #         access_ip_list.append(ip_dict)
    #         if len(access_ip_list) > 9:
    #             break
    # print(access_ip_list)

    # 获取不在白名单里的访问数量排名前10个ip以及每个ip访问最多的域名
    access_ip_list = []
    for client_ip_and_http_host_dict in res_client_ip_and_http_host['aggregations']['3']['buckets']:
        if client_ip_and_http_host_dict['key'] not in ipinfo_list:
            client_ip_dict = {key: value for key, value in client_ip_and_http_host_dict.items() if key in ['key', 'doc_count']}
            http_host_dict = {key: value for key, value in client_ip_and_http_host_dict['5'].items() if key in ['buckets']}
            client_ip_dict.update(http_host_dict)
            client_ip_dict_and_http_host_dict_update = client_ip_dict
            access_ip_list.append(client_ip_dict_and_http_host_dict_update)
            if len(access_ip_list) > 9:
                break

    # print(access_ip_list)
    return access_ip_list
if __name__ == '__main__':
    # getipfromelasticsearch()
    current_date = (datetime.datetime.now().strftime('%Y-%m-%d'))
    basedir = os.path.abspath(os.path.dirname(__file__))
    filename = 'getipfromelasticsearch' + current_date + '.json5'
    filepath = os.path.join(basedir, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
    for every_dict in getipfromelasticsearch():
        with open(filepath, 'a') as f:
            f.write(str(every_dict) + '\n')
