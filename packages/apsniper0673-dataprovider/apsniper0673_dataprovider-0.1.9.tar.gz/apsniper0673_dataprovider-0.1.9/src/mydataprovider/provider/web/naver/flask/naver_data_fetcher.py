import pandas as pd
import time
from typing import Any, List

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(original_logger, {'prefix': 'NDF'})

"""
naver_data_provider_server에서 사용하기위해
Naver에서 Data를 지속적으로 Fetch하는 클래스입니다. 
이 모듈을 직접 import하여 로컬에서 사용할 수도 있습니다. 
단, 이 경우 auto_update가 가능하지 않습니다.
"""

# Essential imports
from mydataprovider.utility.crawler.naver import fetch_acc_stock_info_from_naver_as_dict, get_multiple_current_ohlcv_from_naver
from mydatahandler.handler.singleday_data_handler import SingledayDataHandler
from mydatahandler.handler.stock_data_handler import StockDataHandler
from mydatahandler.handler.functions.update_upsert_df import update_df_with_another_df, upsert_df_with_similar_df

class NaverAccTodayStockInfo:
    """
    네이버에서 정확한 종목 정보를 가져오는 클래스입니다.
    즉, 넥스트레이드 거래량 및 거래대금이 포함된 종목 정보를 제공합니다.
    """
    def __init__(self):
        self.columns = [
            '종목명', '현재가', '전일가', '기준가', '전일대비', '변동률', '시가', '고가', '저가', '상한가', '하한가', 
            '거래량', '거래량_krx', '거래량_nxt',
            '거래대금', '거래대금_krx', '거래대금_nxt', '시가총액', '상장주식수',
            ]
        # index로 종목코드를 사용하면서 동시에 종목코드 칼럼도 유지한다. 
        self.dh = StockDataHandler()
        self.today = pd.to_datetime('today').date() # 오늘 날짜
        self.last_fetch_time = 0 # 마지막으로 종목정보를 가져온 시간
        self.fetch_interval = 1.0 # 
    @property
    def df(self) -> pd.DataFrame:
        """
        종목 정보를 담고 있는 DataFrame을 반환합니다.
        index = ['일자', '종목코드']
        columns = [
            '종목명', '현재가', '전일가', '기준가', '전일대비', '변동률', '시가', '고가', '저가', '상한가', '하한가', 
            '거래량', '거래량_krx', '거래량_nxt',
            '거래대금', '거래대금_krx', '거래대금_nxt', '시가총액', '상장주식수',
        ]
        """
        # 데이터 핸들러에 저장된 값 리턴
        return self.dh.df
    @df.setter
    def df(self, value: pd.DataFrame):
        """
        종목 정보를 담고 있는 DataFrame을 설정합니다.
        index = ['일자, '종목코드']
        columns = [
            '종목명', '현재가', '전일가', '기준가', '전일대비', '변동률', '시가', '고가', '저가', '상한가', '하한가', 
            '거래량', '거래량_krx', '거래량_nxt',
            '거래대금', '거래대금_krx', '거래대금_nxt', '시가총액', '상장주식수',
        ]
        """
        # 데이터핸들러에 데이터 전달
        self.dh.df = value
    def by_symbol(self, symbol: str) -> pd.DataFrame:
        """
        종목코드로 종목 정보를 가져옵니다.
        """
        return self.dh.by_symbol(symbol)
    @property
    def acc_symbols(self) -> list[str]:
        """
        종목코드 리스트를 반환합니다.
        """
        return self.dh.symbols
    
    def fetch_acc(self, symbol)->pd.DataFrame:
        """
        1. 정확한 종목 정보 갱신 후 리턴한다. (add_symbol_as_acc는 update 메쏘드 호출해야 종목 정보를 업데이트한다.)
        Returns: pd.DataFrame
            index: ['일자', '종목코드']
            columns = [
                '종목명', '현재가', '전일가', '기준가', '전일대비', '변동률', '시가', '고가', '저가', '상한가', '하한가', 
                '거래량', '거래량_krx', '거래량_nxt',
                '거래대금', '거래대금_krx', '거래대금_nxt', '시가총액', '상장주식수',
        ]
        """
        
        # 잠시 쉰다. 
        now = time.time()
        elapsed = now - self.last_fetch_time
        self.last_fetch_time = now
        if elapsed < self.fetch_interval:
            time.sleep(1.0 - elapsed)
        
        # 종목 정보를 가져온다.
        stock_info_df = pd.DataFrame([fetch_acc_stock_info_from_naver_as_dict(symbol)])
        # 일자 칼럼 추가 
        stock_info_df['일자'] = pd.to_datetime('today').normalize()
        # df에 업데이트한다. 이 때 자동으로 self.acc_symbols에 등록된다.
        self.dh.upsert_df_with_similar_df(stock_info_df)
        return self.by_symbol(symbol)
    
    def _update(self):
        """
        현재 소유 중인 종목 정보에 대해서 업데이트합니다.
        """
        for symbol in self.acc_symbols:
            self.fetch_acc(symbol)


class _NDF:
    pass

class NaverDataFetcher_acc(_NDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.natsi = NaverAccTodayStockInfo()
    @property
    def acc_df(self) -> pd.DataFrame:
        """
        정확한 종목 정보를 담고 있는 DataFrame을 반환합니다.
        index = ['일자', '종목코드']
        columns = [
            '종목명', '현재가', '전일가', '기준가', '전일대비', '변동률', '시가', '고가', '저가', '상한가', '하한가', 
            '거래량', '거래량_krx', '거래량_nxt',
            '거래대금', '거래대금_krx', '거래대금_nxt', '시가총액', '상장주식수',
        ]
        """
        return self.natsi.df
    @property
    def acc_symbols(self):
        """
        종목코드 리스트를 반환합니다.
        """
        return self.natsi.acc_symbols
    
    def add_symbol_in_acc(self, symbol: str):
        """
        정확한 금일 데이터를 위해 종목을 추가합니다.
        """
        self.fetch_acc_stock_info_as_df(symbol)
    
    def fetch_acc_stock_info_as_df(self, symbol) -> pd.DataFrame:
        """
        1. 정확한 종목 정보 갱신 후 리턴한다. (add_symbol_as_acc는 update 메쏘드 호출해야 종목 정보를 업데이트한다.)
        Returns: pd.DataFrame
            index: ['일자', '종목코드']
            columns = [
                '종목명', '현재가', '전일가', '기준가', '전일대비', '변동률', '시가', '고가', '저가', '상한가', '하한가', 
                '거래량', '거래량_krx', '거래량_nxt',
                '거래대금', '거래대금_krx', '거래대금_nxt', '시가총액', '상장주식수',
        ]
        """
        res_df = self.natsi.fetch_acc(symbol=symbol)
        return res_df
    
    def _update_acc(self):
        """
        현재 소유 중인 종목 정보에 대해서 자동으로 업데이트합니다.
        """
        self.natsi._update()
        logger.info(f"Accurate stock info updated from Naver : {len(self.acc_symbols)} symbols.")

class NaverDataFetcher_non_acc_core(NaverDataFetcher_acc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sdh = SingledayDataHandler() # 금일 종목 정보를 가져오기 위해서 사용
        self.sdh.load_renect_data_from_krx() # 클래스 생성 시 한번 초기화하고 계속 사용한다. 
        self.dh_non_acc = StockDataHandler()
    
    @property
    def all_symbols(self):
        """
        모든 종목코드 리스트를 반환합니다.
        """
        return self.sdh.stock_symbols
    @property
    def non_acc_df(self) -> pd.DataFrame:
        """
        정확한 종목 정보를 제외한 DataFrame을 반환합니다.
        index = ['일자', '종목코드']
        columns = [
            '종목명', '정규장', '넥스트', 
            '전일가', '현재가', '전일대비', 
            '변동률', '변동률_nxt', '변동률_장후', 
            '기준가', '시가', '고가', '저가', 
            '종가', '종가_krx', '종가_nxt', 
            '상한가', '하한가', 
            '거래량', '거래량_krx', '거래량_nxt',
            '거래대금', '거래대금_krx', '거래대금_nxt',
        ]
        """
        return self.dh_non_acc.df
    
    def fetch_all_non_acc_stock_info(self) -> pd.DataFrame:
        """
        종목 코드 리스트를 받아서 해당 종목들의 정보를 가져옵니다. 
        가져온 정보는 자동으로 self.dh_not_acc에 저장됩니다.
        칼럼을 조정합니다. 
        넥스트레이드 거래량 및 거래대금은 0으로 설정합니다.
        Returns: pd.DataFrame
            index = ['일자', '종목코드']
            columns = [
                '종목명', '정규장', '넥스트', 
                '전일가', '현재가', '전일대비', 
                '변동률', '변동률_nxt', '변동률_장후', 
                '기준가', '시가', '고가', '저가', 
                '종가', '종가_krx', '종가_nxt', 
                '상한가', '하한가', 
                '거래량', '거래량_krx', '거래량_nxt',
                '거래대금', '거래대금_krx', '거래대금_nxt',
                ]
        """
        returning_columns = [
            '종목명', '정규장', '넥스트', 
            '전일가', '현재가', '전일대비', 
            '변동률', '변동률_nxt', '변동률_장후', 
            '기준가', '시가', '고가', '저가', 
            '종가', '종가_krx', '종가_nxt', 
            '상한가', '하한가', 
            '거래량', '거래량_krx', '거래량_nxt', # 거래량_krx와 거래량_nxt 추가 필요
            '거래대금', '거래대금_krx', '거래대금_nxt', # 거래대금_krx와 거래대금_nxt 추가 필요
            ]
        df = get_multiple_current_ohlcv_from_naver(self.all_symbols)
        # 일자는 오늘일자로 설정
        df['일자'] = pd.to_datetime('today').normalize()
        
        # 넥스트 거래량/거래대금은 0으로 설정한다. 
        df['거래량_krx'] = df['거래량']
        df['거래량_nxt'] = 0
        df['거래대금_krx'] = df['거래대금']
        df['거래대금_nxt'] = 0
        df.set_index(['일자', '종목코드'], inplace=True, drop=True)
        return self.dh_non_acc.set_data(df[returning_columns])

class NaverDataFetcher_non_acc(NaverDataFetcher_non_acc_core):
    def get_multiple_non_acc_stock_info(self, symbols:List[str]) -> pd.DataFrame:
        """
        특정 종목들에 대해서, 
        저장된 정보를 리턴하거나, fetch 후 리턴합니다. 
        fetch 시에는 모든 정보가 자동으로 저장됩니다. 
        
        Returns: pd.DataFrame
            index = ['일자', '종목코드']
            columns = [
                '종목명', '정규장', '넥스트', 
                '전일가', '현재가', '전일대비', 
                '변동률', '변동률_nxt', '변동률_장후', 
                '기준가', '시가', '고가', '저가', 
                '종가', '종가_krx', '종가_nxt', 
                '상한가', '하한가', 
                '거래량', '거래량_krx', '거래량_nxt',
                '거래대금', '거래대금_krx', '거래대금_nxt',
                ]
        """
        idx = pd.IndexSlice
        return self.get_all_non_acc_stock_info().loc[idx[:, pd.Index(symbols)], :]
    def get_all_non_acc_stock_info(self) -> pd.DataFrame:
        """
        저장된 정보를 리턴하거나, fetch 후 리턴합니다. 
        fetch 시에는 모든 정보가 자동으로 저장됩니다. 
        
        Returns: pd.DataFrame
            index = ['일자', '종목코드']
            columns = [
                '종목명', '정규장', '넥스트', 
                '전일가', '현재가', '전일대비', 
                '변동률', '변동률_nxt', '변동률_장후', 
                '기준가', '시가', '고가', '저가', 
                '종가', '종가_krx', '종가_nxt', 
                '상한가', '하한가', 
                '거래량', '거래량_krx', '거래량_nxt',
                '거래대금', '거래대금_krx', '거래대금_nxt',
                ]
        """
        if self.non_acc_df.empty:
            # 저장된 정보가 없거나, 일부 종목이 없는 경우
            self.fetch_all_non_acc_stock_info()
        return self.non_acc_df
    
    def _update_non_acc(self):
        """
        현재 소유 중인 종목 정보에 대해서 자동으로 업데이트합니다.
        """
        self.fetch_all_non_acc_stock_info()
        logger.info(f"Non-accurate stock info updated from KRX : {len(self.all_symbols)} symbols.")

class NaverDataFetcher_total(NaverDataFetcher_non_acc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dh = StockDataHandler()  # 전체 종목 정보를 관리하는 핸들러. acc + non-acc
        
    def merge_non_acc_with_acc(self):
        """
        정확한 종목 정보와 비정확한 종목 정보를 병합합니다.
        정확한 종목 정보는 NaverAccStockInfo에서 가져오고, 비정확한 종목 정보는 OnedayDataHandler에서 가져옵니다.
        """
        # 정확한 종목 정보와 비정확한 종목 정보를 병합합니다.
        merged_df = update_df_with_another_df(
            df=self.dh_non_acc.df,
            another_df=self.acc_df, 
            )
        logger.info(f"Merged non-accurate stock info with accurate stock info : common symbols={len(self.acc_symbols)}")
        return merged_df
    
    @property
    def df(self) -> pd.DataFrame:
        """
        Returns: pd.DataFrame
        index = ['일자', '종목코드']
        columns = [
            '종목명', '정규장', '넥스트', 
            '전일가', '현재가', '전일대비', 
            '변동률', '변동률_nxt', '변동률_장후', 
            '기준가', '시가', '고가', '저가', 
            '종가', '종가_krx', '종가_nxt', 
            '상한가', '하한가', 
            '거래량', '거래량_krx', '거래량_nxt',
            '거래대금', '거래대금_krx', '거래대금_nxt',
            ]
        """
        return self.merge_non_acc_with_acc()
    
class NaverDataFetcher(NaverDataFetcher_total):
    """
    네이버에서 데이터를 수집하는 Provider입니다.
    """
    def ready(self):
        """
        NaverDataFetcher를 준비합니다.
        """
        logger.info("Naver Data Fetcher is ready.")
        # 정확한 종목 정보를 가져옵니다.
        self._update()
        
    def _update(self):
        """
        현재 소유 중인 종목 정보에 대해서 자동으로 업데이트합니다.
        """
        self._update_acc()
        self._update_non_acc()
        logger.info("Naver Data Fetcher update completed.")


ndf = NaverDataFetcher()


if __name__ == '__main__':
    from mystockutil.df.format import myprint as print
    
    dh = StockDataHandler() # test용 핸들러
    ndf.ready()
    symbol = '005930'  # 삼성전자
    symbols = ['005930', '000660']  # 삼성전자, SK하이닉스
    dh.df = ndf.df
    print(dh.by_symbol("005930"))
    ndf.add_symbol_in_acc(symbol)
    dh.df = ndf.df
    print(dh.by_symbol("005930"))
    
    print('Finished')