import sys
import importlib

major, minor = sys.version_info[:2]
submodule_name = f"{__name__}.traceback-{major}-{minor}"
try:
    # 直接导入并替换sys.modules中的条目
    module = importlib.import_module(submodule_name)
    sys.modules["traceback"] = module
except ImportError as e:
    pass
