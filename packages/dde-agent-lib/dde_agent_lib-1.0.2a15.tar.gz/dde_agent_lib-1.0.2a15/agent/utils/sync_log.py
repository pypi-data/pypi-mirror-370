import os
import random
import threading
import time
import uuid
from datetime import datetime, timedelta

import oss2
from agent.config.app_config import get_app_config

from agent.utils.nacos_val import get_system_config_from_nacos
from agent.utils.dde_logger import dde_logger as logger
from agent.init_env_val import oss_path_pre

def sync_files_oss():
    pid = str(uuid.uuid4())[:16]
    # 配置OSS连接
    system_config = get_system_config_from_nacos()
    endpoint = system_config['oss']['endpoint']
    access_key_id = system_config['oss']['access_key_id']
    access_key_secret = system_config['oss']['access_key_secret']
    bucket_name = system_config['oss']['bucket_name']
    logger.warning(f'日志同步获取到的endpoint为[{endpoint}],access_key_id为[{access_key_id}],bucket_name为[{bucket_name}]')
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    app_config = get_app_config()
    log_oss_env = app_config['logging']['log_oss_env']
    # 定义日志目录和状态文件路径
    log_directory = app_config['logging']['log_directory']
    status_file_path = log_directory + '/last_backup_time.txt'
    if not os.path.exists(status_file_path):
        with open(status_file_path, 'w') as f:
            f.write('')
        logger.warning(f'创建日志同步文件{status_file_path}')
    pid_file_path = log_directory + '/pid.txt'
    if not os.path.exists(pid_file_path):
        with open(pid_file_path, 'w') as f:
            f.write(pid)
        logger.warning(f'创建日志同步文件{pid_file_path}')
    oss_path = oss_path_pre + '/' + log_oss_env + '/'

    while True:
        logger.warning(f'开始备份日志文件，当前时间为{datetime.now()}')

        # 读取上次备份时间
        try:
            with open(status_file_path, 'r') as file:
                last_backup_time = datetime.fromisoformat(file.read().strip())
        except FileNotFoundError:
            logger.error('日志同步状态文件读取失败，从1天前的日志开始备份', exc_info=True)
            last_backup_time = datetime.now() - timedelta(days=1)  # 默认为昨天
        except:
            logger.error('日志同步状态文件内容为空或其他原因，从1天前的日志开始备份', exc_info=True)
            last_backup_time = datetime.now() - timedelta(days=1)  # 默认为昨天

        # 获取需要备份的日志文件列表
        log_files = [f for f in os.listdir(log_directory)
                     if os.path.getmtime(
                log_directory + '/' + f) > last_backup_time.timestamp() and 'last_backup_time.txt' not in f and 'pid.txt' not in f]

        # 备份每个符合条件的日志文件到OSS
        for log_file in log_files:
            try:
                local_path = os.path.join(log_directory, log_file)
                # modification_time = os.path.getmtime(local_path)
                with open(pid_file_path, 'r') as file:
                    f_pid = file.read().strip()
                remote_file_name = f_pid + ':' + log_file
                remote_path = oss_path + log_file[:10] + '/' + remote_file_name  # OSS上的路径
                with open(local_path, 'rb') as f:
                    bucket.put_object(remote_path, f)
                logger.warning(f'{log_file} backed up to OSS.')
            except Exception as e:
                logger.error(f'{log_file} failed to back up to OSS.', exc_info=True)

        # 更新最后备份时间
        with open(status_file_path, 'w') as file:
            file.write(datetime.now().isoformat())

        logger.warning('Backup completed successfully.')

        logger.warning(f'开始清理30天前日志文件，当前时间为{datetime.now()}')
        cur_date = datetime.now()
        date_30_days_ago = cur_date - timedelta(days=30)
        for obj in oss2.ObjectIterator(bucket, prefix=oss_path, delimiter='/'):
            try:
                if obj.is_prefix():
                    dir_name = obj.key
                    dir_date_str = dir_name[len(oss_path):-1]
                    dir_date = datetime.strptime(dir_date_str, '%Y-%m-%d')
                    if dir_date < date_30_days_ago:
                        for obj_to_delete in oss2.ObjectIterator(bucket, prefix=dir_name):
                            bucket.delete_object(obj_to_delete.key)
                        logger.warning(f"Deleted directory: {dir_name}")
            except Exception as e:
                logger.error(f"Failed to delete obj: {obj}")
        logger.warning('Log clean completed successfully.')
        time.sleep(random.randint(60*60, 3*60*60))


def async_sync():
    thread = threading.Thread(target=sync_files_oss)
    thread.start()


# 启动异步同步任务
if __name__ == '__main__':
    async_sync()
