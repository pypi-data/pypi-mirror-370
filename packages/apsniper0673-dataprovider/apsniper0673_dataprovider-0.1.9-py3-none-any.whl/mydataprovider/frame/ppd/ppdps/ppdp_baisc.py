import datetime
import pandas as pd
from typing import List, Tuple

from mydataprovider.table.stock_table_manager import StockTableManager
from mydataprovider.frame.odi.df_odi import odi

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(logger=original_logger, extra={'prefix': 'PPDP'})

"""
PPD의 입출력을 담당. 
"""
class _PPDP:
    def __init__(self) -> None:
        super().__init__()
        self.columns: list = [] # PPDP에서 다루거나 생성하는 모든 칼럼
        self.reading_depth = 0  # 일자기준 데이터를 읽어오는 깊이. 0이면 기준날말. 1일이면 기준날 하루전까지. 
        self.writing_depth = 0 # 일자기준 데이터를 쓰는 깊이. 0이면 기준날만. 1일이면 기준날 하루전까지.
        self.processing_start_date:pd.Timestamp = None # 계산을 시작하는 날짜. 즉, 새로운 raw_data의 첫번째 날짜
        self.processing_end_date:pd.Timestamp = None # 계산을 끝내는 날짜. 즉, 새로운 raw_data의 마지막 날짜
        self.dtype_mapping = {} # 칼럼별 데이터 타입 매핑. PPDP에서 실제 값을 할당한다. 

class PPDP_slicing(_PPDP):
    @property
    def reading_start_date(self):
        return odi.get_prev_open_day(self.processing_start_date, self.reading_depth)
    @property
    def writing_start_date(self):
        return odi.get_prev_open_day(self.processing_start_date, self.writing_depth)
    def _slice_df_for_read(self, df: pd.DataFrame):
        logger.info(f"Slicing df for read: {self.reading_start_date} ~ {self.processing_end_date}")
        return df.loc[(slice(self.reading_start_date, self.processing_end_date), slice(None)), :].copy()
    def _slice_df_for_write(self, df: pd.DataFrame):
        logger.info(f"Slicing df for write: {self.writing_start_date} ~ {self.processing_end_date}")
        return df.loc[(slice(self.writing_start_date, self.processing_end_date), slice(None)), :].copy()


class PPDP_process_new(PPDP_slicing):
    # 상속받은 클래스에도 적용되는 프로세싱 프레임
    def process_new_df(self, df: pd.DataFrame):
        return self.custom_process_new_df(df)
    
    def custom_process_new_df(self, df: pd.DataFrame) -> pd.DataFrame:
        # should be overriden
        return df


class PPDP_Main_process_existing(PPDP_process_new):
    def process_existing_df(self, df: pd.DataFrame, processing_start_date: pd.Timestamp, processing_end_date: pd.Timestamp) -> pd.DataFrame:
        """
        Params:
        df: pd.DataFrame - 기존의 PPD가 계산된 DataFrame + 새로 계산해야하는 날짜의 raw_data가 합쳐진 dataFrame
            - 다른 ppdp에 의해서 계산된 data도 포함되어 있을 수 있다. 
        """
        df = df.copy()
        # 새로 PPD를 계산하여야 하는 시작과 끝 날짜를 설정
        # 이 값은 self.custom_process_existing_df, self.custom_data_fitting, self._slice... 등에서 사용된다.
        self.processing_start_date = processing_start_date
        self.processing_end_date = processing_end_date
        
        res_df = self.custom_process_existing_df(self._slice_df_for_read(df))
        df_to_write = self._slice_df_for_write(res_df)
        # dataFrame에 업데이트
        df.loc[df_to_write.index, :] = df_to_write
        # fitting이 필요한 부분 처리
        df = self.custom_data_fitting(df)
        logger.info(f"Custom Data fitting is done by {self.__class__.__name__}.")
        return df
    
    # df를 받아와서 작업 후 df를 리턴하는 형태로 해야할 듯. 
    def custom_process_existing_df(self, df: pd.DataFrame) -> pd.DataFrame:
        # Could be overriden
        return self.custom_process_new_df(df)    

    def custom_data_fitting(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        df를 받아와서 fitting을 한 후, 그 결과물 df를 리턴한다. 
        """
        # should be overriden
        return df

class PPDP_refresh_today(PPDP_Main_process_existing):
    def initial_process_df_containing_today(self, df: pd.DataFrame, is_refresh:bool=False):
        """
        DDF에서 금일 refresh되는 정보를 Process하기 위한 메쏘드. 
        실시간 데이터를 Processing하기 때문에, 서버에 기록하지 않는다. 
        추가로 구현의 어려움으로 인해서 is_refresh=Ture인 경우 과거의 data는 fitting하지 않는다.
        """
        self.processing_start_date = pd.to_datetime(datetime.date.today())
        self.processing_end_date = self.processing_start_date
        res_df = self.custom_process_existing_df(self._slice_df_for_read(df))
        df_to_write = self._slice_df_for_write(res_df)
        # dataFrame에 업데이트
        df.loc[df_to_write.index, :] = df_to_write
        # fitting이 필요한 부분 처리
        if not is_refresh:
            df = self.custom_data_fitting(df)
        else:
            df = self.custom_data_fitting_as_refresh(df)
        return df
    
    # today_df의 내용을 이용해서 df를 변경해준다.
    def refresh_today_df(self, df: pd.DataFrame, today_df: pd.DataFrame)->pd.DataFrame:
        """Returns: refresh된 df"""
        return self.custom_refresh(df, today_df)
    
    def custom_refresh(self, df: pd.DataFrame, today_df: pd.DataFrame)->pd.DataFrame:
        """Returns: refresh된 df"""
        return df
    
    def custom_data_fitting_as_refresh(self, df: pd.DataFrame)->pd.DataFrame:
        return df
    
class PPD_Processor(PPDP_refresh_today):
    def __init__(self):
        super().__init__()
        self.custom_init()
        
    def custom_init(self):
        """
        상속받은 클래스의 초기화 메쏘드
        오버라이드하여 사용한다.
        """
        pass

if __name__ == '__main__':
    pass