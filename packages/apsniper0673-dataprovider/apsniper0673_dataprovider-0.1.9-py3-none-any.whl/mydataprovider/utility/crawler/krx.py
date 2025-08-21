import pandas as pd
import time

from pykrx import stock
from pykrx.website.krx.market.core import 전종목시세

from mydataprovider.utility.crawler.naver import fetch_acc_stock_info_from_naver_as_dict
# from mydataprovider.frame.odi.df_odi import odi
from mydataprovider.frame.odi.df_odi import odi

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(logger=original_logger, extra={'prefix': 'Web'})

def check_market_opened() -> bool:
    """
    현재 시장이 개장 중인지 확인
    #Fixme: 개장시간이 9시가 아닌 특수한 경우도 고려해야 함.
    """
    now = pd.Timestamp.now()
    if now.weekday() >= 5:
        return False
    if now.hour < 9:
        return False
    return True

# PYKRX를 사용하여 코스피, 코스닥 종목 코드를 가져오는 함수
def get_stock_symbols(date:pd.Timestamp, market=None):
    date = pd.Timestamp(date)
    kospis = stock.get_market_ticker_list(date.strftime('%Y%m%d'), market='KOSPI')
    kosdaqs = stock.get_market_ticker_list(date.strftime('%Y%m%d'), market='KOSDAQ')
    if market == 'KOSPI':
        return kospis
    elif market == 'KOSDAQ':
        return kosdaqs
    return kospis + kosdaqs

def fetch_recent_stock_prices_from_krx(market:str='ALL') -> pd.DataFrame:
    today = pd.Timestamp.today().normalize()
    while True:
        df = fetch_daily_stock_prices_from_krx(today, market)
        if not df.empty:
            break
        today -= pd.Timedelta(days=1)
        time.sleep(1)
    return df

def fetch_daily_stock_prices_from_krx(date: pd.Timestamp=None, market:str='ALL') -> pd.DataFrame:
    """
    Returns: pd.DataFrame
        index: 기본 인덱스
        columns = [
            '일자', '종목코드', '표준코드', '종목명', '마켓구분', '관리구분', '종가', '변동코드', '전일대비', '변동률', 
            '시가', '고가', '저가', '거래량', '거래대금', '시가총액', '상장주식수', '시장ID', '기준가'
            ]
    휴일 또는 날짜 오류의 경우 빈 데이터프레임을 반환한다.
    개장일 장전인 경우, 모든 가격정보를 금일 기준가로 설정한다.
    """
    date = pd.Timestamp.today().normalize() if date is None else pd.Timestamp(date).normalize()
    market2mktid = {
        "ALL": "ALL",
        "KOSPI": "STK",
        "KOSDAQ": "KSQ",
        "KONEX": "KNX"
    }
    df = 전종목시세().fetch(date.strftime('%Y%m%d'), market2mktid[market])
    col_new_names = [
        '종목코드', '표준코드', '종목명', '마켓구분', '관리구분', '종가', '변동코드', '전일대비', '변동률', 
        '시가', '고가', '저가', '거래량', '거래대금', '시가총액', '상장주식수', '시장ID'
    ]
    # 칼럼 이름을 한글로 변경
    df.columns = col_new_names

    # NaN 값을 처리: 숫자형 칼럼은 0 또는 -1로, 문자열 칼럼은 빈 문자열로 채우기
    df = df.fillna({'종목코드': '', '표준코드': '', '종목명': '', '마켓구분': '', '섹터구분': '', 
                    '종가': '-1', '변동코드': '-1', '전일대비': '0', '변동률': '0', 
                    '시가': '-1', '고가': '-1', '저가': '-1', '거래량': '-1', '거래대금': '-1', 
                    '시가총액': '-1', '상장주식수': '-1', '시장ID': ''})
    
    # 모든 칼럼에서 빈칸과 쉼표 제거
    df = df.apply(lambda x: x.str.replace('[, ]', '', regex=True) if x.dtype == "object" else x)
    # df에서 '-' 문자를 제거한다. 
    # 단, 전일대비와 변동률은 음수의 값을 가질 수 있다.
    col_to_apply = [col for col in df.columns if not col in ['전일대비', '변동률']]
    df[col_to_apply] = df[col_to_apply].apply(lambda x: x.str.replace(r'[\-]', '', regex=True) if x.dtype == "object" else x)
    
    if (df['전일대비']=='-').all():
        # 휴일인 경우
        # Fixme: odi를 사용하지 않고, 웹에서 확인할 수 있도록 수정하기
        if not odi.is_open_day(date):
            logger.error(f"금일({date})은 휴일입니다. 빈 데이터프레임을 반환합니다.")
            return pd.DataFrame(columns=['일자']+col_new_names)
    # if (df['종가']=='').all():
    # if date == pd.Timestamp.today().normalize(): # 디버깅용
        # 개장 후 20분이 지나지 않아서 가격 데이터가 비어있는 경우, 전 영업일의 데이터를 불러와서 가격데이터를 그대로 사용한다.
        # 전 영업일의 데이터 불러오기
        pdf:pd.DataFrame = None
        pdate = date
        while True:
            pdf = fetch_daily_stock_prices_from_krx(pdate - pd.Timedelta(days=1), market)
            if pdf.empty:
                pdate -= pd.Timedelta(days=1)
                continue
            break
        # 전 영업일의 가격데이터를 사용하는데, 신규상장 종목의 경우 가격을 0으로 설정한다.
        # Fixme: 신규상장 종목의 경우 가격데이터를 웹에서 가져오도록 한다.
        # 금일 종목코드 전체
        tsymbols = df['종목코드'].to_list()
        # 금일 기준 어제와 공통된 종목코드. 즉 상폐된 종목은 신경쓰지 않음
        common_symbols = [s for s in df['종목코드'].to_list() if s in pdf['종목코드'].to_list()]
        # 금일 기준 새로운(신규상장) 종목코드
        new_symbols = [s for s in df['종목코드'].to_list() if s not in pdf['종목코드'].to_list()]
        # common_symbols의 경우, 어제 가격데이터를 사용
        common_df = df[df['종목코드'].isin(common_symbols)].copy().reset_index(drop=True)
        common_pdf = pdf[pdf['종목코드'].isin(common_symbols)].copy().reset_index(drop=True)
        new_df = df[df['종목코드'].isin(new_symbols)].copy().reset_index(drop=True)
        # 종목코드 기준으로 정렬 및 인덱스 재설정
        common_df = common_df.sort_values(by='종목코드').reset_index(drop=True)
        common_pdf = common_pdf.sort_values(by='종목코드').reset_index(drop=True)
        cols = ['종가', '시가', '고가', '저가']
        for c in cols:
            common_df[c] = common_pdf['종가']
        common_df['전일대비'] = 0
        common_df['변동률'] = '0'
        common_df['거래량'] = 0
        common_df['거래대금'] = 0
        common_df['시가총액'] = common_pdf['시가총액']
        common_df['상장주식수'] = common_pdf['상장주식수']
        # 신규상장 종목들에 대한 처리가 필요함.
        for s in new_symbols:
            row = new_df[new_df['종목코드'] == s].iloc[0]
            try:
                stock_info = pd.Series(fetch_acc_stock_info_from_naver_as_dict(s))
            except Exception as e:
                logger.error(f"신규상장 종목의 정보를 읽는데 실패함. {s}/{row['종목명']}: {e}")
                # 신규상장 종목의 경우, 가격정보가 없을 수 있으므로, 빈 칼럼으로 처리
                stock_info = pd.Series({
                    '종목명': row['종목명'], '현재가': 0, '시가': 0, '고가': 0, '저가': 0,
                    '전일대비': 0, '변동률': 0, '거래량': 0, '거래대금': 0,
                    '시가총액': 0, '상장주식수': 0,
                })
            new_df.loc[new_df['종목코드']==s, ['종목명', '종가', '시가', '고가', '저가', '전일대비', '변동률', '거래량', '거래대금', '시가총액', '상장주식수']] = stock_info[
                ['종목명', '현재가', '시가', '고가', '저가', '전일대비', '변동률', '거래량', '거래대금', '시가총액', '상장주식수']].to_numpy()
            # new_df.loc[new_df['종목코드']==s, '변동률'] = stock_info['변동률']
        # 1️⃣ common_df와 new_df 합치기
        merged_df = pd.concat([common_df, new_df], ignore_index=True)
        # 2️⃣ 종목코드 순서 지정 (tsymbols 기준)
        merged_df['종목코드'] = pd.Categorical(merged_df['종목코드'], categories=tsymbols, ordered=True)
        # 3️⃣ 종목코드 기준으로 정렬
        merged_df = merged_df.sort_values('종목코드').reset_index(drop=True)
        df = merged_df
    # 가격에 해당하는 칼럼들을 int64로 변환
    price_columns = ['종가', '전일대비', '시가', '고가', '저가', '거래량', '거래대금', '시가총액', '상장주식수']
    try:
        for col in price_columns:
            df[col] = df[col].astype('int64')
        df['기준가'] = df['종가'] - df['전일대비']
    except ValueError as e:
        # logger.error(f"Error: {e} while converting price columns to int64") 
        raise Exception(f"Error: {e} while converting price columns to int64")
        # 변환 중 오류가 발생(개장하지 않는 날)하면 빈 DataFrame 반환
        # return pd.DataFrame(columns=col_new_names)
    
    # 변동률 칼럼을 float로 변환하고 100으로 나누기
    df['변동률'] = df['변동률'].astype('float64') / 100
    # 일자는 pd.Timestamp로 통일시키기
    df['일자'] = pd.to_datetime(date).normalize()
    # df['일자'] = date.strftime('%Y-%m-%d')
    res_df = df[['일자']+[col for col in df.columns if col != '일자']]
    
    return res_df

def test_krx():
    import datetime
    df = fetch_daily_stock_prices_from_krx(datetime.datetime.today().date())
    print(df)

def test():
    df = fetch_daily_stock_prices_from_krx(pd.Timestamp.today())
    return df

if __name__ == '__main__':
    from mystockutil.df.format import myprint as print
    df = test()
    print(df)
    print(f"Finished")