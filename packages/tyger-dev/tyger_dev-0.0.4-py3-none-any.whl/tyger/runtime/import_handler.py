import sys


def init_module(module_name: str, module_src: str):
    module_obj = sys.modules[module_name]
    exec(module_src, module_obj.__dict__)
