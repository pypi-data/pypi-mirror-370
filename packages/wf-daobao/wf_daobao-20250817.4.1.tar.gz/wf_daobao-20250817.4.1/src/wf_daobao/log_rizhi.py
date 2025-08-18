import os.path
import sys
from loguru import logger


def uru_log(log_file_prefix):
    # 创建logger
    logging = logger
    # 清空设置
    logging.remove()
    # 日志文件夹路径不存在则创建
    loguru_dir_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "uru_logs" + os.sep
    if not os.path.exists(loguru_dir_path):
        os.makedirs(loguru_dir_path)
    log_file_path = loguru_dir_path + os.sep + "%s_{time}.log" % log_file_prefix
    # 日志输出到文件
    logging.add(log_file_path,
                format='[{time:YYYY-MM-DD HH:mm:ss,SSS}] '  # 时间
                       '{module}.{function} - {line} - {level} - {message}',  # 模块.方法-行号-级别-内容
                retention='720h',  # 30天清理一次日志
                rotation='00:00'  # 每天0点生成新日志文件
                )
    
    # 日志打印到控制台
    logging.add(sys.stdout,
                format="[<green>{time:YYYY-MM-DD HH:mm:ss,SSS}</green>] "  # 时间
                    "<blue>{module}</blue>.<blue>{function}</blue> - "  # 模块.方法
                    "<cyan>{line}</cyan> - "  # 代码行号
                    "<level>{level}</level> - "  # 日志等级
                    "<level>{message}</level>",  # 日志内容
                )
    return logging