import pandas as pd
from sqlalchemy import create_engine, text, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
import datetime
from typing import Union, Any, List
import urllib.parse

from mydataprovider.utility.db.sql import find_missing_columns, add_columns_to_table
from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(original_logger, {'prefix': 'SQLExecutor'})

# 사용할 섹션 설정
section = 'DEFAULT'  # table.brstk.com의 서버에 접속
# section = 'SUB'  # brstk.iptime.org의 서버에 접속(미니피씨)

from myconfigreader import ConfigReader
config = ConfigReader(config_file_name='stock_table_info.ini')
config.set_section(section_name=section)  # 사용할 섹션 설정

# 구성 값 불러오기
USER = config.get_value(key='USER')
PASS = config.get_value(key='PASS')
HOST = config.get_value(key='HOST')
PORT = int(config.get_value(key='PORT'))  # PORT는 int로 가져오는 것이 일반적

# Fixme - tr_data를 처리하는 모듈도 수정할 것
class DBConnector:
    def __init__(
        self,  
        user: str = USER,
        password: str = PASS,
        host: str = HOST,
        port: int = PORT,
        database_name: str = 'stock_data',
        ):
        """DBManager 생성자입니다. DB 연결을 위한 engine과 session을 생성합니다.
        생성자에서 engine과 session을 자동으로 생성합니다."""
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database_name = database_name

        self.engine = self._create_engine()
        self.Session = sessionmaker(bind=self.engine)
    
    def __del__(self):
        self.close_engine()

    def set_connection_info(self, user:str, password:str, host:str, port:int, database:str):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database_name = database
        # 변경된 정보로 DB에 접속한다.
        self.engine = self._create_engine()
        self.Session = sessionmaker(bind=self.engine)

    def get_connection_string(self) -> str:
        return self.make_connection_string(self.user, self.password, self.host, self.port, self.database_name)



    def make_connection_string(self, user: str, password: str, host: str, port: int, database: str) -> str:
        encoded_pw = urllib.parse.quote_plus(password)
        return f'mariadb+pymysql://{user}:{encoded_pw}@{host}:{port}/{database}'

    def _create_engine(self) -> Engine:
        connection_string = self.get_connection_string()
        return create_engine(
            connection_string, pool_size=10, max_overflow=20,
            pool_recycle=3600,     # 1시간마다 커넥션 재활용
            pool_pre_ping=True 
            )

    def get_session(self):
        return self.Session()
    
    def close_engine(self):
        if self.engine is not None:
            try:
                self.engine.dispose()
            except BaseException  as e:
                # logger.error(f"Error while disposing engine- type:{type(e)}, msg: {e}")
                print(f"Error while disposing engine- type:{type(e)}, msg: {e}")

class DBWithSQL(DBConnector):
    """
    query가 들어가는 메쏘드들을 정의합니다.
    """
    def execute_query(self, query: str, params: dict = None) -> Any:
        """Execute a query with optional parameters."""
        with self.engine.connect() as connection:
            trans = connection.begin()
            try:
                if params is None:
                    # 파라미터가 주어지지 않으면 기본적으로 쿼리만 실행
                    res = connection.execute(text(query))
                else:
                    # 파라미터가 있을 경우 바인딩하여 실행
                    res = connection.execute(text(query), params)
                trans.commit()
            except Exception as e:
                logger.error(f"Error: {e} in execute_query")
                trans.rollback()
                raise e
        return res

    def add_primary_key(self, table_name: str, primary_key: Union[str, List[str]]) -> None:
        """Add a primary key to a table. If a TEXT/BLOB column is used, convert it to VARCHAR(TEXT_KEY_SIZE)."""
        TEXT_KEY_SIZE = 50  # TEXT/BLOB 칼럼을 VARCHAR로 변경할 때 사용할 크기
        if isinstance(primary_key, str):
            primary_key = [primary_key]

        pk_clause = ', '.join(f"`{col}`" for col in primary_key)

        with self.engine.connect() as connection:
            try:
                # 현재 테이블 컬럼 타입 조회
                inspector = inspect(self.engine)
                columns_info = inspector.get_columns(table_name)
                col_types = {col['name']: col['type'].__class__.__name__.lower() for col in columns_info}

                # TEXT/BLOB이면 VARCHAR(50)으로 자동 변경
                for col in primary_key:
                    col_type = col_types.get(col)
                    if col_type in ['text', 'blob']:
                        alter = f"ALTER TABLE `{table_name}` MODIFY `{col}` VARCHAR({TEXT_KEY_SIZE});"
                        connection.execute(text(alter))

                # PRIMARY KEY 추가
                query = f"ALTER TABLE `{table_name}` ADD PRIMARY KEY ({pk_clause})"
                connection.execute(text(query))

            except Exception as e:
                logger.error(f"Error: {e} in add_primary_key")
            
    def _build_conditions(self, conditions: dict) -> tuple[str, dict]:
        """Helper method to build SQL conditions and parameters."""
        conditions_str = []
        params = {}
        
        for column, value in conditions.items():
            if isinstance(value, tuple):
                if len(value) == 2 and isinstance(value[0], str) and value[0] in ['>', '<', '>=', '<=']:
                    operator = value[0]
                    conditions_str.append(f"{column} {operator} :{column}")
                    params[column] = value[1]
                elif len(value) == 3 and isinstance(value[2], str) and value[2] == 'between':
                    conditions_str.append(f"{column} BETWEEN :{column}_start AND :{column}_end")
                    params[f"{column}_start"] = value[0]
                    params[f"{column}_end"] = value[1]
            else:
                conditions_str.append(f"{column} = :{column}")
                params[column] = value
        
        return ' AND '.join(conditions_str), params

    def select_rows(self, table_name: str, **conditions: Any) -> pd.DataFrame:
        """Select rows from a table with given conditions."""
        conditions_str, params = self._build_conditions(conditions)
        query = f"SELECT * FROM {table_name} WHERE {conditions_str}" if conditions_str \
            else f"SELECT * FROM {table_name}"
        
        with self.engine.connect() as connection:
            result = connection.execute(text(query), params)
            data=result.fetchall()
            cols = result.keys()
            df = pd.DataFrame(data, columns=cols)
        return df

    def delete_rows(self, table_name: str, **conditions: Any) -> None:
        """Delete rows from a table with given conditions."""
        conditions_str, params = self._build_conditions(conditions)
        query = f"DELETE FROM {table_name} WHERE {conditions_str}"
        
        with self.engine.connect() as connection:
            try:
                trans = connection.begin()
                connection.execute(text(query), params)
                trans.commit()
            except Exception as e:
                logger.error(f"Error: {e} in delete_rows")
                trans.rollback()

    def check_count(self, table_name: str, **conditions: Any) -> int:
        """Check the count of rows in a table with given conditions."""
        conditions_str, params = self._build_conditions(conditions)

        query = f"SELECT COUNT(*) FROM {table_name} WHERE {conditions_str}" if conditions_str \
            else f"SELECT COUNT(*) FROM {table_name}"
        
        with self.engine.connect() as connection:
            result = connection.execute(text(query), params)
            count = result.fetchone()[0]
        
        return count

    def check_exists(self, table_name: str, **conditions: Any) -> bool:
        """Check if a row exists in a table with given conditions."""
        return self.check_count(table_name, **conditions) > 0
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        with self.engine.connect() as connection:
            inspector = inspect(connection)
            return table_name.lower() in inspector.get_table_names()
        
    def get_unique_keys(self, table_name: str) -> List[str]:
        """Get primary keys of a table."""
        with self.engine.connect() as connection:
            inspector = inspect(connection)
            primary_keys = inspector.get_pk_constraint(table_name)['constrained_columns']
        return primary_keys
    
    def fetch_df(self, table_name: str) -> pd.DataFrame:
        """Fetch a table as a DataFrame."""
        with self.engine.connect() as connection:
            query = f"SELECT * FROM {table_name}"
            result = connection.execute(text(query))
            data=result.fetchall()
            cols = result.keys()
            df = pd.DataFrame(data, columns=cols)
        return df
    
    def fetch_df_from(self, table_name: str, date_col_name: str, from_date: datetime.date) -> pd.DataFrame:
        """Fetch a table as a DataFrame from a date."""
        with self.engine.connect() as connection:
            query = f"SELECT * FROM {table_name} WHERE {date_col_name} >= :from_date"
            result = connection.execute(text(query), {'from_date': from_date})
            data=result.fetchall()
            cols = result.keys()
            df = pd.DataFrame(data, columns=cols)
        return df
    
    def post_df(self, table_name: str, df: pd.DataFrame, primary_key:str=None, unique_keys:List[str]=None, exclude_range_index:bool=True, auto_column_repair:bool = True) -> None:
        """
        Post a DataFrame to a table. 
        DB에 해당 테이블이 존재하지 않는 경우, DF를 통해서 테이블을 생성한 후, PK를 지정해준다.
        PK가 중복될 경우, update를 수행합니다.
        df이 비어있는 경우, 아무런 작업도 수행하지 않습니다.
        """
        if not self.check_table_exists(table_name.lower()):
            # 테이블이 존재하지 않는 경우!
            logger.info(f"Creating table {table_name}...")
            if df.index.name or not df.index.is_monotonic_increasing:
                df = df.reset_index()  # 인덱스를 열로 변환
            df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            if primary_key is not None:
                self.add_primary_key(table_name, primary_key)
            return
        # 테이블이 존재하는 경우!
        # PK가 주어지지 않은 경우, 자동으로 추출
        if unique_keys is None:
            unique_keys = self.get_unique_keys(table_name)
        
        # exclude_range_index가 True고, Index에 이름이 없으면 index를 제외
        if exclude_range_index and (df.index.names == ([None])):
            # RangeIndex를 제외
            df = df.reset_index(inplace=False, drop=True)
        else:
            df = df.reset_index(inplace=False, drop=False)

        if auto_column_repair:
            inspector = inspect(self.engine)
            table_columns = [col['name'] for col in inspector.get_columns(table_name)]

            missing_cols = find_missing_columns(df, table_columns)

            if missing_cols:
                logger.info(f"DB에 없는 칼럼 발생: {missing_cols}. 칼럼을 새로 추가합니다 - {table_name}...")
                with self.engine.connect() as connection:
                    add_columns_to_table(connection, table_name, missing_cols, df)
        
        with self.engine.connect() as connection:
            trans = connection.begin()
            cnt = 0
            for _, row in df.iterrows():
                sql = text(f"""
                INSERT INTO {table_name} ({', '.join(df.columns)})
                VALUES ({', '.join([f':{col}' for col in df.columns])})
                ON DUPLICATE KEY UPDATE
                {', '.join([f'{col}=VALUES({col})' for col in df.columns if col not in unique_keys])}
                """)
                
                # print(f"sql to execute: {sql.text}, in post_df")
                
                try:
                    # print(f"row to_dict: {row.to_dict()}")
                    connection.execute(sql, row.to_dict())
                except Exception as e:
                    logger.error(f"Error: {e} in post_df, table_name: {table_name}, row: {row}, pk: {unique_keys}")
                    trans.rollback()
                    return
                cnt += 1
                if cnt != 0 and cnt % 10000 == 0:
                    logger.info(f"Currently, inserted {cnt} rows.")
            trans.commit()
            logger.info(f"Finished: Inserted {cnt} rows to {table_name}.")
        
    def get_columns(self, table_name: str) -> List[str]:
        """Get columns of a table."""
        with self.engine.connect() as connection:
            inspector = inspect(connection)
            columns = inspector.get_columns(table_name)
            return [column['name'] for column in columns]
    
    def truncate_table(self, table_name: str) -> None:
        """Truncate a table."""
        query = f"TRUNCATE TABLE {table_name}"
        with self.engine.connect() as connection:
            connection.execute(text(query))

    def drop_table(self, table_name: str) -> None:
        """Drop a table."""
        query = f"DROP TABLE IF EXISTS {table_name}"
        with self.engine.connect() as connection:
            connection.execute(text(query))
                
if __name__ == '__main__':
    db_manager = DBWithSQL()
    table_name = 'test_table'
    with db_manager.engine.connect() as connection:
        trans = connection.begin()
        
        connection.execute(text("DROP table if exists test_table"))
        connection.execute(text("CREATE TABLE IF NOT EXISTS test_table (id INT PRIMARY KEY, name VARCHAR(50), date DATE)"))
        connection.execute(text("INSERT INTO test_table (id, name, date) VALUES (1, 'Alice', '2023-07-01'), (2, 'Bob', '2023-07-02')"))
        
        trans.commit()

    # 날짜 범위 내의 데이터 조회 테스트
    start_date = datetime.date(2023, 7, 1)
    end_date = datetime.date(2023, 7, 2)
    df = db_manager.select_rows('test_table', date=(start_date, end_date, 'between'))
    assert len(df) == 2

    print(db_manager.select_rows(table_name, name='Alice'))