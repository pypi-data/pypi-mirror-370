# Public Library Imports
import pandas as pd
from typing import List
from abc import ABC, abstractmethod

# Private Library Imports
from mystockutil.logging.logging_setup import CustomAdapter
from mystockutil.logging.logging_setup import logger as original_logger

logger = CustomAdapter(original_logger, {'prefix': 'RDF'})

"""
PPD df를 기본으로 하여, 실시간으로 주가 정보를 업데이트하는 데이터프레임 클래스
"""

# Essential Imports
from mydataprovider.frame.odi.df_odi import odi
from mydataprovider.frame.ppd.df_ppd import DF_PPD, ppd_all, ppd_recent
from mydatahandler.handler.stock_data_handler import StockDataHandler
from mydatahandler.handler.functions.update_upsert_df import update_df_with_another_df
from mydataprovider.provider.web.web_data_provider import wdp


class _RDF:
    def __init__(
        self, 
        ppd:DF_PPD,
        ):
        
        self.ppd = ppd
        self.dh = StockDataHandler()


class RDF_init(_RDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialized_by_ddf = False
        
    def _init_with_ddf(self):
        """
        ddf를 이용하여 초기화한다.
        """
        # 이미 초기화 되었는지 확인
        if self.initialized_by_ddf:
            logger.warning("RDF is already initialized with ddf.")
            return
        # 초기화 코드
        self.dh.set_data(self.ppd.ddf)
        # 필요한 경우 초기화되었음을 표기
        if odi.is_krx_realtime_data_ready():
            # KRX 실시간 데이터가 실제 준비된 경우에만 True로 설정
            self.initialized_by_ddf = True
        return self


class RDF_wdp(RDF_init, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wdp = wdp  # WebDataProvider 인스턴스
        
    def add_acc(self, symbols: List[str]) -> List[str]:
        """
        symbols를 정확한 종목 코드 리스트에 추가한다.
        동시에, RDF의 df에도 정확한 정보를 업데이트 한다. 
        
        Returns: List[str]
            추가된 종목 코드 리스트를 반환한다.
        """
        exisint_acc_symbols = self.wdp.acc_symbols
        symbols = list(set(symbols) - set(exisint_acc_symbols))
        if len(symbols) == 0:
            logger.info("No new symbols to add to accurate stock list.")
            return []
        
        updated_df = self.wdp.fetch_acc(symbols)
        self.dh.update_df_with_another_df(updated_df)
        logger.info(f"Added {len(symbols)} symbols to accurate stock list.")
        
        return symbols


class RDF_df(RDF_wdp):
    @property
    def df(self) -> pd.DataFrame:
        """
        index = ['일자', '종목코드']
        columns = [
            '종목명', '마켓구분', '변동률', '시가총액', '상장주식수', 
            '거래량', '거래대금',
            '시가', '고가', '저가', '종가', '기준가', '전일대비', 
            '시가_krx', '고가_krx', '저가_krx', '종가_krx', '기준가_krx', '거래량_krx', '거래대금_krx', 
            '변동률_krx', '변동률_nxt', '변동률_장후', 
            '시가_nxt', '고가_nxt', '저가_nxt', '종가_nxt', '거래량_nxt', '거래대금_nxt',
            '전일종가_krx', '익일기준가_krx', 
            '금일가격조정멀티플', '누적가격조정멀티플', 
            '거래량양수', '연속거래일수',
            '상한가_krx', '하한가_krx', 
            '종가상한가여부', '종가하한가여부', '시가상한가여부', '시가하한가여부',
            '종가상하한가', '시가상하한가'
            ]
        """
        return self.dh.df
    
    @property
    def today_symbols(self) -> list[str]:
        """
        오늘의 종목 코드 리스트를 반환한다.
        """
        if not self.initialized_by_ddf:
            logger.error("RDF is not initialized with ddf. Calling _init_with_ddf() first.")
            # 초기화한다. 단, 9시 20분 이전에는 self.initialized_by_ddf를 True로 설정하지 않는다.
            # 초기화 후 return 하지 않고 코드를 계속 진행. 
            self._init_with_ddf()
        return self.dh.today_symbols


class RDF_refresh(RDF_df):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    @property
    def acc_symbols(self) -> List[str]:
        """
        정확한 정보를 저장하는 종목 코드 리스트를 반환합니다.
        """
        return self.wdp.acc_symbols
    def refresh(self, rdf_today:pd.DataFrame=None) -> pd.DataFrame:
        """
        rdf_today 데이터를 이용하여 업데이트하거나, wdp에서 오늘의 데이터를 가져와서 업데이트합니다.
        Returns: pd.DataFrame
            rdf_today 또는 오늘의 데이터프레임을 반환합니다.
        """
        if not self.initialized_by_ddf:
            logger.warning("RDF is not initialized with ddf. Calling _init_with_ddf() first.")
            # 초기화한다. 단, 9시 20분 이전에는 self.initialized_by_ddf를 True로 설정하지 않는다.
            # 초기화 후 return 하지 않고 코드를 계속 진행. 
            self._init_with_ddf()
        # 금일이 휴일이 경우, 실시간 업데이트를 하지 않는다. 
        if odi.today_is_holiday:
            return pd.DataFrame(columns=[])
        # KRX 실시간 데이터로 업데이트
        if rdf_today is None:
            # 오늘의 실시간 데이터를 가져온다.
            if not odi.today_is_openday:
                logger.warning("Today is not an open day. Cannot fetch real-time data.")
            rdf_today = self.wdp.fetch_all()
        # Essential codes
        df = self.dh.df.copy()
        fitted_df = update_df_with_another_df(
            df=df,
            another_df = rdf_today
            )
        # 금일 종목정보를 반영하여 PPD를 만든다.
        for ppdp in self.ppd.ppdps:
            fitted_df = ppdp.custom_data_fitting_as_refresh(
                df=fitted_df,
            )
        self.dh.df = fitted_df
        logger.info("RDF has been refreshed with KRX real-time data. Returns today's data.")
        return rdf_today


class RDF(RDF_refresh):
    """
    rdf.ready()로 초기화. 
    rdf.add_symbol_in_accurate('005930')  # 정확한 금일 데이터(거래량/거래대금)을 측정
    rdf.refresh()  # 실시간 데이터로 업데이트
    Fixme: - 9시 20분 이전 실행에 대해서는 체크하지 않음 
    """
    def __init__(
        self,
        ppd:DF_PPD,
        ):
        super().__init__(
            ppd=ppd,
            )
    
    def ready(self):
        """RDF를 준비 상태로 만듭니다.
        """
        # PPD를 준비 상태로 만듭니다.
        self.ppd.ready()
        # RDF 초기화
        self._init_with_ddf()

rdf_recent = RDF(ppd=ppd_recent)
rdf_all = RDF(ppd=ppd_all)

if __name__ == "__main__":
    from mystockutil.df.format import myprint as print
    ppd = ppd_recent
    rdf = RDF(ppd=ppd)
    rdf.ready()
    
    symbols = ['005930', '000660', '035420', '005380', '068270', '012450']
    symbols += ['103140']
    
    newly_added = rdf.add_acc(symbols)
    df = rdf.dh.today_by_symbols(symbols)
    print(rdf.dh.today_by_symbols(symbols))
    
    print("Finished")