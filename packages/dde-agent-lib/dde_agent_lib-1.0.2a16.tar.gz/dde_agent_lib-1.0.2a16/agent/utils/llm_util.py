from typing import Optional, Dict, Any, List, Tuple

from agent.utils.nacos_val import get_system_config_from_nacos
from agent.utils.dde_logger import dde_logger as logger
from asgi_correlation_id import correlation_id
from agent.service.llm.llm_types import LLMRequest
import asyncio
import aiohttp
import json
import time
from aiohttp import ClientTimeout
import requests
from urllib.parse import urlparse
from agent.utils.dde_logger import statis_log
from agent.utils.token_util import count_tokens


def build_service_urls(
        primary_url: str,
        back_urls: Optional[List[str]],
        use_system_back: bool
) -> List[str]:
    system_config = get_system_config_from_nacos()
    system_back_service = system_config["llm_config"]["system_back_service"]
    """构建完整的服务URL列表，包括备用服务"""
    urls = [primary_url] + (back_urls or [])
    if use_system_back:
        if isinstance(system_back_service, list):
            urls.extend(system_back_service)
        else:
            urls.append(system_back_service)
    unique_urls = list(dict.fromkeys(urls))
    return unique_urls


def filter_supported_params(params: Dict[str, Any]) -> Dict[str, Any]:
    system_config = get_system_config_from_nacos()
    llm_supported_params = system_config["llm_config"]["llm_supported_params"]
    """过滤掉LLM服务不支持的参数"""
    filtered = {k: v for k, v in params.items() if k in llm_supported_params}
    unsupported = {k: v for k, v in params.items() if k not in llm_supported_params}

    if unsupported:
        print(f"忽略不支持的参数: {unsupported}")
    return filtered


def build_messages(
        system: Optional[str],
        history: Optional[List[List[str]]],
        chat_content: str
) -> List[Dict[str, str]]:
    """构建符合OpenAI格式的消息列表"""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})

    if history:
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})

    messages.append({"role": "user", "content": chat_content})
    return messages


async def handle_stream_output(url: str, rid: str, messages,  stream, request_increase_mode: bool):
    current_content = []
    current_reasoning = []

    system_config = get_system_config_from_nacos()
    log_mode = system_config["llm_config"]["log_mode"]  # 支持 original+all、original+simple、original、all、simple、none
    final_content = ""
    final_reasoning = ""
    i = 0
    async for chunk in stream:
        if "original" in log_mode:
            logger.info(f"llm_client, rid = {rid} , chunk = {chunk}")

        # 从chunk中安全获取choices（默认空列表）
        choices = chunk.get('choices', [])
        # 取第一个choice（默认空字典）
        first_choice = choices[0] if choices else {}
        # 从choice中安全获取delta（默认空字典）
        delta = first_choice.get('delta', {})

        # 安全获取content和reasoning_content（默认空字符串）
        content = delta.get('content', '') or ''
        reasoning_content = delta.get('reasoning_content', '') or ''

        if content == "" and reasoning_content == "":
            continue

        if request_increase_mode:
            current_content.append(content)
            current_reasoning.append(reasoning_content)
            log_llm_output(content, reasoning_content, rid, i)
            yield {
                "content": content,
                "reasoning_content": reasoning_content,
                "rid": rid
            }
        else:
            current_content.append(content)
            current_reasoning.append(reasoning_content)
            all_content = ''.join(current_content)
            all_reasoning = ''.join(current_reasoning)
            log_llm_output(all_content, all_reasoning, rid, i)
            yield {
                "content": all_content,
                "reasoning_content": all_reasoning,
                "rid": rid
            }
        i = i + 1
    add_stream_llm_call_token_statis(url, rid, json.dumps( messages),''.join(current_reasoning) +''.join(current_content))
    log_llm_output(final_content, final_reasoning, rid, i, True)


def log_llm_output(content, reasoning_content, rid: str, i: int, is_final_chunk=False):
    system_config = get_system_config_from_nacos()
    log_mode = system_config["llm_config"]["log_mode"]
    if "all" in log_mode or is_final_chunk or i == 0:
        logger.info(f"llm_client, i = {i} , is_final_chunk = {is_final_chunk} , rid = {rid} , content = {content} , reasoning_content = {reasoning_content} ")
    elif "simple" in log_mode:
        log_length = system_config["llm_config"]["log_length"]
        log_content = content
        log_reasoning_content = reasoning_content
        split_len = int(log_length / 2)
        if len(log_content) > log_length:
            log_content = log_content[:split_len] + "[...]" + log_content[-split_len:]
        if len(log_reasoning_content) > log_length:
            log_reasoning_content = log_reasoning_content[:split_len] + "[...]" + log_reasoning_content[-split_len:]
        logger.info(f"llm_client, i = {i} , is_final_chunk = {is_final_chunk} , rid = {rid} , log_content = {log_content} ,  log_reasoning_content = {log_reasoning_content} ")

def get_llm_model(service_url: str) -> Optional[str]:
    url = f"{service_url}/models"
    try:
        response = requests.get(url,headers={"Content-Type": "application/json"}, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data.get("data"), list) and len(data["data"]) > 0:
                return data["data"][0].get("id")
        return "None"
    except requests.exceptions.Timeout:
        logger.error(f"get_llm_model timeout, service_url={service_url}", exc_info=True)
        return "None"
    except requests.exceptions.RequestException:
        logger.error(f"get_llm_model exception, service_url={service_url}", exc_info=True)
        return "None"

def get_llm_config(service_url: str) -> Dict[str, Any]:
    """获取LLM服务配置，支持服务标签和URL匹配"""
    system_config = get_system_config_from_nacos()
    service_type_configs = system_config["llm_config"]["service_config"]
    default_config = system_config["llm_config"]["default_service_config"]

    result_config = default_config.copy()
    tag = "default"

    # 解析带标签的服务URL
    if "::" in service_url:
        parts = service_url.split("::")
        if len(parts) == 2:
            result_config["url"] = parts[0]
            tag = parts[1]
        else:
            raise ValueError(f"无效的带标签服务URL格式: {service_url}")
    else:
        result_config["url"] = service_url

    # 查找匹配的服务类型配置
    for config in service_type_configs:
        for url_match in config["url_match"]:
            if url_match in service_url and tag == config["tag"]:
                # 处理普通键的覆盖
                for k in ["model", "api_key", "feature"]:
                    if k in config and config[k] is not None:
                        result_config[k] = config[k]

                # 特殊处理param字典的合并
                if "param" in config and config["param"] is not None:
                    # 确保result_config中有param键且为字典
                    if "param" not in result_config:
                        result_config["param"] = {}
                    elif not isinstance(result_config["param"], dict):
                        result_config["param"] = {}

                    # 合并param字典，用config中的值覆盖result_config中的值
                    result_config["param"].update(config["param"])

                break

    return result_config


def prepare_llm_request(request: LLMRequest, is_stream: bool) -> Dict[str, Any]:
    service_url = request["service_url"]
    chat_content = request["chat_content"]
    system = request.get("system")
    history = request.get("history")
    back_service_urls = request.get("back_service_urls")
    auto_use_system_back_service = request.get("auto_use_system_back_service", True)
    rid = request.get("rid")
    connect_timeout = request.get("connect_timeout")
    ft_timeout = request.get("ft_timeout")
    total_timeout = request.get("total_timeout")
    request_timeout = request.get("request_timeout")

    # 获取系统配置
    system_config = get_system_config_from_nacos()
    default_connect_timeout = system_config["llm_config"]["timeout"]["stream_connect" if is_stream else "invoke_connect"]
    default_ft_timeout = system_config["llm_config"]["timeout"]["stream_ft"] if is_stream else None
    default_total_timeout = system_config["llm_config"]["timeout"]["stream" if is_stream else "invoke"]
    default_request_timeout = system_config["llm_config"]["timeout"]["stream_request" if is_stream else "invoke_request"]

    log_mode = system_config["llm_config"]["log_mode"]

    # 构建服务URL列表（主服务+备用服务）
    all_urls = build_service_urls(service_url, back_service_urls, auto_use_system_back_service)

    # 处理超时和请求ID
    if not connect_timeout:
        connect_timeout = default_connect_timeout
    if not ft_timeout:
        ft_timeout = default_ft_timeout
    if not total_timeout:
        total_timeout = default_total_timeout
    if not request_timeout:
        request_timeout = default_request_timeout
    if not rid:
        rid = str(correlation_id.get()) or "agent"

    # 构建消息并处理日志格式化
    messages = build_messages(system, history, chat_content)
    message_str = json.dumps(messages, ensure_ascii=False)
    message_len = len(message_str)
    if not "all" in log_mode and len(message_str) > 120:
        message_str = message_str[:60] + "[...]" + message_str[-60:]

    return {
        "all_urls": all_urls,
        "connect_timeout": connect_timeout,
        "ft_timeout": ft_timeout,
        "total_timeout": total_timeout,
        "request_timeout": request_timeout,
        "rid": rid,
        "messages": messages,
        "message_str": message_str,
        "message_len": message_len,
        "log_mode": log_mode,
        "system_config": system_config
    }


def prepare_llm_client(url: str, new_rid: str, extra_params: Dict[str, Any]) -> Tuple[Dict[str, Any], str, str, str]:
    llm_config = get_llm_config(url)
    model = llm_config["model"]
    api_key = llm_config["api_key"]
    service_url = llm_config["url"]
    # 处理参数（合并配置参数和额外参数）
    config_params = llm_config.get("param", {})
    config_params.update(extra_params)
    filtered_params = filter_supported_params(config_params)
    trace_info = {"rid": new_rid, "request_id": new_rid}
    filtered_params.update(trace_info)

    #传入的max_completion_tokens不能比模型配置的更大
    config_max_tokens = config_params.get("max_completion_tokens")
    extra_max_tokens = extra_params.get("max_completion_tokens")
    if config_max_tokens is not None and extra_max_tokens is not None and config_max_tokens !="empty" and extra_max_tokens !="empty":
        final_max_completion_tokens = min(int(config_max_tokens), int(extra_max_tokens))
        filtered_params["max_completion_tokens"] = final_max_completion_tokens

    # 处理max_completion_tokens参数兼容
    if "max_completion_tokens" in filtered_params:
        if filtered_params["max_completion_tokens"] == "empty":
            del filtered_params["max_completion_tokens"]
        else:
            filtered_params["max_tokens"] = filtered_params["max_completion_tokens"]
    if model == "autoget":
        model = get_llm_model(service_url)
    return filtered_params, model, api_key, service_url


def abort_llm_request(service_url: str, rid: str):
    t1 = time.time()
    try:
        parsed = urlparse(service_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        logger.info(f"尝试停止流式输出，service_url:{service_url}, rid: {rid}")
        # 准备请求数据
        request_data = {"rid": rid}
        # 发送中止请求
        response = requests.post(
            base_url + "/abort_request",
            json=request_data,
            timeout=10  # 设置合理的超时时间
        )
        if response.status_code == 200:
            elapsed_time_ms = int((time.time() - t1) * 1000)
            statis_log("normal", "common_api", "default", "llm_client", "abort_" + service_url, "success", elapsed_time_ms, service_url, rid)
        else:
            error_msg = f"中止请求失败，HTTP状态码: {response.status_code}"
            logger.error(f"abort_streaming_output exception,service_url={service_url}, rid={rid}, {error_msg}", exc_info=True)
            statis_log("normal", "common_api", "default", "llm_client", "abort_" + service_url, "fail", response.status_code, service_url, rid)

    except Exception as e:
        error_msg = f"停止流式输出时发生异常: {str(e)}"
        logger.error(f"abort_streaming_output exception, rid={rid}, {error_msg}", exc_info=True)
        statis_log("normal", "common_api", "default", "llm_client", "abort_" + service_url, "exception", e, service_url, rid)

def add_stream_llm_call_token_statis(service_url: str, rid: str, input_content:str, output_content:str):
    try:
        if not input_content or not output_content:
            return
        input_token_count = count_tokens(input_content)
        output_token_count = count_tokens(output_content)
        total_token_count = input_token_count + output_token_count
        add_llm_call_token_statis(service_url, rid, input_token_count, output_token_count, total_token_count)
    except Exception as e:
        logger.error(f"add_stream_llm_call_token_statis exception, service_url={service_url}, rid={rid}, {e}", exc_info=True)
def add_invoke_llm_call_token_statis(service_url: str, rid: str, response):
    try:
        usage = response.get('usage')
        if not usage:
            return
        input_tokens = usage.get('prompt_tokens')
        output_tokens = usage.get('completion_tokens')
        total_tokens = usage.get('total_tokens')
        add_llm_call_token_statis(service_url, rid, input_tokens, output_tokens, total_tokens)
    except Exception as e:
        logger.error(f"add_invoke_llm_call_token_statis exception, service_url={service_url}, rid={rid}, {e}", exc_info=True)

def add_llm_call_token_statis(service_url: str, rid: str, input_tokens: int, output_tokens: int, total_tokens: int):
    system_config = get_system_config_from_nacos()
    token_statis_service_url = system_config["llm_config"].get("token_statis_service_url")
    if not token_statis_service_url or token_statis_service_url == "none":
        return
    try:
        request_data = {"tokenId": rid,"tokenCount":total_tokens}
        response = requests.post(
            token_statis_service_url,
            json=request_data,
            timeout=10  # 设置合理的超时时间
        )
        if response.status_code == 200:
            logger.info(f"添加token统计成功，service_url:{service_url}, rid: {rid}, input_tokens:{input_tokens}, output_tokens:{output_tokens}, total_tokens:{total_tokens}")
        else:
            logger.error(f"添加token统计失败，service_url:{service_url}, rid: {rid}, input_tokens:{input_tokens}, output_tokens:{output_tokens}, total_tokens:{total_tokens},HTTP状态码: {response.status_code}")
    except Exception:
        logger.error(f"添加token统计异常，service_url:{service_url}, rid: {rid}, input_tokens:{input_tokens}, output_tokens:{output_tokens}, total_tokens:{total_tokens}", exc_info=True)

async def get_first_token(response):
    async for line in response.content:
        await asyncio.sleep(2)  # 模拟延迟，触发超时
        line_str = line.decode('utf-8').strip()
        if line_str.startswith('data: '):
            json_str = line_str[len('data: '):]
            if json_str == '[DONE]':
                return None
            return json.loads(json_str)
    return None


async def read_remaining_chunks(response):
    """处理剩余流式数据"""
    async for line in response.content:
        line_str = line.decode('utf-8').strip()
        if line_str.startswith('data: '):
            json_str = line_str[len('data: '):]
            if json_str == '[DONE]':
                break
            yield json.loads(json_str)


async def stream_call_llm(service_url, api_key="EMPTY", model="EMPTY", messages=None, extra_body=None, connect_timeout=30.0, first_token_timeout=60.0, total_timeout=3600.0):
    # 在函数内部初始化可变参数
    if messages is None:
        messages = []  # 每次调用都创建新列表
    if extra_body is None:
        extra_body = {}  # 每次调用都创建新字典
    headers = {
        'Authorization': 'Bearer ' + api_key,
        'Content-Type': 'application/json',
    }
    data = {
        "model": model,
        "messages": messages,
        "stream": True,
        **extra_body
    }

    async with aiohttp.ClientSession(timeout=ClientTimeout(connect=connect_timeout, total=total_timeout)) as session:
        async with session.post(service_url + "/chat/completions", headers=headers, json=data) as response:
            response.raise_for_status()
            first_token_task = asyncio.create_task(get_first_token(response))
            try:
                first_token = await asyncio.wait_for(
                    first_token_task, timeout=first_token_timeout
                )
            except asyncio.TimeoutError:
                first_token_task.cancel()
                abort_llm_request(service_url, extra_body.get("rid"))
                raise asyncio.TimeoutError(f"调用大模型首token超时（超过{first_token_timeout}秒）")

            if not first_token:
                abort_llm_request(service_url, extra_body.get("rid"))
                raise asyncio.TimeoutError("调用大模型未收到有效首chunk")
            yield first_token
            try:
                async for chunk in read_remaining_chunks(response):
                    yield chunk
            except asyncio.TimeoutError:
                abort_llm_request(service_url, extra_body.get("rid"))
                raise asyncio.TimeoutError(f"调用大模型请求超时（超过{total_timeout}秒）")


def invoke_call_llm(service_url, api_key="EMPTY", model="EMPTY", messages=None, extra_body=None, connect_timeout=30.0, total_timeout=1800.0):
    if messages is None:
        messages = []
    if extra_body is None:
        extra_body = {}

    headers = {
        'Authorization': 'Bearer ' + api_key,
        'Content-Type': 'application/json',
    }
    data = {
        "model": model,
        "messages": messages,
        "stream": False,  # 非流式请求
        **extra_body
    }
    try:
        response = requests.post(service_url + "/chat/completions", headers=headers, json=data, timeout=(connect_timeout, total_timeout))
        response.raise_for_status()  # 检查HTTP状态码
        return response.json()
    except requests.exceptions.ConnectTimeout:
        abort_llm_request(service_url, extra_body.get("rid"))
        raise TimeoutError(f"调用大模型连接超时（超过{connect_timeout}秒）")
    except requests.exceptions.ReadTimeout:
        abort_llm_request(service_url, extra_body.get("rid"))
        raise TimeoutError(f"调用大模型读取超时（超过{total_timeout}秒）")
