# essential imports
from mydatahandler.api import StockDataHandler

# 다른 주석을 달기 위해서 클래스 생성
class StockDataHandlerKRX(StockDataHandler):
    """
    df:pd.DataFrame
        index: ['일자', '종목코드']
        columns = ['표준코드', '종목명', '마켓구분', '관리구분', '종가', '변동코드', '전일대비', '변동률', 
            '시가', '고가', '저가', '거래량', '거래대금', '시가총액', '상장주식수', '시장ID', '기준가']            
    """
    pass
class StockDataHandlerNXT(StockDataHandler):
    """
    df:pd.DataFrame
        index: ['일자', '종목코드']
        columns = ['표준코드', '종목명', '마켓구분', '종가', '전일대비', '변동률', 
            '시가', '고가', '저가', '거래량', '거래대금', '시장ID']
    """
    pass