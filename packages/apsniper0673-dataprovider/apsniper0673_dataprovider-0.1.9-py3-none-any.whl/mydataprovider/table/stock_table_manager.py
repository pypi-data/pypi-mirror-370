from typing import Union, List, Dict, Any, Optional
import pandas as pd
from sqlalchemy import text, inspect
import os
import datetime

from mydataprovider.table.db_with_sql import DBWithSQL

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(original_logger, {'prefix': 'TM'})

class TableManager():
    """
    기본적인 쿼리들을 실행하는 클래스
    """
    def __init__(self) -> None:
        super().__init__()
        self.initial_date:pd.Timestamp = pd.Timestamp('2011-01-01').normalize()
        self.table_name = None
        self.date_col_name = '일자'
        self.symbol_col_name = '종목코드'
        self.primary_keys:List[str] = [self.date_col_name, self.symbol_col_name] # ['일자', '종목코드']
        self.updated_dates:List[datetime.date] = []
        self.db_with_sql = DBWithSQL() # DBMWithSQL 객체 생성
        self.df:pd.DataFrame = pd.DataFrame()
        
    def execute(self, query: str, params:Dict[str, Any]=None) -> Any:
        """SQL 쿼리를 실행 / str, text(str) 모두 가능"""
        if params is None:
            params = {}
        with self.db_with_sql.engine.connect() as connection:
            if isinstance(query, str):
                res = connection.execute(text(query), params)
            else:
                res = connection.execute(query, params)
        return res

    def read_sql(self, query: str) -> Union[pd.DataFrame, Any]:
        """pd.read_sql을 이용 / 1*1리턴값은 값만 리턴"""
        df = pd.read_sql(query, con=self.db_with_sql.engine)
        # row와 col모두 하나인 경우에는 값만 반환
        if df.shape[0] == 1 and df.shape[1] == 1:
            return df.iloc[0, 0]
        return df

    def select(self, **conditions: Any) -> pd.DataFrame:
        """등치 조건의 select sql을 간단히 실행"""
        return self.db_with_sql.select_rows(self.table_name, **conditions)
    def select_between(self, start_date: datetime.date, end_date: datetime.date, **conditions: Any) -> pd.DataFrame:
        conditions.update({self.date_col_name: (start_date, end_date, 'between')})
        return self.select(**conditions)
    def select_from(self, from_date: datetime.date=None, **conditions: Any) -> pd.DataFrame:
        conditions.update({self.date_col_name: ('>=', from_date)})
        return self.select(**conditions)
    def delete(self, **conditions: Any) -> None:
        """등치 조건의 delete sql을 간단히 실행"""
        self.db_with_sql.delete_rows(self.table_name, **conditions)
    def delete_between(self, start_date: datetime.date, end_date: datetime.date, **conditions: Any) -> None:
        conditions.update({self.date_col_name: (start_date, end_date, 'between')})
        self.delete(**conditions)
    def delete_from(self, from_date: datetime.date=None, **conditions: Any) -> None:
        conditions.update({self.date_col_name: ('>=', from_date)})
        self.delete(**conditions)
    def check_exists(self, **conditions: Any) -> bool:
        return self.db_with_sql.check_exists(self.table_name, **conditions)
    
    def is_table_exists(self, table_name: str=None) -> bool:
        """
        데이터베이스에 해당 테이블이 존재하는지 확인한다.
        """
        if table_name is None:
            table_name = self.table_name
        stock_inspector = inspect(self.db_with_sql.engine)
        return table_name in stock_inspector.get_table_names()

    def get_table_columns(self, table_name: str=None) -> list:
        """
        데이터베이스 테이블의 컬럼 이름을 가져온다.
        """
        stock_inspector = inspect(self.db_with_sql.engine)
        columns_info = stock_inspector.get_columns(table_name)
        columns = [col['name'] for col in columns_info]
        return columns
    
    def get_primary_keys(self, table_name: str) -> list:
        """
        데이터베이스 테이블의 기본 키 컬럼을 가져온다.
        """
        inspector = inspect(self.db_with_sql.engine)
        primary_keys = inspector.get_pk_constraint(table_name)['constrained_columns']
        print(f"Primary keys: {primary_keys}, in get_primary_keys")
        return primary_keys
    
    def set_primary_keys(self, table_name: Optional[str] = None):
        """
        TEXT 컬럼을 포함한 복합키를 만들 때, 컬럼별 인덱싱 길이를 명시해주는 방식.
        key_lengths: {'컬럼명': 길이}
        """
        if table_name is None:
            table_name = self.table_name

        if not self.primary_keys:
            raise ValueError("self.primary_keys가 설정되지 않았습니다.")

        key_lengths = {'종목코드':50}
        
        key_clause_parts = []
        for col in self.primary_keys:
            if col in key_lengths:
                key_clause_parts.append(f"`{col}`({key_lengths[col]})")
            else:
                key_clause_parts.append(f"`{col}`")

        pk_clause = ", ".join(key_clause_parts)
        sql = f"ALTER TABLE `{table_name}` ADD PRIMARY KEY ({pk_clause});"
        logger.info(f"Setting primary keys: {pk_clause}")
        # 테이블에 기본 키를 설정하는 SQL 쿼리 실행
        self.db_with_sql.execute_query(sql)
        
    def truncate_table(self, table_name: str=None) -> None:
        table_name = self.table_name if table_name is None else table_name
        sql = f"TRUNCATE TABLE `{table_name}`;"
        self.db_with_sql.execute_query(sql)
        logger.info(f"다음 테이블을 비웠습니다: {table_name}")
    
    # Override해서 사용할 예정
    def fetch_daily_stock_prices_from_web(self, date:pd.Timestamp, post_to_server:bool=False) -> pd.DataFrame:
        return pd.DataFrame()

class StockTableManager(TableManager):
    def __init__(self) -> None:
        super().__init__()
        self.date_col_name = '일자'
        self.symbol_col_name = '종목코드'
        self.updated_dates:List[pd.Timestamp] = []
        self.updated_index:pd.MultiIndex = None

    def get_table_columns(self, table_name: str=None) -> list:
        if table_name is None:
            table_name = self.table_name
        """
        데이터베이스 테이블의 컬럼 이름을 가져온다.
        """
        return super().get_table_columns(table_name)

    def create_empty_table(self) -> None:
        """
        web에서 초기 날짜의 데이터를 가져와서 서버에 업로드 하여 테이블을 생성 후,
        테이블을 비운다. 
        """
        if not self.is_table_exists(self.table_name):
            logger.info(f"Creating {self.table_name} table...")
            df = self.fetch_daily_stock_prices_from_web(self.initial_date, post_to_server=True)
            # 테이블을 비운다.
            self.set_primary_keys(table_name=self.table_name)
            self.truncate_table(self.table_name)
        else:
            logger.info(f"{self.table_name} table already exists.")
    
    def _create_empty_df(self, sql_file_name:str) -> pd.DataFrame:
        # 서버에 테이블 생성
        # Fixme: 노트북에서 실행될 때 오류발생할 듯
        path = os.path.join(os.getcwd(), 'table', 'sql', sql_file_name)
        with open(path, 'r', encoding='utf-8') as f:
            create_sql = f.read()
        self.db_with_sql.execute_query(create_sql)
        
    # post, fetch의 경우, dataframe의 index 처리가 다를 수 있기 때문에, 상속받은 클래스에서 처리한다. 
    def _post_updated(self, df:pd.DataFrame) -> None:
        self.db_with_sql.post_df(table_name=self.table_name, df=df, primary_keys=self.primary_keys)
    def fetch_whole(self) -> pd.DataFrame:
        """
        서버에서 모든 데이터를 가져와서 df에 저장.
        """
        df = self.db_with_sql.fetch_df(self.table_name)
        return df