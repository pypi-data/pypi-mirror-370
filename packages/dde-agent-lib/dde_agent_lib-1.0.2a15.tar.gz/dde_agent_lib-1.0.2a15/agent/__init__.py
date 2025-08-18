import os
from threading import Timer
from agent.utils.nacos_util import get_config_from_nacos_every_10_seconds
from agent.utils.nacos_val import get_system_config_from_nacos


def timedTask():
    """
    第一个参数: 延迟多长时间执行任务(单位: 秒)
    第二个参数: 要执行的任务, 即函数
    第三个参数: 调用函数的参数(tuple)
    """
    Timer(10, repeat, ()).start()


def repeat():
    get_config_from_nacos_every_10_seconds()
    timedTask()


print("lib start")
get_system_config_from_nacos()
# timedTask()
# async_sync()
