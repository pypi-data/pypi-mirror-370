# public imports
import pandas as pd
from typing import List

from mystockutil.logging.logging_setup import CustomAdapter
from mystockutil.logging.logging_setup import logger as original_logger

# private imports
logger = CustomAdapter(original_logger, {'prefix': 'RDP'})

# essential imports
from mydataprovider.frame.odi.df_odi import odi
import mydataprovider.provider.rdp.flask.rdf_client as rdfc


class _RDP:
    pass

class RDP_fetch(_RDP):
    """
    rdfc의 기능만을 그대로 옮긴 클래스
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rdfc = rdfc  # rdf_client 모듈을 통해 서버와 통신
        self._cache_df:pd.DataFrame = pd.DataFrame(columns=['일자', '종목코드']).set_index(['일자', '종목코드'], drop=True)  # 캐시용 DataFrame 초기화
        self._cached_min_date: pd.Timestamp | None = None
        self._cached_max_date: pd.Timestamp | None = None
    
    def _fetch_from_to(self, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
        """
        기존에 있던 원본 메서드 (수정 없이 유지)
        """
        return self.rdfc.fetch_df(start_date=start_date, end_date=end_date)
    
    def fetch_from_to(self, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
        today = pd.Timestamp.today().normalize()

        # 캐시 초기화
        if self._cache_df.empty:
            self._cache_df = self._fetch_from_to(start_date, end_date)
            self._cached_min_date = start_date
            self._cached_max_date = end_date
            return self._cache_df.copy()
        requested_dates = pd.date_range(start_date, end_date, freq="D")
        
        # 캐시 앞쪽 확장
        if start_date < self._cached_min_date:
            temp_end_date = odi.get_prev_open_day(self._cached_min_date, 1)
            fetched_df = self._fetch_from_to(start_date, temp_end_date)
            self._cache_df = pd.concat([fetched_df, self._cache_df]).drop_duplicates().sort_index()
            self._cached_min_date = start_date
        
        # 캐시 뒤쪽 확장 (오늘 제외)
        if end_date > self._cached_max_date:
            temp_start_date = odi.get_next_open_day(self._cached_max_date, 1)
            fetched_df2 = self._fetch_from_to(temp_start_date, end_date)
            self._cache_df = pd.concat([self._cache_df, fetched_df2]).drop_duplicates().sort_index()
            self._cached_max_date = end_date
        
        # ---- 2단계: 오늘(today) 데이터는 무조건 새로 ----
        if today in requested_dates:
            df_today = self._fetch_from_to(today, today)
            mask = self._cache_df.index.get_level_values('일자') != today
            self._cache_df = pd.concat([self._cache_df[mask], df_today]).drop_duplicates().sort_index()
            self._cached_max_date = today
        
        # ---- 3단계: 요청 범위만 반환 ----
        result = self._cache_df[
            self._cache_df.index.get_level_values('일자').isin(requested_dates)
        ].copy()
        return result
    
    def add_acc(self, symbols: List[str]) -> List[str]:
        """
        정확한 종목 코드 리스트에 종목들을 추가합니다.
        새로 추가된 종목 코드리스트를 반환합니다.
        """
        return self.rdfc.add_acc(symbols=symbols)


class RealtimeDFProvider(RDP_fetch):
    """
    RealtimeDFProvider
    -------------------
    실시간 및 과거 주식 데이터를 RDF 서버를 통해 가져오는 클래스입니다.
    `RDP_core`와 `RDP_fetch`의 기능을 상속하여,
    특정 기간, 특정 날짜 기준으로 다양한 방식으로 데이터를 가져올 수 있습니다.

    Methods
    -------
    fetch_from_to(start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame
        start_date부터 end_date까지의 주식 데이터를 DataFrame으로 가져옵니다.
    
    add_acc(symbols: List[str]) -> List[str]
        정확한 종목 코드 리스트(`acc`)에 새 종목들을 추가하고, 새로 추가된 종목 코드를 반환합니다.
    """
    pass


rdp = RealtimeDFProvider() # 기본 인스턴스 생성


if __name__ == '__main__':  
    from mydataprovider.test_api import myprint as print, dh
    symbols = ['298380']
    
    df = rdp.fetch_from_to(start_date=pd.Timestamp('2025-08-08'), end_date=pd.Timestamp('2025-08-08'))
    print("Finished")