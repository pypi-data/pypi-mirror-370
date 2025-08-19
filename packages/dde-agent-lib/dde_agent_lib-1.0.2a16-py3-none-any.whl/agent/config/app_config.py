import os

from agent.init_env_val import environment, log_directory, log_file, log_level, log_format, log_store, \
    dde_instance_name, dde_nacos_group

_app_config = None
_app_environment = None
# 根据环境变量ENVIRONMENT区分加载的yaml配置文件
def get_app_config():
    """
      根据环境变量ENVIRONMENT判断开发、测试、生产环境，并将对应的yaml文件加载为app_config配置
    返回值: yaml配置
    """
    global _app_config
    global _app_environment

    # 如果配置已经加载，且环境未发生变化，直接返回配置，避免每次加载配置
    if _app_config is not None and environment == _app_environment:
        return _app_config
    logging = {
        "log_directory": log_directory,
        "log_file": log_file,
        "log_level": log_level,
        "log_format": log_format,
        "log_oss_env": environment,
        "log_store": log_store
    }
    nacos = {
        "dde_instance_name": dde_instance_name,
        "dde_nacos_group": dde_nacos_group
    }
    _app_config = {
        "logging": logging,
        "nacos":nacos,
    }
    _app_environment = environment
    return _app_config

