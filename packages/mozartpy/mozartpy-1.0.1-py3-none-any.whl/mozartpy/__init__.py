# __all__ = ['ModelReader']    # 패키지에서 원하는 함수만 공개할 때 사용
import os
from clr_loader import get_coreclr
from pythonnet import set_runtime
import sys

filedir = os.path.dirname(os.path.abspath(__file__))
dllFolder = os.path.join(filedir, r'netcore')

rt = get_coreclr(runtime_config=os.path.join(dllFolder, "ProcessHost.runtimeconfig.json"))
set_runtime(rt)
sys.path.append(dllFolder)
sys.path.append(os.path.join(dllFolder, 'downloader'))

from .modelreader import Model
from .servicehelper import Downloader

