# public imports
import pandas as pd
from typing import List, Tuple

# private imports
from mystockutil.logging.logging_setup import CustomAdapter
from mystockutil.logging.logging_setup import logger as original_logger

logger = CustomAdapter(original_logger, {'prefix': 'SDP'})

"""
Stock Data Provider
1. 데이터 조회를 위해서 웹과 api의 두가지 방식을 가진다.
웹의 경우 naver를 통해서 데이터를 조회하고, # self.ndp로 접근
api의 경우는 한국투자증권과 연계하고자 한다 > 미구현
web와 api의 경우, 공통적인 기능들에 대해서는 최대한 동일한 인터페이스를 제공하도록 한다. 
dataframe의 사용과 관련하여 ppd, rdf를 사용한다.
2. df와 관련해서는 ppd와 rdf를 가지고 있으며,
전체 df를 사용하기 위해서는 초기화를 하여야 하고, 그렇지 않은 경우에는 바로 사용한다.
"""

WRITING_DEPTH = 2

# essential imports
from mydataprovider.frame.odi.df_odi import odi
from mydatahandler.handler.stock_data_handler import StockDataHandler
from mydataprovider.provider.web.web_data_provider import WebDataProvider, wdp
from mydataprovider.provider.rdp.realtime_dataframe_provider import RealtimeDFProvider, rdp


class _SDP:
    def __init__(self):
        pass


class SDP_wdp_core(_SDP):
    def __init__(
        self,
        wdp:WebDataProvider,
        ):
        self.wdp = wdp  # WebDataProvider 인스턴스
    
    def get_stock_names(self, symbols:list) -> list:
        return self.wdp.get_stock_names(symbols)
    def get_stock_symbols(self, names:list) -> list:
        return self.wdp.get_stock_symbols(names)
    
    @property
    def acc_symbols(self) -> List[str]:
        """
        정확한 종목 코드 리스트를 반환합니다.
        """
        return self.wdp.acc_symbols
    
    def _add_acc_through_wdp(self, symbols: List[str]) -> Tuple[List[str], List[str]]:
        """
        symbols를 정확한 종목에 추가합니다.
        """
        return self.wdp.add_acc(symbols)
    
    def fetch_acc(self, symbols: List[str]) -> pd.DataFrame:
        """
        symbols에 해당하는 종목들의 정보를 가져옵니다.
        이 종목들은 자동으로 정확한 종목 코드 리스트에 추가됩니다.
        
        Returns: DataFrame
            Index: '일자', '종목코드'
            columns: 
                [
                '종목명', '현재가', '전일가', '기준가', '전일대비', '변동률', '시가', '고가', '저가', '상한가', '하한가', 
                '거래량', '거래량_krx', '거래량_nxt',
                '거래대금', '거래대금_krx', '거래대금_nxt', '시가총액', '상장주식수',
                ]
        """
        return self.wdp.fetch_acc(symbols)
    
    def fetch_some(self, symbols:list) -> pd.DataFrame:
        """
        넥스트레이드 값은 고려하지 않는 결과값 리턴
        
        Returns: pd.DataFrame
            Index: ['일자', '종목코드']
            columns =[
                '종목명', '정규장', '넥스트', '전일가', '현재가', '전일대비', '변동률',
                '변동률_nxt', '변동률_장후', '기준가', '시가', '고가', '저가', '종가', '종가_krx', '종가_nxt',
                '상한가', '하한가', '거래량', '거래량_krx', '거래량_nxt', '거래대금', '거래대금_krx',
                '거래대금_nxt'
                ] # 넥스트레이드 값은 0 일 수 있음
        """
        return self.wdp.fetch_some(symbols)
    
    def fetch_all_today(self) -> pd.DataFrame:
        """
        금일 모든 종목의 정보를 DataFrame으로 반환합니다.
        Returns: pd.DataFrame
            Index: ['일자', '종목코드']
            columns =[
                '종목명', '정규장', '넥스트', '전일가', '현재가', '전일대비', '변동률',
                '변동률_nxt', '변동률_장후', '기준가', '시가', '고가', '저가', '종가', '종가_krx', '종가_nxt',
                '상한가', '하한가', '거래량', '거래량_krx', '거래량_nxt', '거래대금', '거래대금_krx',
                '거래대금_nxt'
                ]
        """
        return self.wdp.fetch_all()

class SDP_wdp(SDP_wdp_core):
    def get_stock_name(self, symbol:str) -> str:
        return self.get_stock_names([symbol])[0]
    def get_stock_symbol(self, name:str) -> str:
        return self.get_stock_symbols([name])[0]
    
    def fetch_single_acc(self, symbol: str) -> pd.DataFrame:
        """
        symbol에 해당하는 종목의 정보를 DataFrame으로 반환합니다.
        
        Returns: pd.DataFrame
            Index: ['일자', '종목코드']
            columns: 
                [
                '종목명', '현재가', '전일가', '기준가', '전일대비', '변동률', '시가', '고가', '저가', '상한가', '하한가', 
                '거래량', '거래량_krx', '거래량_nxt',
                '거래대금', '거래대금_krx', '거래대금_nxt', '시가총액', '상장주식수',
                ]
        """
        return self.fetch_acc([symbol])
    
    def fetch_current_price(self, symbol:str) -> int:
        res = self.fetch_single_acc(symbol)['현재가'].iloc[0]
        return res


class SDP_rdp_mode(SDP_wdp):
    def __init__(self, mode:str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mode = mode if mode in ['brief', 'detail'] else 'detail'
        self._filter = False # rdp를 이용한 fetch에서만 적용되는 필터
        self._fdh = StockDataHandler()
    
    def set_filter(self, onoff:bool=True):
        self._filter = onoff
    def set_as_brief(self):
        """
        mode를 'brief'로 설정한다.
        """
        self._mode = 'brief'
    def set_as_detail(self):
        """
        mode를 'detail'로 설정한다.
        """
        self._mode = 'detail'
    
    @property
    def _in_brief_columns(self) -> List[str]:
        """
        간략모드의 DataFrame 컬럼을 반환합니다.
        """
        columns = [
            '종목명', '마켓구분', 
            '변동률', '시가총액', '상장주식수', 
            '시가', '고가', '저가', '종가', '기준가', '전일대비', 
            '거래량', '거래대금',
            '거래량양수', '연속거래일수', 
            '종가상한가여부', '종가하한가여부', '시가상한가여부', '시가하한가여부', '종가상하한가', '시가상하한가' 
            ]
        return columns    
    @property
    def _in_detail_columns(self) -> List[str]:
        """
        상세모드의 DataFrame 컬럼을 반환합니다.
        """
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
        return columns
    
    def _df_as_mode(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        df를 mode에 맞게 변환합니다.
        mode가 'brief'인 경우, self._in_brief_columns에 해당하는 컬럼만 남깁니다.
        mode가 'detail'인 경우, self._in_detail_columns에 해당하는 컬럼만 남깁니다.
        """
        if self._filter: 
            df = self._fdh.remove_unnecessary_symbols(df)  # 불필요한 종목 코드 제거
        if self._mode == 'brief':
            return df[self._in_brief_columns]
        elif self._mode == 'detail':
            return df[self._in_detail_columns]
        else:
            raise ValueError(f"Unknown mode: {self._mode}")

# SDP_rdp 클래스에서 사용하기 위한 데코레이터
def apply_mode(func):
    """
    DataFrame을 반환하는 메서드에 붙여서,
    self._df_as_mode()로 자동 변환되도록 하는 데코레이터.
    """
    def wrapper(self, *args, **kwargs):
        df = func(self, *args, **kwargs)
        return self._df_as_mode(df)
    return wrapper
class SDP_rdp_core(SDP_rdp_mode):
    def __init__(
        self,
        rdp:RealtimeDFProvider = rdp,
        *args, **kwargs
        ):
        super().__init__(*args, **kwargs)
        self.rdp = rdp  # RealtimeDFProvider 인스턴스
    
    @apply_mode
    def _fetch_from_to(self, start_date:pd.Timestamp, end_date:pd.Timestamp) -> pd.DataFrame:
        """
        start_date부터 end_date까지의 주식데이터를 DataFrame으로 가져온다.
        """
        return self.rdp.fetch_from_to(start_date=start_date, end_date=end_date)
    
    def _add_acc_through_rdp(self, symbols: List[str]) -> List[str]:
        """
        정확한 종목 코드 리스트에 종목들을 추가합니다.
        새로 추가된 종목 코드리스트를 반환합니다.
        """
        return self.rdp.add_acc(symbols=symbols)


class SDP_rdp_fetch(SDP_rdp_core):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.writing_depth = WRITING_DEPTH
    
    def fetch_df_from_to(self, start_date:pd.Timestamp, end_date:pd.Timestamp) -> pd.DataFrame:
        """
        start_date부터 end_date까지의 주식데이터를 DataFrame으로 가져온다.
        """
        return self._fetch_from_to(start_date=start_date, end_date=end_date)
    
    def fetch_df_from(self, start_date:pd.Timestamp)->pd.DataFrame:
        """
        start_date부터 end_date까지의 주식데이터를 DataFrame으로 가져온다."""
        return self._fetch_from_to(start_date=start_date, end_date=pd.Timestamp('today').normalize())
    
    def fetch_df_n_from(self, start_date:pd.Timestamp, n:int)->pd.DataFrame:
        """
        start_date부터 n일 전까지의 주식데이터를 DataFrame으로 가져온다.
        n은 양수여야 하며, n=1이면 start_date의 데이터만 가져온다.
        """
        if n < 1:
            raise ValueError("n must be a positive integer.")
        end_date = odi.get_prev_open_day(start_date, n)
        return self._fetch_from_to(start_date=start_date, end_date=end_date)
    
    def fetch_df_from_with_buffer(self, start_date:pd.Timestamp) -> pd.DataFrame:
        """
        writing_depth를 고려하여 start_date를 조정 후,
        start_date부터 금일까지의 주식데이터를 DataFrame으로 가져온다.
        """
        start_date = pd.to_datetime(start_date).normalize()
        new_start_date = odi.get_prev_open_day(start_date, self.writing_depth)
        return self.fetch_df_from(start_date=new_start_date)
    
    def fetch_df_n_to(self, to_date:pd.Timestamp, n:int) -> pd.DataFrame:
        """
        to_date로부터 to_date 포함 이전 n개의 주식데이터를 DataFrame으로 가져온다.
        """
        if n < 1:
            raise ValueError("n must be a positive integer.")
        if odi.today_is_openday:
            n -= 1
        start_date = odi.get_prev_open_day(to_date, n)
        return self._fetch_from_to(start_date=start_date, end_date=to_date)
    
    def fetch_df_n_recent(self, n:int) -> pd.DataFrame:
        """
        최근 n일의 주식데이터를 DataFrame으로 가져온다.
        """
        return self.fetch_df_n_to(to_date=pd.Timestamp('today').normalize(), n=n)
    
    def fetch_df_today(self) -> pd.DataFrame:
        """
        금일 주식데이터를 DataFrame으로 가져온다.
        """
        return self.fetch_df_from(pd.to_datetime('today').normalize())


class SDP_combine(SDP_rdp_fetch):
    def add_acc(self, symbols: List[str]) -> Tuple[List[str], List[str]]:
        """
        symbols를 정확한 종목 코드 리스트에 종목을 추가합니다. 현재 wdp를 이용함. 
        """
        new_symbols, total_symbols = self._add_acc_through_wdp(symbols)
        if not new_symbols:
            logger.info("No new symbols to add to acc.")
            return [], total_symbols
        logger.info(f"Added new symbols to acc. \nnew:{len(new_symbols)}\ntotal:{len(total_symbols)}")
        return new_symbols, total_symbols
    
    def add_single_acc(self, symbol: str) -> Tuple[List[str], List[str]]:
        """
        symbol 단일 종목을 정확한 종목에 추가합니다.
        """
        return self.add_acc([symbol])


class SDP_over_700(SDP_combine):
    """
    krx거래대금이 기준거래대금 이상 종목에 대해서 add_acc를 수행합니다.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.over_symbols = []
        self.threshold_trading_value = 7e10  # 700억
    
    # 속도에 오버로드가 걸리는 것 같음. 
    def set_acc_for_over_threshold(self) -> Tuple[List[str], List[str]]:
        """
        krx거래대금이 기준거래대금 이상 종목에 대해서 정확한 종목 코드 리스트에 종목을 추가합니다.
        Returns: Tuple[List[str], List[str]]:
            - 새로 추가된 종목 코드 리스트
            - 전체 종목 코드 리스트
        """
        df_today = self.fetch_df_today()
        over_symbols = df_today[df_today['거래대금_krx'] >= self.threshold_trading_value].get_level_values('종목코드').unique().tolist()
        new_symbols = [symbol for symbol in over_symbols if symbol not in self.over_symbols]
        if new_symbols:
            self.over_symbols.extend(new_symbols)
            new_symbols, total_symbols = self.add_acc(new_symbols)
        else:
            logger.info("No new symbols to add to acc for over threshold.")
            new_symbols, total_symbols = [], self.over_symbols
        self.over_symbols = total_symbols  # 전체 정밀 종목 코드 리스트 업데이트
        return new_symbols, total_symbols

class StockDataProvider(SDP_over_700):
    """
    """
    def __init__(
        self,
        wdp:WebDataProvider = wdp,
        rdp:RealtimeDFProvider = rdp,
        mode:str = 'detail',
        ):
        super().__init__(
            wdp=wdp,
            rdp=rdp,
            mode=mode
        )
    
    def ready(self):
        """
        데이터 프로바이더를 초기화합니다. 
        """
        # wdp, rdp는 ready 메쏘드가 필요하지 않고 바로 이용 가능. 
        # ready는 서버측에서 사용하는 메쏘드임. 
        self.set_filter(True)
        self.set_as_detail()
    
sdp = StockDataProvider()

if __name__ == "__main__":
    # Test the StockDataProvider
    from mydataprovider.test_api import myprint as print, dh
    
    sdp.ready()
    dh.df = sdp.fetch_df_n_recent(1)
    
    # sdp.set_filter(True)  # 필터 활성화
    # df = sdp.fetch_df_n_recent(n=1)  # 최근 3일의 데이터 가져오기
    # df.to_excel('today.xlsx', index=False)  # 엑셀로 저장
    # print(len(df))
    # symbols = ['062040']  
    # dh.df = sdp.fetch_df_n_recent(n=3)  # 최근 3일의 데이터 가져오기
    # print(dh.by_symbols(symbols))  # 특정 종목들의 데이터 출력
    # sdp.add_acc(symbols)  # 종목코드 추가
    # dh.df = sdp.fetch_df_n_recent(n=3)  # 최근 3일의 데이터 가져오기
    # print(dh.by_symbols(symbols))  # 특정 종목들의 데이터 출력
    # new_symbols, total_symbols = sdp.set_acc_for_over_threshold()  # 기준 거래대금 이상 종목에 대해 정확한 종목 코드 리스트에 추가
    # print(f"New symbols added: {new_symbols}")
    # symbols = total_symbols  # 전체 정밀 종목 코드 리스트로 업데이트
    # dh.df = sdp.fetch_df_n_recent(n=3)  # 최근 3일의 데이터 가져오기
    # print(dh.by_symbols(symbols))  # 특정 종목들의 데이터 출력
    
    print("Finished")