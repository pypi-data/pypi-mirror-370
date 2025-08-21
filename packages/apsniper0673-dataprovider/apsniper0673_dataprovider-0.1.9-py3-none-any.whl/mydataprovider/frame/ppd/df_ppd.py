# Public Library Imports
import pandas as pd
# Private Library Imports
from mystockutil.logging.logging_setup import CustomAdapter
from mystockutil.logging.logging_setup import logger as original_logger

logger = CustomAdapter(original_logger, {'prefix': 'PPD'})

"""
Post-Processing DataFrame (PPD) for MyStockDataProvider
df_raw를 사용하여 원본 데이터를 받는다. 
수정주가와 연속거래일수, 상하한가 정보를 포함한 DataFrame을 생성한다.
"""

from mydataprovider.frame.odi.df_odi import odi
from mydataprovider.frame.ppd.convert_to_ppd_df import (convert_as_core_ppd_df,
                                                        convert_as_ppd_df)
from mydataprovider.frame.ppd.ppdps.ppdp_custom import custom_processors
from mydataprovider.frame.raw.df_raw import DF_RAW, raw_all, raw_recent
# Essential imports
from mydataprovider.frame.stock_dataframe import StockDataFrame
from mydatahandler.handler.stock_data_handler import StockDataHandler


class _DF_PPD(StockDataFrame):
    def __init__(self, base_feather_name: str):
        super().__init__(
            table_name='ppd', # 실레로 쓰이지는 않는다.
            base_feather_name=base_feather_name,
            )
        self.ppdps = [p() for p in custom_processors]

    def _change_data_type_of_df(self, df: pd.DataFrame) -> pd.DataFrame:
        #df의 type을 변경
        dtype_mapping = {}
        for p in self.ppdps:
            dtype_mapping = dtype_mapping | p.dtype_mapping
        
        # DataFrame에 존재하는 열만 필터링하여 astype() 적용
        existing_columns = {col: dtype for col, dtype in dtype_mapping.items() if col in df.columns}

        # astype() 적용
        logger.info(f"Changing data type of df...")
        return df.astype(existing_columns)
        
class DF_PPD_calculate(_DF_PPD):
    def calculate_whole(self, df:pd.DataFrame) -> pd.DataFrame:
        """전체 df에 대해서 PPD를 계산하는 메소드"""
        # 개별 PPDP를 이용하여 전체 PPD를 계산합니다.
        df_processed = df.copy()
        for p in self.ppdps:
            logger.info(f"Processing as new df by {p.__class__.__name__}...")
            df_processed = p.process_new_df(df_processed)
        # PPD 계산이 완료된 df를 반환합니다.
        return self._change_data_type_of_df(df_processed)

    def calculate_recent(
        self,
        existing_df: pd.DataFrame,
        new_df: pd.DataFrame,
        ) -> pd.DataFrame:
        """일부 df에 대해서 PPD를 계산하는 메소드"""
        # 개별 PPDP를 이용하여 일부 PPD를 계산합니다.
        existing_df = existing_df.copy()
        # 시작과 끝 날짜 설정
        dates = new_df.index.get_level_values('일자').unique().sort_values()
        start_date, end_date = dates[0], dates[-1]
        for p in self.ppdps:
            logger.info(f"Processing {p.__class__.__name__}...")
            existing_df = p.process_existing_df(df=existing_df, processing_start_date=start_date, processing_end_date=end_date)
        logger.info(f"Finished calculating ppd data until today...")
        # PPD 계산이 완료된 df를 반환합니다.
        return self._change_data_type_of_df(existing_df)

    def _merge_ppd_with_new_raw(self, ppd_df:pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
        """새로운 raw 데이터를 기존 PPD 데이터와 계산하기 전에, 
        물리적으로 두 DataFrame을 합칩니다.
        """
        # ppd_df와 new_df의 일자 인덱스가 겹치면 에러발생 > 나중에 어떻게 처리할지 고민해보자. 흠..
        ppd_dates = ppd_df.index.get_level_values('일자').unique().sort_values()
        new_dates = new_df.index.get_level_values('일자').unique().sort_values()
        if ppd_dates.intersection(new_dates).size > 0:
            logger.warning(
                "PPD DataFrame and new DataFrame have overlapping dates.\n"
                "new_df 일자 기준으로 모든 데이터를 다시 계산합니다. ")
            # raise ValueError("PPD DataFrame and new DataFrame have overlapping dates. Please ensure they are distinct.")

        start_date = new_dates[0]
        # start_date 이전의 PPD 데이터를 필터링합니다.
        filtered_ppd_df = ppd_df[ppd_df.index.get_level_values('일자') < start_date]
        merged_df = pd.concat([filtered_ppd_df, new_df], ignore_index=False).sort_index()
        return merged_df

class DF_PPD_external_df(DF_PPD_calculate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edh = StockDataHandler() # self.df를 위한 DataHandler
    # @property
    # def df(self) -> pd.DataFrame:
    #     """
    #     DataFrame:
    #     index: ['일자', '종목코드']
    #     columns: [
    #         '종목명', '마켓구분', 
    #         '변동률', '변동률_장후', '시가총액', '상장주식수', # 변동률_장후는 종가대비 넥스트 변동률
    #         '시가', '고가', '저가', '종가', '기준가', '전일대비', 
    #         '거래량', '거래대금', # 거래대금 = 거래대금_krx + 거래대금_nxt
    #         '거래량양수', '연속거래일수', 
    #         '종가상한가여부', '종가하한가여부', '시가상한가여부', '시가하한가여부', '종가상하한가', '시가상하한가' 
    #         ]
    #     """
    #     if self.dh.df.empty:
    #         logger.warning("DataFrame is empty. Calculating PPD...")
    #         raise ValueError("DataFrame is empty. Please call .ready() first.")
    #     self.edh.set_data(convert_as_core_ppd_df(original_df=self.dh.df)) # df를 계산함과 동시에 self.edh에 저장합니다.
    #     return self.edh.df

    @property
    def df(self) -> pd.DataFrame:
        """
        index: ['일자', '종목코드']
        columns: [
        '종목명', '마켓구분',
        '변동률', '시가총액', '상장주식수',
        '거래량', '거래대금', # 거래량은 수정값
        '시가', '고가', '저가', '종가', '기준가', '전일대비', # 수정값
        '시가_krx', '고가_krx', '저가_krx', '종가_krx', '기준가_krx',
        '거래량_krx', '거래대금_krx'
        '변동률_krx', '변동률_nxt', '변동률_장후', # 변동률_장후는 종가대비 넥스트 변동률
        '시가_nxt', '고가_nxt', '저가_nxt', '종가_nxt', '거래량_nxt', '거래대금_nxt',
        '거래량_krx', '거래대금_krx',
        '전일종가_krx', '익일기준가_krx',
        '금일가격조정멀티플', '누적가격조정멀티플',
        '거래량양수', '연속거래일수',
        '상한가_krx', '하한가_krx',
        '종가상한가여부', '종가하한가여부', '시가상한가여부', '시가하한가여부', '종가상하한가', '시가상하한가'
        ]
        """
        if self.dh.df.empty:
            logger.warning("DataFrame is empty. Calculating PPD...")
            raise ValueError("DataFrame is empty. Please call .ready() first.")
        return convert_as_ppd_df(original_df=self.dh.df)
    
class DF_PPD_prepare(DF_PPD_external_df):
    def __init__(self, raw:DF_RAW, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw = raw
        
    def prepare_from_new_df(self, df:pd.DataFrame) -> pd.DataFrame:
        """새로운 df를 받아서 PPD를 계산후, 
        self.dh에 저장합니다.
        주로 raw를 통해서 df를 제공받습니다"""
        logger.info("Preparing PPD from new df...")
        df_processed = self.calculate_whole(df)
        self.dh.set_data(df=df_processed)
        return df_processed

    def prepare_from_feather(self) -> pd.DataFrame:
        """feather 파일에서 PPD를 준비합니다."""
        logger.info("Preparing PPD from feather file...")
        # self.dh.set_data(df=self.feather_manager.load_from_feather())
        try:
            df_processed = self._load_from_feather()
        except FileNotFoundError:
            logger.error("Feather file not found. Preparing from raw data...")
            self._when_feather_not_found()
            return self.dh.df
        last_ppd_date = df_processed.index.get_level_values('일자').max()
        new_df = self.raw.dh.df_after(last_ppd_date, include_date=False)
        if new_df.empty:
            logger.info("No new data to process. Returning existing PPD DataFrame.")
            self.dh.set_data(df=df_processed)
            return df_processed
        # 두 DataFrame을 병합합니다.
        df_processed = self._merge_ppd_with_new_raw(ppd_df=df_processed, new_df=new_df)
        # PPD 계산을 수행합니다.
        df_processed = self.calculate_recent(existing_df=df_processed, new_df=new_df)
        self.dh.set_data(df=df_processed)
        self._save_to_feather()
        return df_processed
        
    def _when_feather_not_found(self):
        """feather 파일이 없는 경우 RAW에서 데이터를 준비합니다. 
        """
        df=self.raw.df
        self.prepare_from_new_df(df)
        self._save_to_feather()


class DF_PPD_update_new(DF_PPD_prepare):
    def get_updated_df_with_new_df(
        self, 
        df_today: pd.DataFrame,
        ) -> pd.DataFrame:
        """
        """
        # 두 DataFrame을 병합합니다.
        df_processed = self._merge_ppd_with_new_raw(ppd_df=self.dh.df, new_df=df_today)
        # PPD 계산을 수행합니다.
        df_processed = self.calculate_recent(existing_df=df_processed, new_df=df_today)
        # 결과값은 저장하지 않고 바로 반환.
        return df_processed


class DF_PPD_ddf(DF_PPD_update_new):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 오늘의 임시 데이터를 위한 DataFrame을 초기화합니다.
        self.is_today_ddf_initialized = False # 9시20분 이후로 초기화 된 적이 있는지 여부
        self.is_today_ddf_finalized = False # 8시 10분 이후로 최종화된 적이 있는지 여부

    @property
    def ddf(self) -> pd.DataFrame:
        return self._get_ddf()
    def _get_ddf(self) -> pd.DataFrame:
        """
        DDF(Delta DataFrame)를 반환합니다.
        9시 20분 이후로 업데이트된 데이터를 포함합니다. 
        """
        df_today = self.raw.fetch_recent_df()
        df_updated = self.get_updated_df_with_new_df(df_today=df_today)
        return convert_as_ppd_df(df_updated)


class DF_PPD_today(DF_PPD_ddf):
    @property
    def _updatable_time(self)-> pd.Timestamp:
        """
        오늘 데이터가 없데이트가 가능한 시간 리턴. 일자는 오늘일자로. 공휴일에도 그냥 리턴.
        넥스트가 늦게 끝나므로 넥스트 기준으로 리턴한다.
        """
        return self.raw.raw_nxt._updatable_time

    """
    오늘의 임시 데이터를 이용하는 PPD 클래스.
    어제까지의 데이터는 업데이트된 상태여야 한다. 
    """
    def get_today_updated_df(self) -> pd.DataFrame:
        """
        오늘의 데이터를 업데이트합니다. 
        시간에 따라서 임시 데이터와 최종 데이터를 구분합니다.
        - 9시 20분 이전: 어제자 종가 기준 임시 데이터로 저장 > 매우 불안정한 데이터(가급적 사용하지 말 것)
        - 9시 20분 이후: krx 20분 지연 임시 데이터로 저장
        - (오후) 8시 10분 이후: 최종 데이터로 저장
        """
        # 금일이 휴장일인 경우, self.df를 그대로 반환한다. 
        if odi.today_is_holiday:
            return self.df
        # 아래는 금일이 개장일인 경우
        # 9시 20분 이후부터 장종료 전까지만 우선 구현. 
        if not odi.is_krx_realtime_data_ready():
            # Fixme
            return self.df
        # elif not odi.is_today_nxt_final_data_ready():
        #     # 'realtime'
        #     return self.ddf
        else:
            return self.ddf


class DF_PPD(DF_PPD_today):
    """
    self.df.columns = [
        '종목명', '마켓구분', # 그대로 유지
        '변동률', '시가총액', '상장주식수', # 그대로 유지
        '거래량', # 거래량_krx, 거래량_nxt를 합산한 이전 값은 버리고 수정거래량으로 대치
        '거래대금', # 합산값으로 그대로 유지
        '시가', '고가', '저가', '종가', '기준가', '전일대비', # 각각 '수정'xx 에서 '수정'을 제거
        '시가_krx', '고가_krx', '저가_krx', '종가_krx', # 원래 시가, 고가, 저가, 종가
        '거래량_krx', '거래대금_krx', # 그대로 유지
        '변동률_krx', '변동률_nxt', # 추가
        '시가_nxt', '고가_nxt', '저가_nxt', '종가_nxt', '거래량_nxt', '거래대금_nxt',
        '거래량_krx', '거래대금_krx', # 그대로 유지
        '전일종가_krx', '익일기준가_krx', # '전일종가', '익일기준가' 사용
        '금일가격조정멀티플', '누적가격조정멀티플', # 그대로 유지
        '거래량양수', '연속거래일수', # 그대로 유지
        '상한가_krx', '하한가_krx', # '상한가', '하한가' 사용
        '종가상한가여부', '종가하한가여부', '시가상한가여부', '시가하한가여부', '종가상하한가', '시가상하한가' # 그대로 유지
        ]
        
    self.dh.df.columns = [
        '표준코드', '종목명', '마켓구분', '관리구분', '종가', '변동코드', '전일대비',
        '변동률', '시가', '고가', '저가', '거래량', '거래대금', '시가총액', '상장주식수', '시장ID', '기준가',
        '종가_nxt', '시가_nxt', '고가_nxt', '저가_nxt', '거래량_nxt', '거래대금_nxt',
        '거래량_krx', '거래대금_krx', '전일종가', '익일기준가', '금일가격조정멀티플', '누적가격조정멀티플',
        '수정시가', '수정고가', '수정저가', '수정종가', '수정기준가', '수정전일대비', '수정거래량', '거래량양수',
        '연속거래그룹', '연속거래일수', '상한가', '하한가', '종가상한가여부', '종가하한가여부', '시가상한가여부',
        '시가하한가여부', '종가상하한가', '시가상하한가'
        ]
    """
    def __init__(
        self, 
        raw:DF_RAW,
        base_feather_name: str='ppd',
        ):
        super().__init__(
            raw=raw,
            base_feather_name=base_feather_name,
            )
    
    def ready(self):
        self.raw.ready()
        self.prepare_from_feather()


ppd_recent = DF_PPD(raw=raw_recent, base_feather_name='ppd_recent')
ppd_all = DF_PPD(raw=raw_all, base_feather_name='ppd_all')


if __name__ == "__main__":
    ppd = ppd_all
    ppd.ready()
    
    df = ppd.dh.df_after("2025-06-02")
    print(df.head())

    print("Finished Testing DF_PPD.")