# -*- coding: utf-8 -*-

class ConnectionException(Exception):
    pass


class ConnectionTimeOut(Exception):
    pass


class RequestTimeOut(Exception):
    pass


class RequestException(Exception):
    pass


class ServerException(Exception):
    pass


class GatewayException(Exception):
    pass


class ArgumentsVaildError(Exception):
    pass


class InvalidArgument(Exception):
    pass


class MultiProcessException(Exception):
    pass

class MaxTryExceed(Exception):
    pass


class RunTimeError(Exception):
    pass

ERROR_CHANNEL_BASE = 9100
GATEWAY_ERROR_DICT = {
    ERROR_CHANNEL_BASE + 1: "no timestamp field",
    ERROR_CHANNEL_BASE + 2: "error timestamp format",
    ERROR_CHANNEL_BASE + 3: "error timestamp",
    ERROR_CHANNEL_BASE + 4: "no signature head",
    ERROR_CHANNEL_BASE + 5: "unkown HTTP method",
    ERROR_CHANNEL_BASE + 6: "resty_sm3:new() failed",
    ERROR_CHANNEL_BASE + 7: "sm3:update() failed",
    ERROR_CHANNEL_BASE + 8: "error packet",
    ERROR_CHANNEL_BASE + 9: "no appkey head",
    ERROR_CHANNEL_BASE + 10: "redis not config, please check...",
    ERROR_CHANNEL_BASE + 11: "no getinfo_byself.lua or no get_secret_byself function in getinfo_byself.lua",
    ERROR_CHANNEL_BASE + 12: "no app_secret in redis or hget from redis timeout",
    ERROR_CHANNEL_BASE + 13: "authentication failure,no client_key in clients",
    ERROR_CHANNEL_BASE + 14: "authentication failure,ip not in whitelist",
    ERROR_CHANNEL_BASE + 15: "authentication failure,ip in blacklist",
    ERROR_CHANNEL_BASE + 16: "authentication failure,app_auth_type is nil",
    ERROR_CHANNEL_BASE + 17: "no client_id in body",
    ERROR_CHANNEL_BASE + 18: "no client_id in args",
    ERROR_CHANNEL_BASE + 19: "error client id",
    ERROR_CHANNEL_BASE + 20: "no client_id head",
    ERROR_CHANNEL_BASE + 21: "error packet,no data_value with get request",
    ERROR_CHANNEL_BASE + 22: "must json type",
    ERROR_CHANNEL_BASE + 23: "error packet,not data_value in post_args",
    ERROR_CHANNEL_BASE + 24: "error packet,not data_value in header or args"
}

SERVER_ERROR_DICT = {
    1002005: "该API不存在",
    1002007: "该API名称已存在!",
    1002008: "该API名称[{0}]已归档!",
    1002013: "json转换失败!",
    1002016: "该path已归档!",
    1002018: "微服务API[{0}]不符合发布规则",
    1002024: "该API已归档",
    1002025: "版本[{0}]正在审核，不能归档",
    1004001: "api版本信息已存在，不可删除！",
    1004002: "api版本信息已上线，不可归档！",
    1005001: "获取RestTemplate对象失败！",
    1005002: "请求URL不能为空！",
    1005003: "请求URL[{0}]不是HTTP协议！",
    1005004: "请求信息不能为空！",
    1005005: "请求头部信息不能为空！",
    1005006: "请求参数信息不能为空！",
    1005007: "请求头部信息缺少httpMethod配置！",
    1005009: "请求头部信息缺少contentType配置！",
    1005010: "远程访问地址[{0}],服务返回报文[{1}],发生异常！",
    1005011: "远程访问地址[{0}],HTTP状态[{1}],HTTP状态说明[{2}],发生异常！",
    1005012: "远程访问地址[{0}],发生异常！",
    1005013: "转换json结构失败！",
    1005016: "服务治理URL，获得失败！",
    100000: "发生异常",
    100011: "参数[{0}]不能为空",
    100027: "请求格式错误",
    100034: "参数[{0}]非法",
    100038: "只能删除空分组",
    100039: "上级分组不能是当前分组或当前分组的下级分组",
    100040: "分组[{0}]的上级分组出现循环引用",
    100041: "{0}[{1}]不存在",
    100042: "{0}[{1}]已存在",
    100043: "{0}JSON反序列化异常",
    100044: "{0}JSON序列化异常",
    101001: "未知的渠道过期状态[{0}]",
    101002: "未知的渠道状态[{0}]",
    102001: "审核记录的状态应为{0}目前是{1}",
    102002: "您只能撤回自己的申请",
    103001: "您已评论，每人只能评论一次",
    103002: "只能删除自己的评论",
    104001: "该API已上线，不能发起上线申请",
    104002: "该API已经在审核中，不能重复发起上线申请",
    104003: "当前已存在草稿版本，不能重复创建草稿版本",
    104004: "只能保存草稿版本",
    104005: "不能保存待审核的API",
    104006: "该API的审核状态不为待审核",
    104007: "审核记录的类型不为API上线申请",
    104008: "API[{0}]的[{1}]版本{2}待审核，不能删除",
    104009: "API[{0}]的[{1}]版本已上线，不能删除",
    104010: "API[{0}]的[{1}]版本{2}待审核，不能归档",
    104011: "API[{0}]的[{1}]版本已上线，不能归档",
    105001: "不能删除基分组",
    105002: "API分组[{}]不在系统ID关联的基分组下",
    200001: "未知的{0}",
    200002: "解析{0}失败",
    200003: "数据库连接失败：{0}",
    200004: "获取方言失败：{0}",
    200011: "参数校验失败：{0}",
    200012: "参数{0}校验失败：{1}",
    200013: "参数{0}转换失败：{1}",
    200014: "参数{0}不能为空",
    200015: "请求解析失败：{0}",
    200021: "生成SQL失败：{0}",
    200022: "自动分页失败，{0}",
    200023: "查询失败：{0}",
    200031: "CSV写入失败：{0}",
    200032: "FTP异常：{0}",
    200033: "DBF文件写入失败：{0}",
    200034: "SFTP异常：{0}",
    200041: "非法的URL：{0}",
    200042: "将请求参数序列化为JSON失败",
    200043: "HTTP请求失败：{0}",
    200044: "解析JSON响应失败",
    200050: "推库初始化异常：{0}",
    200051: "推库执行失败：{0}",
    804001: "ES获取日志失败",
    804002: "检查索引[{0}]是否存在发生异常",
    804003: "创建索引[{0}]的索引结构发生异常",
    804004: "删除索引[{0}]发生异常",
    804005: "新增索引[{0}]文档数据[{1}]发生异常",
    804006: "批量新增索引[{0}]文档数据发生异常",
    804007: "更新索引[{0}]文档数据[{1}]发生异常",
    804008: "删除索引[{0}]文档数据[{1}]发生异常",
    804009: "从索引[{0}]将数据迁移至索引[{1}]发生异常"
}

