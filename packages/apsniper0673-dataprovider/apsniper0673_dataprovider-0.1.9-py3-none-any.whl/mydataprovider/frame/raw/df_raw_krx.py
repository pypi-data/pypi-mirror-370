import pandas as pd
import datetime

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(original_logger, {'prefix': 'DF_RAW_KRX'})

"""
class DF_RAW_KRX: raw_krx 테이블을 관리 및 조회화는 클래스
df - double index: '일자', '종목코드'

raw.by_date(date)
raw.by_symbol(symbol)

---- 관리 ----
어제까지의 데이터 업데이트
금일 실시간 데이터 업데이트
오후 3시55분 이후 금일 데이터 업데이트 > 언제 finalized 되는지 확인 필요
ODI도 함께 업데이트 한다. > 해야하나? 어떤걸?

---- 조회 ----
각 종목별 데이터 조회
각 날짜별 데이터 조회
"""
from mydataprovider.frame.odi.df_odi import odi
from mydataprovider.frame.stock_dataframe import StockDataFrame
from mydataprovider.frame.raw.stock_data_handler_for_raw import StockDataHandlerKRX
from mydataprovider.table.tm_raw_krx import TM_RAW_KRX

class _DF_RAW_KRX(StockDataFrame):
    def __init__(
        self,
        feather_name: str,  # feather 파일 이름
        ):
        super().__init__(
            table_name='raw_krx',
            base_feather_name = feather_name,
            )
        self.dh:StockDataHandlerKRX # Type hinting for StockDataHandlerKRX        
        
class _DF_RAW_KRX_table(_DF_RAW_KRX):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # 기본적으로 raw_krx 테이블을 관리하는 객체
        self.default_start_date = pd.Timestamp('2011-01-01')
        self.table_manager = TM_RAW_KRX()

    def _from_web_to_raw_in_timerange(self, from_date:datetime.date, to_date:datetime.date):
        """
        timerange 내의 데이터를 업데이트
        """
        from_date = pd.to_datetime(from_date)
        to_date = pd.to_datetime(to_date)
        count = 0
        for date in pd.date_range(from_date, to_date):
            self._from_web_to_raw(date)
            count += 1
            if count % 10 == 0:
                print(f"Processing {date.strftime('%Y-%m-%d')} in from_krx_to_raw_in_timerange")

    def _from_web_to_raw(self, date:datetime.date) -> bool:
        """
        1. KRX에서 주가 데이터를 가져와서 raw 테이블에 저장합니다.
        2. sdh.df에도 업데이트하고, 서버에도 업데이트한다.
        return: 업데이트 성공 여부 > 휴일인 경우 False? True가 나을려나? 
        """
        # date에 해당하는 데이터를 KRX에서 가져와서 raw_krx 테이블에 저장
        # 리턴값으로 해당일의 데이터프레임을 받아온다. 
        date = pd.to_datetime(date)
        daily_df = self.table_manager.fetch_from_web(date=date, post_to_server=True)
        # ODI도 업데이트 > 사실 보통은 할 필요가 없기는 함.

        # 장 시작 전, 휴장일 등에 대한 처리
        if daily_df.empty:
            # 휴일 처리
            odi.add_offday(date)
            return False

        # 개장일 처리
        # 1. odi 처리 
        odi.add_onday(date)

        # 2. df 업데이트
        self.dh.add_single_daily_df(daily_df=daily_df,)
        return True
    
    def _fetch_from_server(self) -> pd.DataFrame:
        return self.table_manager.fetch_whole()
                
class DF_RAW_KRX_update(_DF_RAW_KRX_table):
    """
    StockDataFrame의 abstract method을 구현한 클래스
    - _is_updatable_today: 오늘 데이터가 업데이트 가능한지 여부를 반환합니다.
    - _update_today: 어제까지는 이미 업데이트 되어 있는 상태에서 오늘의 데이터를 업데이트합니다.
    - _update_until_yesterday: 어제까지 데이터를 업데이트합니다.
    """
    @property
    def _updatable_time(self)->pd.Timestamp:
        """데이터가 업데이트 가능한 시간(시각)을 반환합니다.
        """
        # KRX의 경우, 오후 6시 00분 이후에 데이터가 업데이트 가능 > NXT와 동일하게 설정하도록 한다. 
        # return pd.Timestamp('18:00:00')
        return pd.Timestamp('20:00:00')
        
    
class DF_RAW_KRX(DF_RAW_KRX_update):
    pass

raw_krx_recent = DF_RAW_KRX(feather_name = 'raw_krx_recent')
raw_krx_all = DF_RAW_KRX(feather_name = 'raw_krx_all')

def test():
    """
    Test function to check if the class works as expected.
    """
    raw_krx_recent.ready()
    raw_krx_recent.dh.set_as_recent_df()
    raw_krx_recent._save_to_feather()
    
    df = raw_krx_recent.dh.by_date(pd.Timestamp('2025-06-03'))
    print(df.head())
    
    raw_krx_recent._save_to_feather()
    
if __name__ == "__main__":
    raw = raw_krx_recent
    df = raw._load_from_feather()
    df = df[[col for col in df.columns if not col in df.index.names]]
    raw.dh.df = df
    raw._save_to_feather()
    print("Finished testing DF_RAW_KRX.")