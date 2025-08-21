# Public imports
from typing import List, Dict
import requests
import pickle

import pandas as pd

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger, logger as original_logger
logger = CustomAdapter(original_logger, {'prefix': 'NDClient'})

"""
NDP Server에 대응하는 클라이언트 모듈입니다.
"""

# Essential imports
from mydataprovider.utility.get_available_server import get_available_server

# 로컬 호스트를 먼저 찾는다 > 데이터 절약하기 위해서
server_candidates = [
    'http://localhost:5012', # 백업서버
    'http://localhost:5002',
    'http://brstk.com:5012', # 백업서버
    'http://brstk.com:5002',
    'http://brstk.iptime.org:5002',
    ]

SERVER_URL = get_available_server(server_candidates=server_candidates)

if SERVER_URL is None:
    raise Exception("No available server.")
logger.info(f"Connected to: {SERVER_URL}")

def fetch_all(preview=False):
    """
    GET 요청을 통해 여러 종목 정보를 가져옵니다.
    받는 데이터는 DataFrame이며, 이를 그대로 반환합니다. 
    종목 정보는 acc_data와 non_acc_data가 합쳐져 있습니다. 
    
    Returns: pd.DataFrame
            index = ['일자', '종목코드']
            columns =[
                '종목명', '정규장', '넥스트', '전일가', '현재가', '전일대비', '변동률',
                '변동률_nxt', '변동률_장후', '기준가', '시가', '고가', '저가', '종가', '종가_krx', '종가_nxt',
                '상한가', '하한가', '거래량', '거래량_krx', '거래량_nxt', '거래대금', '거래대금_krx',
                '거래대금_nxt'
                ]
    """
    params = {"preview": str(preview).lower()}
    url = f"{SERVER_URL}/fetch_all"
    
    res = requests.get(url, params=params)
    res.raise_for_status()  # HTTP 에러 시 예외 발생
    
    if preview:
        # JSON (list of dicts) → DataFrame
        json_data = res.json()
        df = pd.DataFrame(json_data)
        df['일자'] = pd.to_datetime(df['일자']).dt.normalize()
        df = df[['일자', '종목코드'] + [col for col in df.columns if not col in ['일자', '종목코드']]]
        df.set_index(['일자', '종목코드'], inplace=True, drop=True)
    else:
        # Pickle (binary) → DataFrame
        df = pickle.loads(res.content)
    return df
    

"""
여러 종목 정보를 가져오는 함수
"""
def fetch_some(symbols:List[str])-> pd.DataFrame:
    """
    POST 요청을 통해 여러 종목 정보를 가져옵니다.
    받는 데이터는 DataFrame이며, 이를 그대로 반환합니다. 
    Returns: pd.DataFrame
            index = ['일자', '종목코드']
            columns =[
                '종목명', '정규장', '넥스트', '전일가', '현재가', '전일대비', '변동률',
                '변동률_nxt', '변동률_장후', '기준가', '시가', '고가', '저가', '종가', '종가_krx', '종가_nxt',
                '상한가', '하한가', '거래량', '거래량_krx', '거래량_nxt', '거래대금', '거래대금_krx',
                '거래대금_nxt'
                ] # 넥스트레이드 값은 0
    """
    response = requests.post(
        f"{SERVER_URL}/fetch_some", 
        json={"symbols": symbols})
    if response.ok:
        # octec-stream으로 반환되므로, 이를 DataFrame으로 변환
        df = pickle.loads(response.content)
        return df
    else:
        print("POST 오류:", response.status_code, response.text)
        return pd.DataFrame(columns=['일자', '종목코드']).set_index(['일자', '종목코드'], drop=True)  # 빈 DataFrame 반환

def fetch_acc(symbols:List[str]) -> pd.DataFrame:
    """
    여러 종목 정보를 가져오는 함수입니다.
    symbols: List[str] - 종목 코드 리스트
    Returns: pd.DataFrame
        index = ['일자', '종목코드']
        columns =[
            '종목명', '정규장', '넥스트', '전일가', '현재가', '전일대비', '변동률',
            '변동률_nxt', '변동률_장후', '기준가', '시가', '고가', '저가', '종가', '종가_krx', '종가_nxt',
            '상한가', '하한가', '거래량', '거래량_krx', '거래량_nxt', '거래대금', '거래대금_krx',
            '거래대금_nxt'
        ]
    """
    response = requests.post(
        f"{SERVER_URL}/fetch_acc", 
        json={"symbols": symbols})
    if response.ok:
        # octec-stream으로 반환되므로, 이를 DataFrame으로 변환
        df = pickle.loads(response.content)
        return df
    else:
        print("POST 오류:", response.status_code, response.text)
        return pd.DataFrame(columns=['일자', '종목코드']).set_index(['일자', '종목코드'], drop=True)  # 빈 DataFrame 반환

def get_acc_symbols():
    """
    정확한 종목 정보를 가진 종목들의 리스트를 반환합니다.
    Returns: List[str] - 정확한 종목 코드 리스트
    """
    response = requests.get(f"{SERVER_URL}/get_acc_symbols")
    if response.ok:
        data = response.json()
        return data.get("acc_symbols", [])
    else:
        print("GET 오류:", response.status_code, response.text)
        return []

# 실행 예시
if __name__ == "__main__":
    from mystockutil.df.format import myprint as print
    
    symbols = [
        "005930",  # 삼성전자
        "000660",  # SK hynix
        # "035420",  # NAVER
        # "005380",  # 현대차
        # "068270",  # 셀트리온
    ]
    # for stock in stocks:
    res = fetch_acc(symbols)
    print(res)
    # res_df = fetch_all(preview=True)
    # res = fetch_some(symbols)
    
    print(f"Fineshed")