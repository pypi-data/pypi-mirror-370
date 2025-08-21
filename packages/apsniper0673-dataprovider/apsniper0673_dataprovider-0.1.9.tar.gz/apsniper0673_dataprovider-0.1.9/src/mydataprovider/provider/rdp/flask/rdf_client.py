# public imports
import requests
import pickle
import pandas as pd
from typing import List

# private imports
from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger, logger as original_logger
logger = CustomAdapter(original_logger, {'prefix': 'rdf_client'})

"""
Data Provider Client
"""

# essential imports
from mydataprovider.utility.get_available_server import get_available_server
server_candidates = [
    'http://localhost:5011', # 백업/개발 서버
    'http://localhost:5001',
    'http://brstk.com:5011',
    'http://brstk.com:5001',
    ]

SERVER_URL = get_available_server(server_candidates=server_candidates)

if SERVER_URL is None:
    raise Exception("No available server.")
logger.info(f"Connected to: {SERVER_URL}")

def fetch_df(
    start_date: pd.Timestamp,
    end_date: pd.Timestamp = None,
) -> pd.DataFrame:
    """
    서버의 /fetch_df API 호출.
    
    Args:
        start_date (pd.Timestamp): 조회 시작 날짜
        end_date (pd.Timestamp): 조회 끝 날짜 (선택)
    
    Returns: pd.DataFrame
        index = ['일자', '종목코드']
        columns = [
            '종목명', '마켓구분', '변동률', '시가총액', '상장주식수', 
            '거래량', '거래대금',
            '시가', '고가', '저가', '종가', '기준가', '전일대비', 
            '시가_krx', '고가_krx', '저가_krx', '종가_krx', '기준가_krx', '거래량_krx', '거래대금_krx', 
            '변동률_krx', '변동률_nxt', '변동률_장후', 
            '시가_nxt', '고가_nxt', '저가_nxt', '종가_nxt', '거래량_nxt', '거래대금_nxt',
            '전일종가_krx', '익일기준가_krx', 
            '금일가격조정멀티플', '누적가격조정멀티플', 
            '거래량양수', '연속거래일수',
            '상한가_krx', '하한가_krx', 
            '종가상한가여부', '종가하한가여부', '시가상한가여부', '시가하한가여부',
            '종가상하한가', '시가상하한가'
            ]
    """        
    start_date = pd.to_datetime(start_date).normalize()
    end_date = pd.to_datetime(end_date).normalize() if end_date else pd.Timestamp.now().normalize()
    
    url = f"{SERVER_URL}/fetch_df"
    params = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
    }
    response = requests.post(url, json=params)
    
    if response.status_code == 200:
        # preview 모드면 HTML, 아니면 pickle 데이터
        try:
            return pickle.loads(response.content)
        except Exception as e:
            raise ValueError(f"Failed to decode data: {e}")
    elif response.status_code == 404:
        print("No data found for given parameters.")
        return pd.DataFrame(columns=['일자', '종목코드']).set_index(['일자', '종목코드'], drop=True)
    else:
        raise RuntimeError(f"Request failed: {response.status_code}, {response.text}")

def add_acc(symbols: List[str]) -> List[str]:
    """
    서버의 /add_acc API 호출.
     - symbols를 정확히 측정하는 종목으로 추가합니다.
    
    Returns:
        List[str]: 추가된 종목 코드 리스트
    """
    url = f"{SERVER_URL}/add_acc"
    response = requests.post(url, json={"symbols": symbols})
    
    try:
        return response.json()['added_symbols']
    except Exception as e:
        raise RuntimeError(f"Invalid response: {e}, content={response.text}")

if __name__ == "__main__":
    from mystockutil.df.format import myprint as print
    from mydatahandler.handler.stock_data_handler import StockDataHandler
    dh = StockDataHandler()
    
    start_date = pd.Timestamp("2025-07-21")
    end_date = pd.Timestamp("2025-07-24")
    
    df = fetch_df(start_date=start_date, end_date=end_date)
    dh.df = df
    symbols = ["005930", "000660", "035420", "005380", "068270", "012450"]
    res_df = dh.by_symbols(symbols)
    print(res_df)
    
    new_symbols = ["298040"]
    add_acc(new_symbols)
    
    df = fetch_df(start_date=start_date, end_date=end_date)
    dh.df = df
    res_df = dh.by_symbols(symbols + new_symbols)
    print(res_df)
    
    print("Finished.")