import json
from typing import Dict, Any, AsyncGenerator
from agent.service.llm.llm_types import LLMRequest
from agent.utils import llm_util
from agent.utils.nacos_val import get_system_config_from_nacos
import uuid, time
from agent.utils.dde_logger import statis_log
from agent.utils.dde_logger import dde_logger as logger


class LLMClient:

    @staticmethod
    def get_llm_property(service_url: str) -> Dict[str, Any]:
        return llm_util.get_llm_config(service_url)

    @staticmethod
    def get_base_common_model(model_name: str = "qwen72b"):
        system_config = get_system_config_from_nacos()
        base_common_model_config = system_config["llm_config"]["base_common_model"]
        qwen72b = base_common_model_config["qwen72b"]
        return base_common_model_config.get(model_name, qwen72b)

    @staticmethod
    def abort_llm_request(service_url: str, rid: str):
        llm_util.abort_llm_request(service_url, rid)

    @staticmethod
    async def llm_stream(
            request: LLMRequest,
            request_increase_mode: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式调用LLM服务"""
        # 准备请求参数
        prepared_data = llm_util.prepare_llm_request(request, is_stream=True)
        all_urls = prepared_data["all_urls"]
        connect_timeout = prepared_data["connect_timeout"]
        ft_timeout = prepared_data["ft_timeout"]
        total_timeout = prepared_data["total_timeout"]
        request_timeout = prepared_data["request_timeout"]  # 总请求超时时间
        rid = prepared_data["rid"]
        messages = prepared_data["messages"]
        message_str = prepared_data["message_str"]
        message_len = prepared_data["message_len"]

        errors = []
        first_valid_chunk_received = False
        start_time = time.time()  # 记录整个请求开始时间
        timeout_info = f"connect:{connect_timeout},ft:{ft_timeout},total:{total_timeout}, request:{request_timeout}"
        # 遍历所有服务URL
        for url in all_urls:
            # 计算已消耗时间和剩余时间
            elapsed_time = time.time() - start_time
            remaining_time = request_timeout - elapsed_time
            if remaining_time <= 0:
                logger.error(f"请求总超时，已消耗时间: {elapsed_time:.2f}s，超过限制: {request_timeout}s")
                errors.append(f"请求总超时，剩余时间不足")
                raise TimeoutError(f"调用大模型超过总请求限制时间（超过{request_timeout}秒）")

            # 本次调用的超时时间为原始total_timeout和剩余时间的最小值
            current_total_timeout = min(total_timeout, remaining_time)
            new_rid = f"{rid}_{uuid.uuid4()}"
            model = ""
            filtered_params = {}
            try:
                logger.info(
                    f"尝试连接服务URL: {url}, "
                    f"总超时限制: {request_timeout}s, "
                    f"已消耗: {elapsed_time:.2f}s, "
                    f"本次超时: {current_total_timeout:.2f}s"
                )
                timeout_info = f"connect:{connect_timeout},ft:{ft_timeout},total:{total_timeout}, request:{request_timeout}, current_total_time:{current_total_timeout}"
                t1 = time.time()
                filtered_params, model, api_key,service_url = llm_util.prepare_llm_client(
                    url, new_rid, request.get("extra_params", {})
                )

                # 调用流式接口，使用计算后的当前超时时间
                stream_response = llm_util.stream_call_llm(
                    service_url,
                    api_key=api_key,
                    model=model,
                    messages=messages,
                    extra_body=filtered_params,
                    connect_timeout=connect_timeout,
                    first_token_timeout=ft_timeout,
                    total_timeout=current_total_timeout  # 使用调整后的超时时间
                )

                # 处理流式响应
                first_token_time = 0
                is_first_token = True

                async for _item in llm_util.handle_stream_output(url, new_rid, messages,  stream_response, request_increase_mode):
                    # 记录首条token的响应时间
                    if is_first_token:
                        first_token_time = int((time.time() - t1) * 1000)
                        is_first_token = False

                    # 标记已收到有效chunk
                    if not first_valid_chunk_received:
                        first_valid_chunk_received = True

                    #  yield流式结果
                    yield _item

                # 所有chunk处理完成且成功接收，记录日志并返回
                if first_valid_chunk_received:
                    elapsed_time_ms = int((time.time() - t1) * 1000)
                    statis_log(
                        "normal", "stream_api", "default", "llm_client",
                        f"stream_{url}", "success", elapsed_time_ms,
                        first_token_time, url, new_rid, model,
                        filtered_params, timeout_info, message_str, message_len
                    )
                    return

            except Exception as e:
                # 已收到有效chunk但后续出错，不再重试备用服务
                if first_valid_chunk_received:
                    statis_log(
                        "normal", "stream_api", "default", "llm_client",
                        f"stream_{url}", "exception", e, "已收到有效chunk，后续出错不再重试",
                        url, all_urls, new_rid, model, filtered_params, timeout_info, message_str, message_len
                    )
                    return
                # 未收到有效chunk，记录错误并尝试下一个备用服务
                else:
                    error_msg = f"服务URL {url} 调用失败: {str(e)}"
                    errors.append(error_msg)
                    statis_log(
                        "normal", "stream_api", "default", "llm_client",
                        f"stream_{url}", "exception", e, "未收到有效chunk，尝试下一个服务",
                        url, all_urls, new_rid, model, filtered_params, timeout_info, message_str, message_len
                    )
                    logger.error(f"call llm exception, rid={new_rid}, url={url}, {error_msg}", exc_info=True)
                    continue

        # 所有服务均失败，抛出异常
        logger.error(f"所有服务调用失败, {errors}, rid_pre={rid}", exc_info=True)
        raise Exception(f"所有服务URL调用失败: {errors}, rid_pre={rid}")

    @staticmethod
    def llm_invoke(request: LLMRequest):
        prepared_data = llm_util.prepare_llm_request(request, is_stream=False)
        all_urls = prepared_data["all_urls"]
        connect_timeout = prepared_data["connect_timeout"]
        total_timeout = prepared_data["total_timeout"]
        request_timeout = prepared_data["request_timeout"]  # 总请求超时时间
        rid = prepared_data["rid"]
        messages = prepared_data["messages"]
        message_str = prepared_data["message_str"]
        message_len = prepared_data["message_len"]

        errors = []
        start_time = time.time()  # 记录整个请求开始时间
        timeout_info = f"connect:{connect_timeout},total:{total_timeout}, request:{request_timeout}"
        for url in all_urls:
            # 计算已消耗时间和剩余时间
            elapsed_time = time.time() - start_time
            remaining_time = request_timeout - elapsed_time
            if remaining_time <= 0:
                logger.error(f"请求总超时，已消耗时间: {elapsed_time:.2f}s，超过限制: {request_timeout}s")
                errors.append(f"请求总超时，剩余时间不足")
                raise TimeoutError(f"调用大模型超过总请求限制时间（超过{request_timeout}秒）")

            # 本次调用的超时时间为原始total_timeout和剩余时间的最小值
            current_total_timeout = min(total_timeout, remaining_time)
            new_rid = rid + "_" + str(uuid.uuid4())
            model = ""
            filtered_params = {}
            try:
                logger.info(
                    f"尝试连接服务URL: {url}, "
                    f"总超时限制: {request_timeout}s, "
                    f"已消耗: {elapsed_time:.2f}s, "
                    f"本次超时: {current_total_timeout:.2f}s"
                )
                timeout_info = f"connect:{connect_timeout},total:{total_timeout}, request:{request_timeout}, current_total_time:{current_total_timeout}"
                t1 = time.time()
                filtered_params, model, api_key, service_url = llm_util.prepare_llm_client(
                    url, new_rid, request.get("extra_params", {})
                )
                response = llm_util.invoke_call_llm(
                    service_url,
                    api_key=api_key,
                    model=model,
                    messages=messages,
                    extra_body=filtered_params,
                    connect_timeout=connect_timeout,
                    total_timeout=current_total_timeout  # 使用调整后的超时时间
                )
                logger.info(f"llm_invoke response, rid: {new_rid}, url = {url} , filtered_params: {filtered_params} , message: {message_str} ,  response: {response}")
                choices = response.get('choices', [])
                if choices:
                    first_choice = choices[0] if len(choices) > 0 else {}
                    message = first_choice.get('message', {})
                    content = message.get('content', '') or ""
                    reasoning_content = message.get('reasoning_content', '') or ""
                    is_valid = bool(content) or bool(reasoning_content)
                    if is_valid:
                        elapsed_time_ms = int((time.time() - t1) * 1000)
                        res = {
                            "content": content,
                            "reasoning_content": reasoning_content,
                            "rid": new_rid
                        }
                        res_str = json.dumps(res, ensure_ascii=False)
                        res_len = len(res_str)
                        llm_util.add_invoke_llm_call_token_statis(url, new_rid,response)
                        statis_log("normal", "common_api", "default", "llm_client", "invoke_" + url, "success", elapsed_time_ms, url, new_rid, model, filtered_params, timeout_info, f"[{message_len}]{message_str}", f"[{res_len}]{res_str}")
                        return res
                    else:
                        statis_log("normal", "common_api", "default", "llm_client", "invoke_" + url, "fail", "response.choices response invalid", url, new_rid, model, filtered_params, timeout_info, f"[{message_len}]{message_str}")
                else:
                    statis_log("normal", "common_api", "default", "llm_client", "invoke_" + url, "fail", "response.choices empty", url, new_rid, model, filtered_params, timeout_info, f"[{message_len}]{message_str}")
            except Exception as e:
                statis_log("normal", "common_api", "default", "llm_client", "invoke_" + url, "exception", e, url, new_rid, model, filtered_params, timeout_info, f"[{message_len}]{message_str}")
                error_msg = f"服务URL {url} 调用失败: {str(e)}"
                logger.error(f"call llm exception, rid={new_rid}, url={url}, {error_msg}", exc_info=True)
                errors.append(error_msg)
        logger.error(f"call llm final fail, {errors}, rid_pre={rid}", exc_info=True)
        raise Exception(f"所有服务URL调用失败: {errors}, rid_pre={rid}")


# 模块级API接口
_client = LLMClient()
get_llm_property = _client.get_llm_property
get_base_common_model = _client.get_base_common_model
llm_stream = _client.llm_stream
llm_invoke = _client.llm_invoke
abort_llm_request = _client.abort_llm_request
