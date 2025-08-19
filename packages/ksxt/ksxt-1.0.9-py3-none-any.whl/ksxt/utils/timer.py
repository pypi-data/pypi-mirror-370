from datetime import datetime
import time

import pytz


@staticmethod
def now(base_market: str = "KRW"):
    if base_market == "KRW":
        return datetime.now(tz=pytz.timezone("Asia/Seoul"))
    elif base_market == "USD":
        return datetime.now(tz=pytz.timezone("US/Eastern"))
    else:
        return datetime.now(tz=pytz.utc)


@staticmethod
def seconds():
    return int(time.time())


@staticmethod
def milliseconds():
    return int(time.time() * 1_000)


@staticmethod
def create_datetime_with_today(hhmmss: str) -> datetime:
    """
    hhmmss 형식의 시간 문자열을 받아 오늘 날짜를 포함한 datetime 객체를 생성합니다.

    Parameters:
    hhmmss (str): "hhmmss" 형식의 시간 문자열 (예: "123045")

    Returns:
    datetime: 오늘 날짜와 주어진 시간이 포함된 datetime 객체
    """
    # 현재 날짜를 가져옴
    today = datetime.now()

    # hhmmss 문자열을 datetime 객체로 변환
    time_part = datetime.strptime(hhmmss, "%H%M%S").time()

    # 현재 날짜와 주어진 시간을 합쳐 datetime 객체 생성
    combined_datetime = datetime.combine(today, time_part)

    return combined_datetime
