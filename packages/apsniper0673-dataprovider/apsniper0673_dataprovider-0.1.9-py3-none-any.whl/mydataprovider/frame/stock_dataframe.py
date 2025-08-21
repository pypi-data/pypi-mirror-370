import pandas as pd

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(original_logger, {'prefix': 'StockDataFrame'})

"""
RAW, DDF, RDF의 상위 클래스 
"""
from mydataprovider.frame.odi.df_odi import odi
from mydatahandler.handler.stock_data_handler import StockDataHandler
from mydataprovider.frame.feather.feather_manager import FeatherManager

class _StockDataFrame:
    def __init__(
        self,
        table_name: str,
        base_feather_name: str,
        ):
        self.table_name = table_name
        self.primary_keys = ['일자', '종목코드']
        self.date_col_name = '일자'
        self.symbol_col_name = '종목코드'
        self.default_start_date = pd.Timestamp('2011-01-01')  # 기본 시작 날짜 > 기본시작 날짜가 다른 경우도 있음. 
        self.feather_manager = FeatherManager(base_feather_name=base_feather_name) # feather 파일을 관리하는 객체
        self.dh = StockDataHandler() # df를 관리하는 객체


class StockDataFrame_feather(_StockDataFrame):
    def _load_from_feather(self) -> pd.DataFrame:
        """
        feather 파일에서 데이터를 로드하고, 필요한 경우 업데이트합니다."""
        # feather 파일에서 데이터를 로드하여 sdh에 설정
        # feather 파일이 없는 경우 예외를 발생시킴
        df=self.feather_manager.load_from_feather()
        df = self._convert_index_to_timestamp(df)  # 인덱스를 타임스탬프로 변환
        return df
    def _convert_index_to_timestamp(self, df:pd.DataFrame):
        df = df.copy()
        df.index = pd.MultiIndex.from_arrays([
            pd.to_datetime(df.index.get_level_values('일자')),
            df.index.get_level_values('종목코드')
            ], names=['일자', '종목코드'])
        return df
    def _save_to_feather(self):
        """Feather 파일로 데이터를 저장합니다."""
        self.feather_manager.save_to_feather(df=self.dh.df)
    @property
    def _is_updatable_until_yesterday(self):
        """금일 제외하고 데이터가 업데이트 가능한지(어제까지) 여부를 반환합니다."""
        return not (self.dh.last_date == odi.recent_open_day_except_today)
    
class StockDataFrame_abstract(StockDataFrame_feather):
    """
    
    Abstrace methods:
    - _updatable_time(self)->pd.Timestamp: 데이터가 업데이트가 가능한 시간을 반환합니다.
    - _update_today: 어제까지는 이미 업데이트 되어 있는 상태에서 오늘의 데이터를 업데이트합니다.
    - _update_until_yesterday: 어제까지 데이터를 업데이트합니다.
    """
    def update_until_today(self) -> None:
        """오늘까지 데이터를 업데이트합니다."""
        if self._is_updatable_until_yesterday:
            logger.info(f"Updating {self.table_name} data until yesterday...")
            self._update_until_yesterday()  # 어제까지 업데이트
        if self._is_updatable_today:
            # 오늘 데이터가 업데이트 가능한 경우
            logger.info(f"Updating {self.table_name} data for today...")
            self._update_today()
        self.feather_manager.delete_old_feathers(keep=2)  # 최근 2개 feather 파일만 보존
            
    @property
    def _is_updatable_today(self):
        """오늘 데이터가 업데이트 가능한지 여부를 반환합니다.
        만일 오늘이 휴장일 경우에는 False를 반환합니다.
        """
        if odi.today_is_openday:
            return pd.Timestamp.now() >= self._updatable_time
        else:
            return False  # 휴장일에는 업데이트 불가
    @property
    def _updatable_time(self)->pd.Timestamp:
        """데이터가 업데이트 가능한 시간(시각)을 반환합니다.
        """
        pass
    
    def _update_today(self):
        """어제까지는 이미 업데이트 되어 있는 상태에서 오늘의 데이터를 업데이트합니다. """
        pass
    def _update_until_yesterday(self):
        """어제까지 데이터를 업데이트합니다."""
        pass
    def _fetch_from_server(self) -> pd.DataFrame:
        """sql을 실행하여 df을 가져온다."""
        pass

class StockDataFrame_common(StockDataFrame_abstract):
    def _update_today(self):
        """
        어제까지는 이미 업데이트 되어 있는 상태에서 오늘의 데이터를 업데이트합니다.
        feather 파일에 저장하기 때문에 오늘자 데이터가 확정된 경우에만 호출 됩니다. 
        """
        if self.dh.last_date == odi.today:
            # 이미 오늘 데이터가 업데이트 되어 있는 경우
            logger.info(f"Today's {self.table_name} price data is already updated.")
            return
        logger.info(f"Updating today's {self.table_name} price data...")
        self._from_web_to_raw(date=pd.Timestamp.today().normalize())
        logger.info("Today's price data has been updated.")
        self._save_to_feather()

    def _update_until_yesterday(self):
        """어제까지 데이터를 업데이트합니다."""
        start_date:pd.Timestamp = odi.get_next_open_day(self.dh.last_date)
        end_date = odi.prev_open_day
        if start_date > end_date:
            logger.info(f"No data to update from {start_date} to {end_date}.")
            return
        logger.info(f"Updating {self.table_name} price data from {start_date} to {end_date}...")
        self._from_web_to_raw_in_timerange(start_date, end_date)
        logger.info(f"Price data has been updated until {end_date}.")
        self._save_to_feather()

    def _from_web_to_raw(self, date: pd.Timestamp) -> bool:
        """ 지정된 날짜에 해당하는 데이터를 웹에서 가져와서 raw 테이블에 저장합니다.
        """
        pass
    def _from_web_to_raw_in_timerange(self, start_date: pd.Timestamp, end_date: pd.Timestamp) -> None:
        """
        지정된 날짜 범위에 해당하는 데이터를 웹에서 가져와서 raw 테이블에 저장합니다.
        """
        pass

class StockDataFrame(StockDataFrame_common):
    def __init__(
        self,
        table_name: str,
        base_feather_name: str,
        ):
        super().__init__(
            table_name=table_name, 
            base_feather_name=base_feather_name,
            )
    
    def ready(self):
        """
        데이터프레임을 준비합니다.
        feather 파일이 있는 경우 해당 파일에서 데이터를 로드하고,
        feather 파일이 없는 경우 서버에서 데이터를 가져옵니다.
        그 후, 금일날짜까지 데이터를 업데이트합니다.
        """
        # RAW_KRX와 RAW_NXT에서 공통적으로 사용
        try:
            logger.info(f"Preparing {self.table_name} data from feather file...")
            self.dh.df=self._load_from_feather()  # feather에서 데이터를 가져와서 핸들러에 설정
        except FileNotFoundError:
            logger.warning(f"Feather file for {self.table_name} not found. Fetching data from server...")
            self._when_feather_not_found()
        logger.info(f"{self.table_name} data is ready.")
        self.update_until_today()  # 오늘까지 업데이트
    
    def _when_feather_not_found(self):
        """feather 파일이 없는 경우 서버에서 데이터를 준비합니다.
        PPD에서는 사용하지 않고 오버라이드 한다. """
        self._ready_from_server()
        
    # feather 파일이 없는 경우 서버에서 데이터를 준비합니다.
    def _ready_from_server(self):
        """
        sql을 실행하여 df을 가져온다.
        """
        df = self._fetch_from_server()
        self.dh.set_data(df=df)        