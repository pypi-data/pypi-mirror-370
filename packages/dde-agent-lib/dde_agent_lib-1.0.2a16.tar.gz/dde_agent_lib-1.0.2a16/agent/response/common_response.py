from typing import Any

from pydantic import BaseModel, Field

from agent.exception.exception_constants import exception_constants


class CommonResponse(BaseModel):
    """通用返回"""
    code: str = Field(
        default=exception_constants.SUCCESS_CODE,
        description="返回码"
    )
    reason: str = Field(
        default=exception_constants.SUCCESS_MSG,
        description="返回描述"
    )
    data: Any = Field(
        default=None,
        description="返回数据"
    )
