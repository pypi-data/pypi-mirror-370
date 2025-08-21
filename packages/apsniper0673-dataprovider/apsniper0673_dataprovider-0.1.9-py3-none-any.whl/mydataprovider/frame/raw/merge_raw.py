import pandas as pd

def merge_raw_dfs(raw_krx:pd.DataFrame, raw_nxt:pd.DataFrame) -> pd.DataFrame:
    """
    raw_krx와 raw_nxt의 df를 병합하여 반환
    Params:
        raw_krx (pd.DataFrame): KRX raw data DataFrame
            index = ['일자', '종목코드']
            columns = ['일자', '종목코드', '표준코드', '종목명', '마켓구분', '관리구분', '종가', '변동코드', '전일대비', '변동률', 
                '시가', '고가', '저가', '거래량', '거래대금', '시가총액', '상장주식수', '시장ID', '기준가']            
        raw_nxt (pd.DataFrame): NXT raw data DataFrame
            index = ['일자', '종목코드']
            columns = ['일자', '종목코드', '표준코드', '종목명', '마켓구분', '종가', '전일대비', '변동률', 
                '시가', '고가', '저가', '거래량', '거래대금', '시장ID']
        Returns:
            pd.DataFrame: 병합된 DataFrame
            1. '시가', '고가', '저가', '종가'는 krx 값을 그대로 쓰고, 
            2. nxt의 '시가', '고가', '저가', '종가'는 _nxt로 변경한다.
            3. '거래량', '거래대금'은 krx + nxt 값을 사용. 
            단, 거래량_krx, 거래량_nxt, 거래대금_krx, 거래대금_nxt 칼럼도 유지
            4. 나머지 칼럼은 krx 값을 그대로 사용.
    """
    if raw_krx.empty and raw_nxt.empty:
        raise ValueError("Both raw_krx and raw_nxt DataFrames are empty.")
    if raw_krx.empty:
        raise ValueError("raw_krx DataFrame is empty.")
    if raw_nxt.empty:
        raise ValueError("raw_nxt DataFrame is empty.")
    raw_krx = normalize_index(raw_krx, duplicate=True)
    raw_nxt = normalize_index(raw_nxt, duplicate=True)
    
    # suffixes 사용하여 공통 컬럼 구분
    merged = raw_krx.merge(
        raw_nxt,
        how='left',
        left_index=True,
        right_index=True,
        suffixes=('', '_nxt')
    )
    # na값을 수정
    merged.fillna({
        '시가_nxt': 0, '고가_nxt': 0, '저가_nxt': 0, '종가_nxt': 0,
        '거래량_nxt': 0, '거래대금_nxt': 0
    }, inplace=True)

    # 거래량/거래대금: 두 값 합산
    for col in ['거래량', '거래대금']:
        # krx값도 유지
        merged[col+'_krx'] = merged[col]
        merged[col] = merged[[col, f'{col}_nxt']].sum(axis=1)

    # 필요 없는 _nxt 접미사 제거 (시가~종가 제외)
    drop_cols = [
        col for col in merged.columns
        if col.endswith('_nxt')
        and not any(col.startswith(prefix) for prefix in ['시가', '고가', '저가', '종가', '거래량', '거래대금'])
    ]
    merged.drop(columns=drop_cols, inplace=True)

    return merged

def normalize_index(df: pd.DataFrame, duplicate:bool=True) -> pd.DataFrame:
    """
    DataFrame의 인덱스를 ['일자', '종목코드']로 설정하고, 정렬한다.
    duplicate가 True인 경우, 인덱스와 중복되는 칼럼을 가지도록 한다.
    Params:
        df (pd.DataFrame): 인덱스를 설정할 DataFrame
    Returns:
        pd.DataFrame: 인덱스가 ['일자', '종목코드']로 설정된 DataFrame
    """
    # 우선 칼럼에 '일자'와 '종목코드'가 있도록 만든다. 
    if set(df.index.names) == {'일자', '종목코드'}:
        df = df[[col for col in df.columns if col not in ['일자', '종목코드']]]
        df.reset_index(drop=False, inplace=True)
    # 인덱스를 ['일자', '종목코드']로 설정한다.
    df.set_index(['일자', '종목코드'], drop=not duplicate, inplace=True)
    return df.sort_index()