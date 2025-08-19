from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime, UTC


class CommonResponseHeader(BaseModel):
    # 요청 시간
    request_time: datetime = datetime.now(UTC)
    # 요청 Parameter
    request_params: dict


class CommonResponse(BaseModel):
    # response code (success / fail)
    success: Optional[str] = None
    # response message code
    msg_code: Optional[str] = None
    # response message
    msg: Optional[str] = None
    # 거래소 별 API 호출 시 반환되는 원본 Response 데이터
    info: Any


# 제네릭을 사용한 전체 Response 모델
T = TypeVar("T")


class GeneralResponse(BaseModel, Generic[T]):
    header: CommonResponseHeader
    response: CommonResponse
    info: Optional[T] = None
