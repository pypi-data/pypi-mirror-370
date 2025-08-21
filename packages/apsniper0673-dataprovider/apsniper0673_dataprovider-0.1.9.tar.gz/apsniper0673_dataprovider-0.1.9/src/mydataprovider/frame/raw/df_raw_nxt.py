import pandas as pd
import datetime

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(original_logger, {'prefix': 'DF_RAW_NXT'})


"""
class DF_RAW_NXT: raw_krx 테이블을 관리 및 조회화는 클래스
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
from mydataprovider.frame.raw.stock_data_handler_for_raw import StockDataHandlerNXT
from mydataprovider.table.tm_raw_nxt import TM_RAW_NXT

class _DF_RAW_NXT(StockDataFrame):
    def __init__(
        self,
        feather_name: str,  # feather 파일 이름
        ):
        super().__init__(
            table_name='raw_nxt',
            base_feather_name = feather_name,
            )
        self.dh:StockDataHandlerNXT # Type hinting for StockDataHandlerNXT
        
class _DF_RAW_NXT_table(_DF_RAW_NXT):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # 기본적으로 raw_nxt 테이블을 관리하는 객체
        self.default_start_date = pd.Timestamp('2025-03-04')
        self.table_manager = TM_RAW_NXT()

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
                print(f"Processing {date.strftime('%Y-%m-%d')} in from_nxt_to_raw_in_timerange")

    def _from_web_to_raw(self, date:datetime.date) -> bool:
        """
        1. NXT에서 주가 데이터를 가져와서 raw_nxt 테이블에 저장합니다.
        2. sdh.df에도 업데이트하고, 서버에도 업데이트한다.
        return: 업데이트 성공 여부 > 휴일인 경우 False? True가 나을려나? 
        """
        # date에 해당하는 데이터를 NXT에서 가져와서 raw_nxt 테이블에 저장
        # 리턴값으로 해당일의 데이터프레임을 받아온다. 
        daily_df = self.table_manager.fetch_from_web(date=date, post_to_server=True)
        # ODI 업데이트는 진행하지 않는다(KRX에서 진행됨)
        if daily_df.empty:
            # 휴일 처리
            return False
        # df 업데이트
        self.dh.add_single_daily_df(daily_df=daily_df,)
        return True

    def _fetch_from_server(self) -> pd.DataFrame:
        return self.table_manager.fetch_whole()


# RAW_KRX와 RAW_NXT는 코드가 거의 동일하다.
class DF_RAW_NXT_update(_DF_RAW_NXT_table):
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
        # NXT의 경우, 오후 8시 00분 이후에 데이터가 업데이트 가능
        return pd.Timestamp('20:00:00')
        
class DF_RAW_NXT(DF_RAW_NXT_update):
    """
    """
    def make_new_feather(self):
        """
        web에서 모든 데이터를 가져와서 
        새로운 feather 파일을 생성합니다.
        넥스트레이드 최초 시작일: 25-03-04
        """
        self.default_start_date
        # 이전 개장일까지 df를 만들어옴.
        logger.info("Creating new feather file with all data from NXT...")
        self._from_web_to_raw_in_timerange(from_date=self.default_start_date, to_date=odi.prev_open_day)
        self._save_to_feather()
        logger.info("New feather file created successfully.")
        self.update_until_today()

raw_nxt_recent = DF_RAW_NXT(feather_name = "raw_nxt_recent")
raw_nxt_all = DF_RAW_NXT(feather_name = "raw_nxt_all")

def test_make_new_feather():
    """
    Test function to check if the class works as expected.
    """
    raw_nxt_recent.make_new_feather()
    print("Test completed successfully.")

def test_ready_from_server():
    raw_nxt_recent._when_feather_not_found()
    print(raw_nxt_recent.dh.df.tail())
    
def test():
    raw_nxt_recent.ready()
    print(raw_nxt_recent.dh.df.tail())

if __name__ == "__main__":
    raw = raw_nxt_all
    df = raw._load_from_feather()
    df = df[[col for col in df.columns if not col in df.index.names]]
    raw.dh.df = df
    raw._save_to_feather()
    
    print("Finished.")