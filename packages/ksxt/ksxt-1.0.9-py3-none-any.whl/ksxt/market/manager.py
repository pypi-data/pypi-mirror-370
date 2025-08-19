from datetime import date, datetime, timedelta
import logging
import os.path as path
import tempfile
from threading import Lock, Thread
import time
from typing import Iterable, Optional, Union
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from itertools import chain

from ksxt.market.db import Base, Market
from ksxt.market.base import MarketBase
from ksxt.market.krx.kosdaq import Kosdaq
from ksxt.market.krx.kospi import Kospi
from ksxt.market.krx.stock import KrxStockItem
from ksxt.market.logging import KsxtLogger
from ksxt.market.markets import MARKET_ITEM_TYPE, MARKET_TYPE, MARKETS
from ksxt.market.us.amex import Amex
from ksxt.market.us.nasdaq import Nasdaq
from ksxt.market.us.nyse import Nyse
from ksxt.market.us.stock import UsStockItem


class MarketManager(KsxtLogger):
    db_path: str
    engine: Engine
    markets: dict[str, MarketBase]

    _sessionmaker: sessionmaker
    _rth: int = 0
    _sstd: datetime
    _sl: Lock

    @property
    def kospi(self) -> Kospi:
        """코스피"""
        return self["kospi"]  # type: ignore

    @property
    def kosdaq(self) -> Kosdaq:
        """코스닥"""
        return self["kosdaq"]  # type: ignore

    @property
    def nasdaq(self) -> Nasdaq:
        """나스닥(National Association of Securities Dealers Automated Quotations)"""
        return self["nasdaq"]  # type: ignore

    @property
    def nyse(self) -> Nyse:
        """뉴욕증권거래소(the New York Stock Exchange)"""
        return self["nyse"]  # type: ignore

    @property
    def amex(self) -> Amex:
        """미국증권거래소(AMerican stock EXchange)"""
        return self["amex"]  # type: ignore

    @property
    def session(self) -> Session:
        """세션"""
        return self._sessionmaker()

    def stock(self, code: str) -> Union[KrxStockItem, UsStockItem]:
        """코스피/코스닥/뉴욕/나스닥/아멕스 종목"""
        return self.kospi[code] or self.kosdaq[code] or self.nyse[code] or self.nasdaq[code] or self.amex[code]  # type: ignore

    def __init__(
        self,
        db_path: Optional[str] = None,
        auto_sync: bool = False,
    ):
        if db_path is None:
            db_path = path.join(tempfile.gettempdir(), f".ksxt-cache_market.{datetime.now().strftime('%Y%m%d')}.db")

        self.db_path = db_path
        self.markets = {}
        self._sstd = None
        self._sl = Lock()
        self._create_database()

        if auto_sync:
            self._st_sync()

    def _create_database(self):
        self.engine = create_engine(
            f"sqlite:///{self.db_path}?check_same_thread=False"
        )  # maybe it will be ok for a while...
        Base.metadata.create_all(self.engine)
        self._sessionmaker = sessionmaker(bind=self.engine, autoflush=False)

    def _logger_ready(self, logger: logging.Logger):
        logger.debug(f"database open: {self.db_path}")

    def _init(self):
        self._sync_all(comp=False, verbose=False)

    def sync_at(self, code: str) -> datetime:
        """종목 정보를 마지막으로 업데이트한 시간"""
        return self.session.query(Market.sync_at).filter(Market.code == code).scalar()

    def sync_all(self):
        """모든 시장을 동기화합니다."""
        self._sync_all(comp=True, verbose=False)

    def _sync_all(self, comp: bool = False, verbose: bool = False) -> bool:
        with self._sl:
            now = datetime.now()

            if comp:
                self._sstd = now
            else:
                if self._sstd:
                    if now - self._sstd < timedelta(seconds=30):
                        if verbose:
                            self.logger.info("MARKET: too early to sync")

                        return False

                self._sstd = now

        for code in MARKETS:
            self[code].sync()

        return True

    def _get_market(self, session: Session, code: str) -> Market:
        market = self[code]

        if not market:
            raise KeyError(f"Unknown market: {code}")

        session.merge(market._market())
        session.commit()

        return session.query(Market).filter(Market.code == code).one()

    def _update_sync_at(self, code: str):
        """종목 정보를 업데이트한 시간을 업데이트합니다."""
        with self.session as sess:
            dm = self._get_market(sess, code)
            dm.sync_at = datetime.now()  # type: ignore
            sess.commit()

    def _st_sync(self):
        """자동동기화 스레드"""
        self._rth += 1
        tid = self._rth
        Thread(target=self._at_sync, args=(tid,), daemon=True).start()

    def _at_sync(self, tid: int):
        """자동 동기화"""
        n = False
        time.sleep(31)
        while self._rth == tid:
            try:
                if self._sync_all(comp=False, verbose=n):
                    self.logger.info("MARKET: auto-sync")
            except Exception as e:
                self.logger.error(f"MARKET: auto-sync exception: {e}")
            finally:
                if not n:
                    n = True
                time.sleep((60 * 60 * 24) + 5)

    def __getitem__(self, code: str) -> MARKET_TYPE:
        """시장"""
        if code not in self.markets:
            market = MARKETS[code](self)
            market._emit_logger(self.logger)
            self.markets[code] = market
        else:
            market = self.markets[code]
        return market  # type: ignore

    def search(self, keyword: str, origin: list[str] = None) -> dict[str, Iterable[MARKET_ITEM_TYPE]]:
        """종목 검색을 수행합니다.

        Args:
            keyword: 검색 키워드
            origin: 검색할 시장 (기본값: 모든 시장)
        """
        result = {}

        for market in self.markets.values():
            if not origin or market.code in origin:
                result[market.code] = market.search(keyword)

        return result

    def stock_search(self, keyword: str) -> dict[str, Iterable[KrxStockItem]]:
        """코스피/코스닥 종목 검색을 수행합니다."""
        return self.search(keyword, ["kospi", "kosdaq"])  # type: ignore

    def stock_search_combined(self, keyword: str) -> Iterable[KrxStockItem]:
        """코스피/코스닥 종목 검색을 수행합니다."""
        return chain(*self.stock_search(keyword).values())

    def search_one(self, keyword: str, origin: list[str] = None) -> MARKET_ITEM_TYPE:
        """종목 검색을 수행합니다.

        Args:
            keyword: 검색 키워드
            origin: 검색할 시장 (기본값: 모든 시장)
        """
        for market in self.markets.values():
            if not origin or market.code in origin:
                result = market.search_one(keyword)

                if result:
                    return result

        return None

    def stock_search_one(self, keyword: str) -> KrxStockItem:
        return self.search_one(keyword, ["kospi", "kosdaq"])  # type: ignore
