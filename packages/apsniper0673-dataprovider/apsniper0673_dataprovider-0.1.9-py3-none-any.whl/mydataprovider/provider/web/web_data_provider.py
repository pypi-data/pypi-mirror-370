from typing import List, Tuple
import pandas as pd

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(logger=original_logger, extra={'prefix': 'WDP'})

# Essential imports
from mydataprovider.provider.web.krx.krx_data_provider import kdp
from mydataprovider.provider.web.naver.naver_data_provider import ndp

class _WDP:
    pass

class WDP_krx(_WDP):
    def __init__(self):
        super().__init__()
        self.kdp = kdp # KRX 데이터 프로바이더
    def get_stock_names(self, symbols:list) -> list:
        return self.kdp.get_stock_names(stock_symbols=symbols)
    def get_stock_symbols(self, names:list) -> list:
        return self.kdp.get_stock_symbols(stock_names=names)

class WDP_naver(WDP_krx):
    def __init__(self):
        super().__init__()
        self.ndp = ndp # Naver 데이터 프로바이더
    @property
    def acc_symbols(self) -> List[str]:
        """
        정확한 종목 코드 리스트를 반환합니다.
        """
        return self.ndp.acc_symbols
    def add_acc(self, symbols: List[str]) -> Tuple[List[str], List[str]]:
        """
        symbols를 정확한 종목 코드 리스트에 종목을 추가합니다.
        """
        return self.ndp.add_acc(symbols)
    def fetch_acc(self, symbols: List[str]) -> pd.DataFrame:
        """
        symbols에 해당하는 종목들의 정보를 가져옵니다.
        이 종목들은 자동으로 정확한 종목 코드 리스트에 추가됩니다.
        
        Returns: DataFrame
            Index: ['일자', '종목코드']
            columns: 
                [
                '종목명', '현재가', '전일가', '기준가', '전일대비', '변동률', '시가', '고가', '저가', '상한가', '하한가', 
                '거래량', '거래량_krx', '거래량_nxt',
                '거래대금', '거래대금_krx', '거래대금_nxt', '시가총액', '상장주식수',
                ]
        """
        return self.ndp.fetch_acc(symbols)
    def fetch_some(self, symbols: List[str]) -> pd.DataFrame:
        """
        여러 종목의 정보를 DataFrame으로 반환합니다.
        
        Returns: pd.DataFrame
            Index: ['일자', '종목코드']
            columns =[
                '종목명', '정규장', '넥스트', '전일가', '현재가', '전일대비', '변동률',
                '변동률_nxt', '변동률_장후', '기준가', '시가', '고가', '저가', '종가', '종가_krx', '종가_nxt',
                '상한가', '하한가', '거래량', '거래량_krx', '거래량_nxt', '거래대금', '거래대금_krx',
                '거래대금_nxt'
                ]
        """
        return self.ndp.fetch_some(symbols)
    def fetch_all(self) -> pd.DataFrame:
        """
        모든 종목의 정보를 DataFrame으로 반환합니다.
        
        Returns: pd.DataFrame
            Index: ['일자', '종목코드']
            columns =[
                '종목명', '정규장', '넥스트', '전일가', '현재가', '전일대비', '변동률',
                '변동률_nxt', '변동률_장후', '기준가', '시가', '고가', '저가', '종가', '종가_krx', '종가_nxt',
                '상한가', '하한가', '거래량', '거래량_krx', '거래량_nxt', '거래대금', '거래대금_krx',
                '거래대금_nxt'
                ]
        """
        return self.ndp.fetch_all()


class WebDataProvider(WDP_naver):
    pass

wdp = WebDataProvider()  # 기본 인스턴스 생성

if __name__ == '__main__':
    from mystockutil.df.format import myprint as print
    res = wdp.fetch_acc(["196170"])
    
    # symbols = ["005930", "000660", "035420", "005380", "068270", "012450"]
    # res = wdp.fetch_some(symbols)
    # print(res)
    
    res = wdp.fetch_all()
    print(len(res))
    
    # acc_symbols = len(wdp.acc_symbols)
    # print(acc_symbols)
    
    print("Finished.")
