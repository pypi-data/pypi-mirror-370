import yaml
import nacos,os
import logging

from agent.utils.nacos_val import getVal, insert_system_config_from_nacos

global_client_cron = None
logger = logging.getLogger(__name__)

def get_config_from_nacos_every_10_seconds():
    try:
        """
        每10秒从nacos上拉取配置，然后推送到原本的system_config_from_nacos中
        """
        nacos_group, nacos_namespace, nacos_server_address, service_name, nacos_user, nacos_pwd = getVal()
        global global_client_cron
        if (global_client_cron is None):
            log_dir = os.getenv('NACOS_LOG_DIR', '/root/logs/nacos')
            os.makedirs(log_dir, exist_ok=True)
            global_client_cron = nacos.NacosClient(nacos_server_address, namespace=nacos_namespace, username=nacos_user,password=nacos_pwd,logDir=log_dir)
        data_id = service_name + '.yaml'
        system_config = global_client_cron.get_config(data_id, nacos_group, 20, None)
        if (system_config is not None):
            system_config_yaml = yaml.safe_load(system_config)
            insert_system_config_from_nacos(system_config_yaml)
    except Exception as e:
        logger.error(e)


