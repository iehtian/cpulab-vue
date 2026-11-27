import os
import sys

# 获取当前文件所在目录
pwd = os.path.dirname(os.path.abspath(__file__))
# 将 backend 目录添加到 Python 搜索路径
sys.path.append(os.path.join(pwd, "backend"))

bind = "0.0.0.0:5001"
timeout = 120

accesslog = pwd + "/log/access.log"
errorlog = pwd + "/log/error.log"
loglevel = "info"
