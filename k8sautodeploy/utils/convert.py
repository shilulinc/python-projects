import re


def check_str_len(string):
    # 字符长度不超过253 个
    return string if len(string) <= 253 else False


def check_start_with(string):
    while re.compile(r'^http:\/\/').search(string):
        string = re.sub(r'^http:\/\/', '', string)

    # 名称仅允许小写字母、数字开始
    start_with_regex = re.compile(r'^([0-9]|[a-z])')
    return string if start_with_regex.search(string) is not None else False


def check_end_with(string):
    # 以- 结尾时，省去-
    while re.compile(r'(-)$').search(string):
        string = string[:-1]

    # 仅允许小写字母、数字结尾
    end_with_regex = re.compile(r'([0-9]|[a-z])$')
    return string if end_with_regex.search(string) is not None else False


def check_connection_symbol(string):
    # 两个或两个以上 - 连接时转换为一个 -
    while re.compile(r'--').search(string):
        string = string.replace('--', '-')
    return string


def convert_connection_symbol(string):
    # - [/_] 符号统一转化为 -
    string = re.sub(r'\/|_|\|', '-', string)

    # (.*) 跳过不进行转化
    string = re.sub(r'\(\.\*\)', '', string)

    # 出现( 或者 ) 时 跳过不进行转化
    while re.compile(r'\(.*\)').search(string):
        string = re.sub(r'\(.*\)', '', string)
    return string


def convert(string):
    string = check_start_with(string)
    string = convert_connection_symbol(string)
    string = check_connection_symbol(string)
    string = check_end_with(string)
    string = check_str_len(string)

    return string


# print(convert("http://foo.example.com/api/v3/(.*)/(call|staff)/extractor"))


