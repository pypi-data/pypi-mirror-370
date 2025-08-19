import os

# 环境，eg dev
environment = os.environ.get("ENVIRONMENT")

# 日志相关的配置
log_directory = os.environ.get("log_directory_lib", default="/var/log/dde_agent")
log_file = os.environ.get("log_file_lib", default="app.log")
log_level = os.environ.get("log_level_lib", default="DEBUG")  # 需修改
log_format = os.environ.get("log_format_lib",
                            default="%(asctime)s - %(levelname)s - [%(process)d]  - %(correlation_id)s | %(asctime)s | %(message)s")
log_store = os.environ.get("log_store_lib", default="agent-dev")  # 需修改

# 大模型调用来源，当前source为服务名，eg core
source = os.environ.get("source_lib","unknow")

# 大模型调用限流次数，eg 15
llm_limit = os.environ.get("llm_limit_lib")

# openai的key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# lib库连接nacos的相关配置
dde_instance_name = os.environ.get("dde_instance_name_lib", default="dde-agent-lib")
dde_nacos_group = os.environ.get("dde_nacos_group_lib", default="dde")
dde_nacos_namespace_lib = os.environ.get('dde_nacos_namespace_lib')
dde_nacos_addr_lib = os.environ.get('dde_nacos_addr_lib')
dde_nacos_user_lib = os.environ.get('dde_nacos_user_lib')
dde_nacos_pwd_lib = os.environ.get('dde_nacos_pwd_lib')

# 日志上传oss
oss_path_pre = os.environ.get("oss_path_pre_lib")
