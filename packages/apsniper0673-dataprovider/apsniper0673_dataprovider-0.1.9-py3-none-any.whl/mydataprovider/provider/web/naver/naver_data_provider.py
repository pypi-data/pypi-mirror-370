import pandas as pd
from typing import Any, List, Tuple

"""
NDP Class
"""

# essential imports
from mydataprovider.provider.web.naver.flask import naver_data_client as ndc


class _NDP:
    def __init__(self):
        self.ndc = ndc  # naver_data_client 모듈을 통해 서버와 통신

class NDP_acc(_NDP):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @property
    def acc_symbols(self) -> List[str]:
        """
        정확한 종목 코드 리스트를 반환합니다.
        """
        return self.ndc.get_acc_symbols()
    
    def fetch_acc(self, symbols: list[str]) -> pd.DataFrame:
        """
        symbols에 해당하는 종목들의 정보를 가져옵니다.
        Returns: DataFrame
            Index: '일자', '종목코드'
            columns: 
                [
                '종목명', '현재가', '전일가', '기준가', '전일대비', '변동률', '시가', '고가', '저가', '상한가', '하한가', 
                '거래량', '거래량_krx', '거래량_nxt',
                '거래대금', '거래대금_krx', '거래대금_nxt', '시가총액', '상장주식수',
                ]
        """
        return self.ndc.fetch_acc(symbols)
    
    def add_acc(self, symbols: List[str]) -> Tuple[List[str], List[str]]:
        """
        symbols를 정확한 종목 코드 리스트에 추가합니다.
        
        Returns: tuple[list[str], list[str]]
            - 새로 추가된 종목 코드 리스트
            - 전체 종목 코드 리스트
        """
        cur_symbols = self.acc_symbols
        new_symbols = [symbol for symbol in symbols if symbol not in cur_symbols]
        total_symbols = list(set(cur_symbols + new_symbols))
        if new_symbols:
            print(f"Fetching new symbols to add to acc...: symbols num={len(new_symbols)}")
            self.fetch_acc(new_symbols) # fetch_acc를 통해 정확한 종목를 보내도록 설정
            print(f"Added new symbols to acc: {new_symbols}")
            
        else:
            print("No new symbols to add to acc.")
        return new_symbols, total_symbols

class NDP_non_acc(NDP_acc):
    def fetch_all(self) -> pd.DataFrame:
        """
        모든 종목의 정보를 DataFrame으로 반환합니다.
        이 중에는 넥스트레이드 값이 있는 것도 있고, 없는 것도 있습니다.
        Returns: pd.DataFrame
            Index: '일자', '종목코드'
            columns: 
                [
                '종목명', '현재가', '전일가', '기준가', '전일대비', '변동률', '시가', '고가', '저가', '상한가', '하한가', 
                '거래량', '거래량_krx', '거래량_nxt',
                '거래대금', '거래대금_krx', '거래대금_nxt', '시가총액', '상장주식수',
                ]
        """
        return self.ndc.fetch_all()
    
    def fetch_some(self, symbols: list[str]) -> pd.DataFrame:
        """
        symbols에 해당하는 종목들의 정보를 가져옵니다.
        이 중에는 넥스트레이드 값이 있는 것도 있고, 없는 것도 있습니다.
        Returns: pd.DataFrame
            Index: '일자', '종목코드'
            columns =[
                '종목명', '정규장', '넥스트', '전일가', '현재가', '전일대비', '변동률',
                '변동률_nxt', '변동률_장후', '기준가', '시가', '고가', '저가', '종가', '종가_krx', '종가_nxt',
                '상한가', '하한가', '거래량', '거래량_krx', '거래량_nxt', '거래대금', '거래대금_krx',
                '거래대금_nxt'
                ]
        """
        res = self.ndc.fetch_some(symbols)
        return res


class NaverDataProvider(NDP_non_acc):
    """
    Naver Data Provider Client Class
    네이버에서 종목 정보를 가져오는 클라이언트를 사용하는 클래스입니다.
    """
    pass

ndp = NaverDataProvider()


if __name__ == "__main__":
    from mystockutil.df.format import myprint as print
    
    symbols = ["005930", "000660", "035420", "005380", "068270", "012450"]
    
    # res = ndp.fetch_some(symbols)
    # print(res)
    # ndp.add_acc(symbols)
    # res = ndp.fetch_some(symbols)
    # print(res)

    res = ndp.fetch_all()
    print(len(res))
    print("Finished fetching stock info.")