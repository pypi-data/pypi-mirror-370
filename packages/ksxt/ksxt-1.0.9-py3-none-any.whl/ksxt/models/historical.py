from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ksxt.models.common import GeneralResponse


class OHLCVData(BaseModel):
    datetime: datetime
    open_price: float | int
    high_price: float | int
    low_price: float | int
    close_price: float | int
    acml_volume: float | int
    acml_amount: float | int


class HistoricalDataInfo(BaseModel):
    symbol: str
    security_name: Optional[str] = None
    history: List[OHLCVData]


# Historical Data에 대한 구체적인 Response 타입
class KsxtHistoricalDataResponse(GeneralResponse[HistoricalDataInfo]):
    pass
