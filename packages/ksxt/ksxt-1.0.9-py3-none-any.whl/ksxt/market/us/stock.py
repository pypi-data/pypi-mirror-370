from datetime import datetime
from typing import Generic, Iterable, Iterator, Literal, TypeVar, get_args
from ksxt.market.base import MarketItemBase, MarketBase
from ksxt.market.db import Base

STIS = {"1": "Index", "2": "Stock", "3": "ETP(ETF)", "4": "Warrant"}

SJONG = {"0": "구성종목없음", "1": "구성종목있음"}

ETYP = {
    "001": "ETF",
    "002": "ETN",
    "003": "ETC",
    "004": "Others",
    "005": "VIX Underlying ETF",
    "006": "VIX Underlying ETN",
}


class UsStockItem(MarketItemBase):
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

    @property
    def stis_name(self) -> str:
        return STIS.get(self.stis, None)

    @property
    def sjong_name(self) -> str:
        return SJONG.get(self.sjong, None)

    @property
    def etyp_name(self) -> str:
        return ETYP.get(self.etyp, None)

    def __init__(self, data: str):
        super().__init__(data, delimiter="\t")


t_item = TypeVar("t_item", bound=UsStockItem)
t_dbitem = TypeVar("t_dbitem", bound=Base)


class UsStockMarket(Generic[t_item, t_dbitem], MarketBase[t_item, t_dbitem]):
    def search(self, name: str, limit: int = 50) -> Iterable[t_item]:
        """
        종목 검색 (이름 기준)

        Args:
            name (str): 종목의 영어 이름
            limit (int, optional): 조회 갯수 제한. Defaults to 50.

        Returns:
            Iterable[t_item]: 종목 정보
        """
        _, db_type = get_args(self.__orig_bases__[0])  # type: ignore
        return self._search(db_type.enam, name, limit)  # type: ignore

    def items(self, offset: int = 0, limit: int = 100) -> Iterable[t_item]:
        """
        종목 조회 (offset 기준)

        Args:
            offset (int, optional): offset 정보. Defaults to 0.
            limit (int, optional): 조회 갯수 제한. Defaults to 100.

        Returns:
            Iterable[t_item]: 종목 정보
        """
        return super().items(offset, limit)

    def all(self) -> Iterator[t_item]:
        """
        모든 종목 조회

        Returns:
            _type_: 종목 정보

        Yields:
            Iterator[t_item]: 종목 정보
        """
        return super().all()  # type: ignore

    def __getitem__(self, code: str) -> t_item:
        """
        종목 검색 (종목코드 기준)

        Args:
            code (str): 종목 코드

        Returns:
            t_item: 종목 정보
        """
        """종목을 가져옵니다."""
        _, db_type = get_args(self.__orig_bases__[0])  # type: ignore
        return self._get(db_type.symb, code)
