import pandas as pd

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(logger=original_logger, extra={'prefix': 'DF_RAW'})

"""
raw: raw_krx와 raw_nxt의 df를 통합하여 관리하는 클래스
"""
from mydataprovider.frame.odi.df_odi import odi
from mydataprovider.frame.raw.df_raw_krx import DF_RAW_KRX, raw_krx_all, raw_krx_recent
from mydataprovider.frame.raw.df_raw_nxt import DF_RAW_NXT, raw_nxt_all, raw_nxt_recent
from mydataprovider.frame.raw.merge_raw import merge_raw_dfs
from mydatahandler.handler.stock_data_handler import StockDataHandler


class _DF_RAW:
    def __init__(
        self,
        raw_krx:DF_RAW_KRX,
        raw_nxt:DF_RAW_NXT,
        ):
        
        self.dh = StockDataHandler()
        self.raw_krx = raw_krx
        self.raw_nxt = raw_nxt

class DF_RAW_merge(_DF_RAW):
    def _merge_dfs(self) -> None:
        """
        raw_krx와 raw_nxt의 df를 병합하여 반환
        """
        self.dh.set_data(df=merge_raw_dfs(raw_krx=self.raw_krx.dh.df, raw_nxt=self.raw_nxt.dh.df))

class DF_RAW_today(DF_RAW_merge):
    """
    금일자의 데이터와 관련한 DF_RAW 클래스
    다른 클래스에서 주로 사용함. 
    """
    def fetch_recent_df(self) -> pd.DataFrame:
        """
        최근 개장일의 raw 데이터를 web에서 가져옵니다. 
        temporary, realtime, final 모두 가능합니다. 
        Returns: pd.DataFrame
            ['일자', '종목코드', '표준코드', '종목명', '마켓구분', '관리구분', '종가', '변동코드', '전일대비',
            '변동률', '시가', '고가', '저가', '거래량', '거래대금', '시가총액', '상장주식수', '시장ID', '기준가',
            '종가_nxt', '시가_nxt', '고가_nxt', '저가_nxt', '거래량_nxt', '거래대금_nxt',
            '거래량_krx', '거래대금_krx']
        """
        merged_df = self.fetch_merged_df_by_date(odi.recent_open_day)
        return merged_df
    def fetch_merged_df_by_date(self, date:pd.Timestamp=None) -> pd.DataFrame:
        """
        특정 일자의 raw 데이터를 web에서 가져옵니다. 
        """
        date = pd.Timestamp.now().normalize() if date is None else pd.to_datetime(date).normalize()
        df_krx = self.raw_krx.table_manager.fetch_from_web(date)
        df_nxt = self.raw_nxt.table_manager.fetch_from_web(date)
        df_merged = merge_raw_dfs(raw_krx=df_krx, raw_nxt=df_nxt)
        return df_merged

class DF_RAW(DF_RAW_today):
    """
    KRX와 NXT의 raw 데이터를 통합하여 관리하는 클래스. 
    이 클래스는 KRX와 NXT의 raw 데이터를 각각 DF_RAW_KRX와 DF_RAW_NXT로부터 가져와서 병합합니다.
    .ready() 메서드를 호출하여 데이터를 준비하고 병합합니다.
    Params:
        raw_krx (DF_RAW_KRX): KRX의 raw 데이터 프레임
        raw_nxt (DF_RAW_NXT): NXT의 raw 데이터 프레임
    """
    def ready(self):
        """raw_krx와 raw_nxt의 금일날짜까지 업데이트된 데이터를 준비하고 병합합니다.
        """
        # KRX와 NXT의 raw 데이터를 준비합니다.
        self.raw_krx.ready()
        self.raw_nxt.ready()
        self._merge_dfs()
    
    @property
    def df(self) -> pd.DataFrame:
        """
        index: ['일자', '종목코드']
        
        columns:
            ['표준코드', '종목명', '마켓구분', '관리구분', '종가', '변동코드', '전일대비',
            '변동률', '시가', '고가', '저가', '거래량', '거래대금', '시가총액', '상장주식수', '시장ID', '기준가',
            '종가_nxt', '시가_nxt', '고가_nxt', '저가_nxt', '거래량_nxt', '거래대금_nxt',
            '거래량_krx', '거래대금_krx']
        """
        if self.dh.df.empty:
            raise ValueError("No data available. Please call .ready() first.")
        return self.dh.df

class DF_RAW_Recent(DF_RAW):
    """
    DF_RAW_Recent 클래스 > df_recent로 하나의 인스턴스로 사용.
    """
    def __init__(self):
        super().__init__(raw_krx=raw_krx_recent, raw_nxt=raw_nxt_recent)
    
    def ready(self):
        """
        최근 raw 데이터를 준비합니다.
        준비 후 최근 데이터만 유지합니다.
        """
        super().ready()
        # 최근 데이터만 유지
        self.raw_krx.dh.set_as_recent_df()
        self.raw_nxt.dh.set_as_recent_df()
        # feather 파일에도 저장
        self.raw_krx._save_to_feather()
        self.raw_nxt._save_to_feather()

class DF_RAW_All(DF_RAW):
    """
    DF_RAW_All 클래스 > df_all로 하나의 인스턴스로 사용.
    """
    def __init__(self):
        super().__init__(raw_krx=raw_krx_all, raw_nxt=raw_nxt_all)

raw_recent = DF_RAW_Recent()
raw_all = DF_RAW_All()

def test():
    # 테스트용 코드
    raw_recent.ready()
    raw_all.ready()
    print("Raw data is ready.")
    print(raw_recent.dh.df.head())
    print(raw_recent.dh.df.tail())
    print(raw_recent.dh.df.shape)
    print(raw_recent.dh.df.columns)
    print(raw_recent.dh.df.index.names)
        
if __name__ == "__main__":
    # raw_all.ready()
    # df = raw_all.dh.df_after("2025-06-02")
    raw_recent.ready()
    df = raw_recent.dh.df_after("2025-06-02")
    print(df.head())
    
    print("Finished updating raw data.")