# -*- coding: utf-8 -*-
import time
import inspect
from functools import wraps


def retry(count, exp_name, time_delta=1.0):
    def decorate(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            assert count
            exec_count = 1
            while exec_count < count:
                try:
                    return func(*args, **kwargs)
                except exp_name as ex:
                    exec_count += 1
                    if exec_count == count:
                        raise ex
                    print("Retry because Multi-Process")
                    if time_delta:
                        time.sleep(time_delta)

        return wrap

    return decorate


functions = []


def lru_cache(*args, **kwargs):
    from functools import lru_cache as _lru_cache

    def decorator(func):
        func = _lru_cache(*args, **kwargs)(func)
        functions.append(func)
        return func

    return decorator


def args_check(*checks):
    def decorator(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            call_args = None
            for check in checks:
                if call_args is None:
                    call_args = inspect.getcallargs(get_original_func(func), *args, **kwargs)

                check.check(func.__name__, call_args.get(check.arg_name, check.arg_name), kwargs)

            return func(*args, **kwargs)
        return wrap

    return decorator


def get_original_func(func):
    func_wrapped = getattr(func, "__wrapped__", None)
    while func_wrapped:
        func = func_wrapped
        func_wrapped = getattr(func, "__wrapped__", None)

    return func


class ArgumentChecker(object):

    def __init__(self, args_name):
        self._args_name = args_name
        self._functions = []
        self._required_func = None

    def is_instance(self, _types):
        from dataquant.utils.error import InvalidArgument

        def warp(func, value):
            if not isinstance(value, _types):
                raise InvalidArgument("函数[{}] 参数类型异常，参数[{}]有效类型为[{}]，实参类型为[{}]".format(
                    func, self._args_name, _types, type(value)))

        self._functions.append(warp)
        return self

    def is_required(self):
        from dataquant.utils.error import InvalidArgument

        assert self.arg_name
        if not isinstance(self.arg_name, (tuple, list)):
            raise InvalidArgument("必填项装饰器，参数的有效类型为元组或数组，实参类型为[{}]".format(type(self._args_name)))

        def warp(func, value):
            checkd = False
            for name in self.arg_name:
                if name in value.keys() and value[name]:
                    checkd = True
                    break

            if not checkd:
                raise InvalidArgument("函数[{}] 必填项参数异常，参数[{}]至少填其中一个，实参传入为{}".format(
                    func, self._args_name, list(value.keys())))

        self._required_func = warp
        return self

    def check(self, func, value, kwargs):
        if self._required_func:
            self._required_func(func, kwargs)
            return

        for check_func in self._functions:
            check_func(func, value)

    @property
    def arg_name(self):
        return self._args_name


def check(arg_name):
    return ArgumentChecker(arg_name)



