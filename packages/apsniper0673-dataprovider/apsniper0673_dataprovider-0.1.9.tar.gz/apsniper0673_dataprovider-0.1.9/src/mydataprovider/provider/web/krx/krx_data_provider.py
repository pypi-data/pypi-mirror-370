# public imports
import pandas as pd
from typing import List
import pandas as pd

# private imports
from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(logger=original_logger, extra={'prefix': 'KDP'})

"""
KRX Data Provider
"""

# essential imports
from mydatahandler.handler.singleday_data_handler import SingledayDataHandler

class _KRXDataProvider:
    """
    KRX Data Provider
    self.tdf에 금일자의 krx 데이터를 다운 받아서 이를 이용하여 여러 기능을 수행합니다. 
    금일이 휴일인 경우에는, 가장 최근의 데이터를 가져옵니다.
    
    self.tdf:pd.DataFrame
        index='종목코드'
        columns = ['일자', ... ]
    """
    def __init__(self):
        self.sdh:SingledayDataHandler = SingledayDataHandler()
        self.sdh.ready() # 최근 개장일로 데이터를 로드한다. 
    @property
    def df(self) -> pd.DataFrame:
        """
        self.odh.df를 반환합니다.
        index = '종목코드'
        columns = [
            '일자', '표준코드', '종목명', '마켓구분', '관리구분', '종가', '변동코드', '전일대비',
            '변동률', '시가', '고가', '저가', '거래량', '거래대금', '시가총액', '상장주식수', '시장ID', '기준가'
            ]
        """
        return self.sdh.df
    @property
    def date(self) -> pd.Timestamp:
        """
        self.odh.date를 반환합니다.
        데이터의 유일한(동일한) 날짜
        """
        return self.sdh.date
    
    def set_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        df를 self.odh.df로 설정합니다.
        """
        self.sdh.set_data(df)
        return self.df


class KRXDataProvider(_KRXDataProvider):
    def get_stock_names(self, stock_symbols:List[str])->List[str]:
        return self.sdh.get_stock_names(stock_symbols=stock_symbols)
    def get_stock_symbols(self, stock_names:List[str])->List[str]:
        return self.sdh.get_stock_symbols(stock_names=stock_names)

kdp = KRXDataProvider()


if __name__ == '__main__':
    print(kdp.get_stock_names(['005930']))  # 삼성전자
    print("Finished testing Krx Data Provider")