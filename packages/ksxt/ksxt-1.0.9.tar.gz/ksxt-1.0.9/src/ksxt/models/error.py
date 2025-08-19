from typing import Optional
from pydantic import BaseModel

from ksxt.models.common import GeneralResponse


class ErrorInfo(BaseModel):
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class KsxtErrorResponse(GeneralResponse[ErrorInfo]):
    pass
