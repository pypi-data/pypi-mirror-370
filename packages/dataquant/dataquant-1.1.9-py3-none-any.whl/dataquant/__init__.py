# -*- coding: UTF-8 -*-

import warnings
import importlib
import pkgutil
import dataquant

from dataquant.utils.client import init
__version__ = '1.1.9'
__all__ = []


def _init():
    for loader, module_name, is_pkg in pkgutil.walk_packages(__path__, "dataquant."):
        if module_name.startswith("dataquant.apis") and not is_pkg:
            try:
                api_module = importlib.import_module(module_name)
            except ImportError as ex:
                warnings.warn("import module[{}] error, msg={}".format(module_name, ex))

            for api_name in api_module.__all__:
                try:
                    api = getattr(api_module, api_name)
                    globals()[api_name] = api
                except AttributeError as ex:
                    warnings.warn("load api[{}] error, msg={}".format(api_name, ex))
        elif module_name.startswith("dataquant.pof") and not is_pkg:
            namespace = module_name.split('.')[-2]
            namespace_name = namespace
            namespace = type(namespace, (object,), {})
            namespace.__module__ = "dataquant"
            setattr(dataquant, namespace_name, namespace)
            dataquant.__all__.append(namespace_name)

            try:
                api_module = importlib.import_module(module_name)
            except ImportError as ex:
                warnings.warn("import module[{}] error, msg={}".format(module_name, ex))

            _module = getattr(dataquant, namespace_name)
            for api_name in api_module.__all__:
                try:
                    api = getattr(api_module, api_name)
                    setattr(_module, api_name, api)
                except AttributeError as ex:
                    warnings.warn("load api[{}] error, msg={}".format(api_name, ex))
        elif module_name.startswith("dataquant.ic") and not is_pkg:
            namespace = module_name.split('.')[-2]
            namespace_name = namespace
            namespace = type(namespace, (object,), {})
            namespace.__module__ = "dataquant"
            setattr(dataquant, namespace_name, namespace)
            dataquant.__all__.append(namespace_name)

            try:
                api_module = importlib.import_module(module_name)
            except ImportError as ex:
                warnings.warn("import module[{}] error, msg={}".format(module_name, ex))

            _module = getattr(dataquant, namespace_name)
            for api_name in api_module.__all__:
                try:
                    api = getattr(api_module, api_name)
                    setattr(_module, api_name, api)
                except AttributeError as ex:
                    warnings.warn("load api[{}] error, msg={}".format(api_name, ex))
        elif module_name.startswith("dataquant.cd") and not is_pkg:
            namespace = module_name.split('.')[-2]
            namespace_name = namespace
            namespace = type(namespace, (object,), {})
            namespace.__module__ = "dataquant"
            setattr(dataquant, namespace_name, namespace)
            dataquant.__all__.append(namespace_name)

            try:
                api_module = importlib.import_module(module_name)
            except ImportError as ex:
                warnings.warn("import module[{}] error, msg={}".format(module_name, ex))

            _module = getattr(dataquant, namespace_name)
            for api_name in api_module.__all__:
                try:
                    api = getattr(api_module, api_name)
                    setattr(_module, api_name, api)
                except AttributeError as ex:
                    warnings.warn("load api[{}] error, msg={}".format(api_name, ex))
        elif module_name.startswith("dataquant.sql") and not is_pkg:
            namespace = module_name.split('.')[-2]
            namespace_name = namespace
            namespace = type(namespace, (object,), {})
            namespace.__module__ = "dataquant"
            setattr(dataquant, namespace_name, namespace)
            dataquant.__all__.append(namespace_name)

            try:
                api_module = importlib.import_module(module_name)
            except ImportError as ex:
                warnings.warn("import module[{}] error, msg={}".format(module_name, ex))

            _module = getattr(dataquant, namespace_name)
            for api_name in api_module.__all__:
                try:
                    api = getattr(api_module, api_name)
                    setattr(_module, api_name, api)
                except AttributeError as ex:
                    warnings.warn("load api[{}] error, msg={}".format(api_name, ex))
        elif module_name.startswith("dataquant.hk") and not is_pkg:
            namespace = module_name.split('.')[-2]
            namespace_name = namespace
            namespace = type(namespace, (object,), {})
            namespace.__module__ = "dataquant"
            setattr(dataquant, namespace_name, namespace)
            dataquant.__all__.append(namespace_name)

            try:
                api_module = importlib.import_module(module_name)
            except ImportError as ex:
                warnings.warn("import module[{}] error, msg={}".format(module_name, ex))

            _module = getattr(dataquant, namespace_name)
            for api_name in api_module.__all__:
                try:
                    api = getattr(api_module, api_name)
                    setattr(_module, api_name, api)
                except AttributeError as ex:
                    warnings.warn("load api[{}] error, msg={}".format(api_name, ex))
        elif module_name.startswith("dataquant.intl") and not is_pkg:
            namespace = module_name.split('.')[-2]
            namespace_name = namespace
            namespace = type(namespace, (object,), {})
            namespace.__module__ = "dataquant"
            setattr(dataquant, namespace_name, namespace)
            dataquant.__all__.append(namespace_name)

            try:
                api_module = importlib.import_module(module_name)
            except ImportError as ex:
                warnings.warn("import module[{}] error, msg={}".format(module_name, ex))

            _module = getattr(dataquant, namespace_name)
            for api_name in api_module.__all__:
                try:
                    api = getattr(api_module, api_name)
                    setattr(_module, api_name, api)
                except AttributeError as ex:
                    warnings.warn("load api[{}] error, msg={}".format(api_name, ex))

_init()

del _init
