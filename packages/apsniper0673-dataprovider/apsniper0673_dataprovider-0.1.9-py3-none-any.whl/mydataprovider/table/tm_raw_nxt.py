from typing import List, Tuple, Any 
import pandas as pd
import datetime

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(original_logger, {'prefix': 'TM_RAW_NXT'})

"""
class _RAW : raw 테이블을 관리하는 부모 클래스
- fetch_from: 서버에서 특정일 이후의 데이터를 가져와서 df에 저장
- fetch_n: 서버에서 최근 n일간의 데이터를 가져와서 df에 저장
- fetch: 서버에서 모든 데이터를 가져와서 df에 저장
- post_updated: 업데이트된 df를 서버에 저장 > 날짜별, 종목별, 또는 (날짜,종목)별로 저장
- create_empty_df: 서버에 빈 테이블을 생성 후, fetch해 온다.
- init_df: df를 초기화한다. 인덱스 설정 등
"""

# Essential Imports
from mydataprovider.table.stock_table_manager import StockTableManager
from mydataprovider.utility.crawler.nxt import fetch_daily_stock_prices_from_nxt
from mydataprovider.frame.odi.df_odi import odi

class _TM_NXT(StockTableManager):
    krx_fetch_interval = 1
    table_creating_sql = f"""
            CREATE TABLE IF NOT EXISTS `raw_nxt` (
            `일자` date NOT NULL,
            `종목코드` varchar(50) NOT NULL,
            `표준코드` text DEFAULT NULL,
            `종목명` text DEFAULT NULL,
            `마켓구분` text DEFAULT NULL,
            `종가` bigint(20) DEFAULT NULL,
            `전일대비` bigint(20) DEFAULT NULL,
            `변동률` double DEFAULT NULL,
            `시가` bigint(20) DEFAULT NULL,
            `고가` bigint(20) DEFAULT NULL,
            `저가` bigint(20) DEFAULT NULL,
            `거래량` bigint(20) DEFAULT NULL,
            `거래대금` bigint(20) DEFAULT NULL,
            `시장ID` text DEFAULT NULL,
            PRIMARY KEY (`일자`,`종목코드`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
            """
    def __init__(self) -> None:
        super().__init__()
        self.updated_dates = []
        self.updated_symbols = []
        self.updated_dates_and_symbols:List[Tuple[pd.Timestamp, str]] = []
        self.primary_keys = ['일자', '종목코드']
        self.is_today_krx_df_updated = False
        self.is_today_nxt_df_updated = False
        self._make_empty_table() # 테이블이 없을 경우, 빈 테이블을 생성한다.
        
    def _make_empty_table(self) -> pd.DataFrame:
        """
        서버에 빈 테이블을 생성한다.
        """
        self.db_with_sql.execute_query(self.table_creating_sql)
            
"""
DB의 raw_krx 테이블을 관리하는 클래스
테이블은 DB에 만들어져 있다고 가정한다.
테이블이 없는 경우, 수동으로 생성해야 한다. krx에서 하루치를 다운 받아서 post하면 된다. 
Primary key는 ['일자', '종목코드']로 설정되어 있다.
"""
class _TM_RAW_NXT(_TM_NXT):
    def __init__(self) -> None:
        super().__init__()
        self.table_name = 'raw_nxt'

    def fetch_from_web(self, date:pd.Timestamp, post_to_server=False) -> pd.DataFrame:
        """
        Returns: pd.DataFrame
            columns = ['일자', '종목코드', '표준코드', '종목명', '마켓구분', '종가', '전일대비', '변동률', 
            '시가', '고가', '저가', '거래량', '거래대금', '시장ID']
        KRX에서 주가 데이터를 가져와서 raw_nxt 테이블에 저장 후, 일간 데이터를 리턴
        """
        date = pd.to_datetime(date).normalize()
        daily_df = self.fetch_daily_stock_prices_from_web(date=date, post_to_server=post_to_server)
        return daily_df
        
class TM_RAW_NXT(_TM_RAW_NXT):
    # 오버라이딩
    def fetch_daily_stock_prices_from_web(self, date:pd.Timestamp, post_to_server:bool=True) -> pd.DataFrame:
        """
        Returns: pd.DataFrame
            columns = ['일자', '종목코드', '표준코드', '종목명', '마켓구분', '종가', '전일대비', '변동률', 
            '시가', '고가', '저가', '거래량', '거래대금', '시장ID']
        """
        date = pd.to_datetime(date).normalize()
        daily_df = fetch_daily_stock_prices_from_nxt(date)
        if odi.today_is_openday and odi.is_today_nxt_final_data_ready():
            # 오늘이 개장일이고, NXT 데이터가 최종적으로 확정된 경우
            # 서버에 업데이트
            logger.info(f"Updating raw_krx table with data for {date.strftime('%Y-%m-%d')}")            
            self.db_with_sql.post_df(self.table_name, daily_df, self.primary_keys)
        return daily_df
    
if __name__ == '__main__':
    tm_nxt = TM_RAW_NXT()
    df = tm_nxt.fetch_daily_stock_prices_from_web(datetime.date(2025, 3, 4), post_to_server=True)
    print("Finished fetching NXT stock data.")