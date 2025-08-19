from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Literal

from sqlalchemy import Boolean, Column, Date, Float, Integer, String
from ksxt.market.db import Base

from ksxt.market.us.stock import UsStockItem, UsStockMarket


# region typedef struct
# {
#     char    ncod[2+1];  /* National code        */
#     char    exid[3+1];  /* Exchange id          */
#     char    excd[3+1];  /* Exchange code        */
#     char    exnm[16+1]; /* Exchange name        */
#     char    symb[16+1]; /* Symbol               */
#     char    rsym[16+1]; /* realtime symbol      */
#     char    knam[64+1]; /* Korea name           */
#     char    enam[64+1]; /* English name         */
#     char    stis[1+1];  /* Security type        */
#                         /* 1:Index              */
#                         /* 2:Stock              */
#                         /* 3:ETP(ETF)           */
#                         /* 4:Warrant            */
#     char    curr[4+1];  /* currency             */
#     char    zdiv[1+1];  /* float position       */
#     char    ztyp[1+1];  /* data type            */
#     char    base[12+1]; /* base price           */
#     char    bnit[8+1];  /* Bid order size       */
#     char    anit[8+1];  /* Ask order size       */
#     char    mstm[4+1];  /* market start time(HHMM)  */
#     char    metm[4+1];  /* market end time(HHMM)    */
#     char    isdr[1+1];  /* DR 여부  :Y, N       */
#     char    drcd[2+1];  /* DR 국가코드          */
#     char    icod[4+1];  /* 업종분류코드         */
#     char    sjong[1+1]; /* 지수구성종목 존재 여부 */
#                         /*   0:구성종목없음      */
#                         /*   1:구성종목있음      */
#     char    ttyp[1+1];  /* Tick size Type        */
#     char    etyp[3+1]; /* 001: ETF 002: ETN 003: ETC 004: Others 005: VIX Underlying ETF 006: VIX Underlying ETN*/
#     char    ttyp_sb[3+1]; /* Tick size type 상세 (ttyp 9일 경우 사용) : 런던 제트라 유로넥스트  */
# }
# endregion typedef struct


@dataclass
class NyseItem(UsStockItem):
    CONTROL = [
        ("ncod", 2 + 1),
        ("exid", 3 + 1),
        ("excd", 3 + 1),
        ("exnm", 16 + 1),
        ("symb", 16 + 1),
        ("rsym", 16 + 1),
        ("knam", 64 + 1),
        ("enam", 64 + 1),
        ("stis", 1 + 1),
        ("curr", 4 + 1),
        ("zdiv", 1 + 1),
        ("ztyp", 1 + 1),
        ("base", 12 + 1),
        ("bnit", 8 + 1),
        ("anit", 8 + 1),
        ("mstm", 4 + 1),
        ("metm", 4 + 1),
        ("isdr", 1 + 1),
        ("drcd", 2 + 1),
        ("icod", 4 + 1),
        ("sjong", 1 + 1),
        ("ttyp", 1 + 1),
        ("etyp", 3 + 1),
        ("ttyp_sb", 3 + 1),
    ]

    # Notional code
    ncod: str
    # Exchange ID
    exid: str
    # Exchange Code
    excd: str
    # Exchange Name
    exnm: str
    # Symbol
    symb: str
    # Realtime Symbol
    rsym: str
    # Korean name
    knam: str
    # English name
    enam: str
    # Security Type
    stis: Literal["1", "2", "3", "4"]
    # currency
    curr: str
    # float position
    zdiv: str
    # data type
    ztyp: str
    # base price
    base: float
    # bid order size
    bnit: float
    # ask ordersize
    anit: float
    # market start time (HHMM)
    mstm: str
    # market end time (HHMM)
    metm: str
    # DR 여부 : Y/N
    isdr: bool
    # DR 국가코드
    drcd: str
    # 업종분류코드
    icod: str
    # 지수구성종목 존재 여부
    sjong: Literal["0", "1"]
    # Tick Size Type
    ttyp: str
    #
    etyp: Literal["001", "002", "003", "004", "005", "006"]
    # Tick size type 상세 (ttyp 8일 경우 사용) : 런던 제트라 유로넥스트
    ttyp_sb: str

    def __init__(self, data: str = None):
        if data:
            super().__init__(data)


class _NyseItem(Base):
    __tablename__ = "nyse"
    # Notional code
    ncod = Column(String)
    # Exchange ID
    exid = Column(String)
    # Exchange Code
    excd = Column(String)
    # Exchange Name
    exnm = Column(String)
    # Symbol
    symb = Column(String, primary_key=True)
    # Realtime Symbol
    rsym = Column(String)
    # Korean name
    knam = Column(String)
    # English name
    enam = Column(String)
    # Security Type
    stis = Column(String)
    # currency
    curr = Column(String)
    # float position
    zdiv = Column(String)
    # data type
    ztyp = Column(String)
    # base price
    base = Column(Float)
    # bid order size
    bnit = Column(Float)
    # ask ordersize
    anit = Column(Float)
    # market start time (HHMM)
    mstm = Column(String)
    # market end time (HHMM)
    metm = Column(String)
    # DR 여부 : Y/N
    isdr = Column(Boolean)
    # DR 국가코드
    drcd = Column(String)
    # 업종분류코드
    icod = Column(String)
    # 지수구성종목 존재 여부
    sjong = Column(String)
    # Tick Size Type
    ttyp = Column(String)
    #
    etyp = Column(String)
    # Tick size type 상세 (ttyp 8일 경우 사용) : 런던 제트라 유로넥스트
    ttyp_sb = Column(String)


class Nyse(UsStockMarket[NyseItem, _NyseItem]):
    def __init__(self, client):
        super().__init__(client, "nyse", "뉴욕", "https://new.real.download.dws.co.kr/common/master/nysmst.cod.zip")
