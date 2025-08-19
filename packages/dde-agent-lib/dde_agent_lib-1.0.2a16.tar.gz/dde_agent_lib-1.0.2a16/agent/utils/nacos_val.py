import os
from typing import Any

import yaml
import nacos

from agent.config.app_config import get_app_config
from agent.init_env_val import dde_nacos_group, dde_nacos_namespace_lib, dde_nacos_addr_lib, dde_nacos_user_lib, dde_nacos_pwd_lib, dde_instance_name

system_config_from_nacos = None
global_client_storage = None

def getVal():
    app_configs = get_app_config()
    # 先从环境变量中获取nacos信息，如果为None，则从配置文件yaml中获取nacos信息
    nacos_group = dde_nacos_group
    nacos_namespace = dde_nacos_namespace_lib
    nacos_user = dde_nacos_user_lib
    nacos_pwd = dde_nacos_pwd_lib
    if nacos_namespace is None:
        raise RuntimeError("环境变量中读不到dde_nacos_namespace_lib")
    nacos_server_address = dde_nacos_addr_lib
    if nacos_server_address is None:
        raise RuntimeError("环境变量中读不到dde_nacos_addr_lib")
    service_name = dde_instance_name
    return nacos_group, nacos_namespace, nacos_server_address, service_name, nacos_user, nacos_pwd


def get_system_config_from_nacos():
    """从全局安全变量config_from_nacos中，线程安全读取nacos系统配置"""
    global system_config_from_nacos
    if (system_config_from_nacos is None):
        system_config_from_nacos = get_the_new_nacos_config()
    return system_config_from_nacos


def get_the_new_nacos_config():
    """
    将启动的实例注册到nacos上，以供portal后端通过nacos调用
    """
    nacos_group, nacos_namespace, nacos_server_address, service_name, nacos_user, nacos_pwd = getVal()
    global global_client_storage
    if (global_client_storage is None):
        log_dir = os.getenv('NACOS_LOG_DIR', '/root/logs/nacos')
        os.makedirs(log_dir, exist_ok=True)
        global_client_storage = nacos.NacosClient(nacos_server_address, namespace=nacos_namespace, username=nacos_user, password=nacos_pwd,logDir=log_dir)
    # 定义服务实例参数
    data_id = service_name + '.yaml'
    system_config = global_client_storage.get_config(data_id, nacos_group, 20, None)
    system_config_yaml = yaml.safe_load(system_config)
    return system_config_yaml


def insert_system_config_from_nacos(config: Any):
    """系统配置信息放在nacos上，如果nacos配置修改，观察者的回调函数会将新的nacos配置放入全局安全变量中"""
    global system_config_from_nacos
    # with lock:
    system_config_from_nacos = config