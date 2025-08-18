# -*- coding: utf-8 -*-

import time
import random
import warnings

_CLIENT = None


def get_client():
    global _CLIENT
    if _CLIENT is None:
        init()

    return _CLIENT


def init(**kwargs):
    """
    :param str username: 用户名，license模式下为'license'
    :param str password: 用户密码，license模式下为下发的license
    :param str protocol：传输协议，默认HTTP
    :param str url: 数据服务的URL
    :param int connect_timeout: 连接建立超时时间,默认5秒
    :param int request_timeout: 数据传输超时时间，默认300秒
    :param str compressor: 数据传输过程中的压缩算法，默认不使用
    :param int pool_size: 连接池大小，默认10
    :param int page_size: 数据请求分页大小，默认100000
    :return:
    """

    from dataquant.utils.config import read_config, write_config

    # 获取系统配置
    kwargs_num = len(kwargs)
    retry_times = 0
    load_succ = False
    while not load_succ and retry_times <= 3:
        try:
            conf = read_config()['system']
            load_succ = True
        except Exception as ex:
            time.sleep(random.random()*0.5+0.2)
            retry_times = retry_times + 1
    if not load_succ and retry_times > 3:
        # 读取配置失败，使用默认配置启动
        warnings.warn("读取配置失败，请检查dataquant.utils.config.yml")

    user = kwargs.pop("username", None)
    if user is None:
        user = conf.get("username")
    else:
        conf["username"] = user
    assert user

    pwd = kwargs.pop("password", None)
    if pwd is None:
        pwd = conf.get("password")
    else:
        conf["password"] = pwd
    assert pwd

    url = kwargs.pop("url", None)
    if url is None:
        url = conf.get("url")
    else:
        conf["url"] = url
    assert url

    protocol = kwargs.pop("protocol", None)
    if protocol is None:
        protocol = conf.get("protocol", "HTTP")
    else:
        if protocol != "HTTP":
            warnings.warn("protocol 当前只支持HTTP，设置的{}将不会生效".format(protocol))
        else:
            conf["protocol"] = "HTTP"

    con_timeout = kwargs.pop("connect_timeout", None)
    if con_timeout is None:
        con_timeout = conf.get("connect_timeout", 5)
    else:
        if int(con_timeout) <= 0 or int(con_timeout) > 1000:
            warnings.warn("connect_timeout 有效范围为(0, 1000]，设置的{}将不会生效".format(con_timeout))
        else:
            conf["connect_timeout"] = con_timeout

    timeout = kwargs.pop("request_timeout", None)
    if timeout is None:
        timeout = conf.get("request_timeout", 300)
    else:
        if int(timeout) <= 0 or int(timeout) > 100000:
            warnings.warn("request_timeout 有效范围为(0, 100000]，设置的{}将不会生效".format(timeout))
        else:
            conf["request_timeout"] = timeout

    pool_size = kwargs.pop("pool_size", None)
    if pool_size is None:
        pool_size = conf.get("pool_size", 10)
    else:
        if int(pool_size) <= 0 or int(pool_size) > 100:
            warnings.warn("pool_size 有效范围为(0, 100]，设置的{}将不会生效".format(pool_size))
        else:
            conf["pool_size"] = pool_size

    compressor = kwargs.pop("compressor", None)
    if compressor is None:
        compressor = conf.get("compressor", None)
    else:
        conf["compressor"] = compressor

    page_size = kwargs.pop("page_size", None)
    if page_size is None:
        page_size = conf.get("page_size", 100000)
    else:
        if int(page_size) <= 0 or int(page_size) > 100000:
            warnings.warn("page_size 有效范围为(0, 100000]，设置的{}将不会生效".format(page_size))
        else:
            conf["page_size"] = page_size

    quote_parallel = kwargs.pop("quote_parallel", None)
    if quote_parallel is None:
        quote_parallel = conf.get("quote_parallel", 50)
    conf["quote_parallel"] = quote_parallel

    quote_format = kwargs.pop("quote_format", None)
    if quote_format is None:
        quote_format = conf.get("quote_format", "arrow")
    if quote_format.lower() in ('a', 'arrow'):
        quote_format = "Arrow"
    elif quote_format.lower() in ('p', 'parquet'):
        quote_format = "Parquet"
    else:
        raise ValueError("Unknown quote_format, available values are:a for Arrow,p for Parquet")

    conf["quote_format"] = quote_format

    parallel_mode = kwargs.pop("parallel_mode", None)
    if parallel_mode is None:
        parallel_mode = conf.get("parallel_mode", "t")
    if parallel_mode.lower() in ('t', 'thread'):
        parallel_mode = "Thread"
    elif parallel_mode.lower() in ('c', 'coroutine'):
        parallel_mode = "Coroutine"
    else:
        raise ValueError("Unknown quote_format, available values are:t for Thread,c for Coroutine")

    conf["parallel_mode"] = parallel_mode

    config = {
        "protocol": protocol,
        "auth": {
            "username": user,
            "password": pwd,
        },
        "request_timeout": timeout,
        "connect_timeout": con_timeout,
        "url": url,
        "pool_size": pool_size,
        "compressor": compressor,
        "page_size": page_size,
        "quote_format": quote_format,
    }

    if protocol == "HTTP":
        from dataquant.utils.connection_pool import ConnectionPool
        global _CLIENT
        _CLIENT = _CLIENT = ConnectionPool(config)
    else:
        raise RuntimeError("传输协议无效，got protocol[{}]".format(protocol))

    # 保存配置文件
    if kwargs_num > 0:
        write_config({'system': conf})
    #
    from dataquant.apis.base.api import load_conf as load_base_conf
    from dataquant.apis.quote.api import load_conf as load_quote_conf
    load_base_conf()
    load_quote_conf()
    return


def environ():
    """
    获取环境配置信息
    :return:
    """
    global _CLIENT
    if _CLIENT:
        return _CLIENT.config

    return {}
