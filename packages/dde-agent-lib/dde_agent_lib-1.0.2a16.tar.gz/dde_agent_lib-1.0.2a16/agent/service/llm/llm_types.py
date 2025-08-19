from typing import Optional, List, Dict, Any, TypedDict


class LLMRequest(TypedDict, total=False):
    """LLM请求参数对象"""
    service_url: str
    chat_content: str
    system: Optional[str]
    history: Optional[List[List[str]]]
    back_service_urls: Optional[List[str]]
    auto_use_system_back_service: bool
    rid: Optional[str | int]
    connect_timeout: Optional[float]
    ft_timeout: Optional[float]
    total_timeout: Optional[float]
    request_timeout: Optional[float]
    extra_params: Dict[str, Any]
