from datetime import datetime
from pydantic import BaseModel
from ksxt.models.common import GeneralResponse


class TokenInfo(BaseModel):
    access_token: str
    token_type: str
    remain_time_second: float
    expired_datetime: datetime


class KsxtTokenResponse(GeneralResponse[TokenInfo]):
    pass
