import pandas as pd

from mydataprovider.table.db_with_sql import DBWithSQL
from mydataprovider.table.stock_table_manager import StockTableManager

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(original_logger, {'prefix': 'ODI'})

"""
TMODI: ODI table을 관리하는 클래스입니다.
"""
class _TM_ODI(StockTableManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.table_name = 'odi_'        
        self.table_name = 'odi_new'
        self.primary_keys = [self.date_col_name]
        self.db_with_sql = DBWithSQL()
class TM_ODI(_TM_ODI):
    def fetch_whole(self) -> pd.DataFrame:
        try:
            df = self.db_with_sql.fetch_df(self.table_name)
            df[self.date_col_name] = pd.to_datetime(df[self.date_col_name])
            # 인덱스 설정
            df.set_index(self.date_col_name, drop=False, inplace=True)
            df.index.name = self.date_col_name
            df.sort_index(inplace=True, ascending=True)
            # 칼럼별 데이터 처리
            for col in df.columns:
                if col in ['개장여부']:
                    df[col] = df[col].astype(bool)
        except Exception as e:
            print(f"Error: {e} while fetching odi table.\nAssume it does not exist. Let's make one from 2011")
            # self._create_empty_df()
            raise e
        return df
    
    def post_df(self, df:pd.DataFrame):
        """
        df의 index가 일자이고, 칼럼이 ['일자', '개장여부', ...]인 경우에만 사용합니다.
        Params:
        df: pd.DataFrame - ODI DataFrame의 일부
            index: 일자
            columns: ['일자', '개장여부', ...]
        """
        df = df.copy()
        df.drop(columns=['일자'], inplace=True, errors='ignore')
        
        def timedelta_to_timestr(x):
            return str(x).split()[-1] if pd.notnull(x) else None
        df['개장시간'] = df['개장시간'].apply(timedelta_to_timestr)
        df['폐장시간'] = df['폐장시간'].apply(timedelta_to_timestr)
        
        self.db_with_sql.post_df(self.table_name, df, self.primary_keys[0])
        
    def _create_empty_df(self):
        # 서버에도 테이블을 생성해 준다. 
        with open('./sql/create_odi.txt', 'r', encoding='utf-8') as f:
            create_sql = f.read()
        self.db_with_sql.execute_query(create_sql)
