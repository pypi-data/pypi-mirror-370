from venv import logger
import numpy as np
import pandas as pd
from typing import List, Tuple

from mystockutil.etc import (
    round_down_price_with_series_kospi_current, 
    round_down_price_with_series_kosdaq_current, 
    round_down_price_with_series_kospi_old, 
    round_down_price_with_series_kosdaq_old, 
    round_up_price_with_series_kospi_current, 
    round_up_price_with_series_kosdaq_current, 
    round_up_price_with_series_kospi_old, 
    round_up_price_with_series_kosdaq_old
)

from mydataprovider.frame.odi.df_odi import odi
from mydataprovider.frame.ppd.ppdps.ppdp_baisc import PPD_Processor

"""
class template(PPD_Processor):
    def custom_init(self):
        self.reading_depth = 0
        self.writing_depth = 0
        self.columns = ['전일종가', '익일기준가']
        self.dtype_mapping = {
            '거래량양수': 'bool'
        }
    # 리턴값은 수정된 데이터프레임입니다.
    def custom_process_new_df(self, df: pd.DataFrame) -> pd.DataFrame:
        # 여기에 처리할 내용을 적어주세요.
        return df
    # 리턴값은 수정된 데이터프레임입니다.
    # custom_process_new_df와 동일한 경우 정의하지 않아도 됩니다. 
    def custom_process_existing_df(self, df: pd.DataFrame) -> pd.DataFrame:
        # 여기에 처리할 내용을 적어주세요.
        return df
    # df를 받아와서 변경된 데이터를 다시 df에 저장합니다.
    # 리턴값은 변경된 df와 서버에 업로드할 df입니다.
    def custom_data_fitting(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        # 여기에 처리할 내용을 적어주세요.
        return pd.DataFrame(), pd.DataFrame()
    # 금일 데이터를 refresh합니다.
    # df를 받아와서 변경된 데이터를 다시 df에 저장합니다.
    def custom_refresh(self, df: pd.DataFrame, today_df: pd.DataFrame)->pd.DataFrame:
        # Returns: refresh된 df
        pass
"""

class adjust_price_processor(PPD_Processor):
    def custom_init(self):
        self.reading_depth = 2
        self.writing_depth = 1
        self.columns = ['전일종가', '익일기준가', '금일가격조정멀티플', '누적가격조정멀티플', 
                        '수정시가', '수정고가', '수정저가', '수정종가', '수정기준가', '수정전일대비', '수정거래량']
        self.dtype_mapping = {
            '거래량양수': 'bool'
        }
    def custom_process_new_df(self, df: pd.DataFrame) -> pd.DataFrame:
        # 분석 전단계 칼럼 생성
        logger.info(f"Adjusting prices for new df...")
        df = df.copy()
        df['전일종가'] = df.groupby(level='종목코드')['종가'].shift(1).fillna(0).astype('int64')
        df['익일기준가'] = df.groupby(level='종목코드')['기준가'].shift(-1).fillna(0).astype('int64')
        
        # 금일가격조정멀티플 계산
        df['금일가격조정멀티플'] = np.where((df['종가'] <= 0) | (df['익일기준가'] <= 0), 1, df['익일기준가'] / df['종가'])
        df['금일가격조정멀티플'] = df['금일가격조정멀티플'].fillna(1)

        # 누적가격조정멀티플 초기화
        df['누적가격조정멀티플'] = 1

        # 누적가격조정멀티플 계산
        df['누적가격조정멀티플'] = df[::-1].groupby(level='종목코드')['금일가격조정멀티플'].cumprod().astype('float64')[::-1]
        
        # 수정종가, 수정거래량 등 계산
        price_cols = ['시가', '고가', '저가', '종가', '기준가']
        for col in price_cols:
            df['수정'+col] = df[col] * df['누적가격조정멀티플']
            df['수정'+col] = df['수정'+col].astype('int64')
        
        df['수정전일대비'] = df['수정종가'] - df['수정기준가']
        df['수정전일대비'] = df['수정전일대비'].astype('int64')
        df['수정거래량'] = df['거래량'] / df['금일가격조정멀티플']
        df['수정거래량'] = df['수정거래량'].astype('int64')
        
        return df
    
    def custom_data_fitting(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        데이터 합치는 기준 날 누적가격조정멀티플이 1이 아닌 경우, 누적가격조정멀티플을 다시 계산한다.
        """
        # 누적멀티플이 1이 아닌 종목코드 추출
        df_filtered = df.loc[df.index.get_level_values('일자') == self.writing_start_date]
        # df_filtered = df.loc[(self.writing_start_date, slice(None)), :]
        cond = df_filtered['누적가격조정멀티플'] != 1
        multiple_changed_symbols = df_filtered[cond].index.get_level_values('종목코드').unique()
        print(f"Multiple changed symbols: {multiple_changed_symbols}")
        
        # 해당 종목에 대해서만 처리
        def adjust_price_with_group(group):
            group = group.sort_index(level='일자', ascending=False).copy()
            group['누적가격조정멀티플'] = group['금일가격조정멀티플'].cumprod()
            group = group.sort_index(level='일자')  # 다시 오름차순 정렬
            
            for col in ['시가', '고가', '저가', '종가', '기준가']:
                group['수정'+col] = group[col] * group['누적가격조정멀티플']
            group['수정전일대비'] = group['수정종가'] - group['수정기준가']
            group['수정거래량'] = group['거래량'] / group['금일가격조정멀티플']
            return group

        df.loc[df.index.get_level_values('종목코드').isin(multiple_changed_symbols)] = (
            df.loc[df.index.get_level_values('종목코드').isin(multiple_changed_symbols)]
            .groupby(level='종목코드', group_keys=False)
            .apply(adjust_price_with_group)
        )
        return df
    
    def custom_data_fitting_old(self, df: pd.DataFrame) -> pd.DataFrame:
        # 해당 날짜 범위의 조건을 생성하고 '누적가격조정멀티플' 값이 1인 경우
        df_filtered = df.loc[(self.writing_start_date, slice(None)), :]
        cond = df_filtered['누적가격조정멀티플'] != 1

        # 조건을 만족하는 종목코드 추출
        multiple_changed_symbols = df_filtered[cond].index.get_level_values('종목코드').unique()
        print(f"Multiple changed symbols: {multiple_changed_symbols}")
        df_changed_list:List[pd.DataFrame] = []
        for symbol in multiple_changed_symbols:
            df_changed = df.loc[(slice(None), symbol), :].copy()
            # 누적가격조정멀티플 계산
            df_changed['누적가격조정멀티플'] = df_changed[::-1].groupby(level='종목코드')['금일가격조정멀티플'].cumprod().astype('float64')[::-1]
            
            # 수정종가, 수정거래량 등 계산
            price_cols = ['시가', '고가', '저가', '종가', '기준가']
            for col in price_cols:
                df_changed['수정'+col] = df_changed[col] * df_changed['누적가격조정멀티플']
            
            df_changed['수정전일대비'] = df_changed['수정종가'] - df_changed['수정기준가']
            df_changed['수정거래량'] = df_changed['거래량'] / df_changed['금일가격조정멀티플']
            
            # 변경사항 저장    
            df.loc[df_changed.index, :] = df_changed
            df_changed_list.append(df_changed)
        return df

    def custom_refresh(self, df: pd.DataFrame, today_df: pd.DataFrame)->pd.DataFrame:
        """Returns: refresh된 df"""
        cols_to_refresh = ['저가', '고가', '종가', '거래량']
        df.loc[today_df.index, cols_to_refresh] = today_df[cols_to_refresh].values
        cols_to_refresh_2 = ['수정'+col for col in cols_to_refresh]
        df.loc[today_df.index, cols_to_refresh_2] = today_df[cols_to_refresh].values
        df.loc[(odi.today, slice(None)), '거래대금'] = df.loc[(odi.today, slice(None)), '수정거래량'].values * df.loc[(odi.today, slice(None)), '수정종가'].values
        return df


        
class cont_trading_days_processor(PPD_Processor):
    def custom_init(self):
        self.reading_depth = 1
        self.writing_depth = 0
        self.columns = ['거래량양수', '연속거래그룹', '연속거래일수']
    # 리턴값은 수정된 데이터프레임입니다.
    def custom_process_new_df(self, df: pd.DataFrame) -> pd.DataFrame:
        print(f"Calculating continuous trading days...")
        df = df.copy()

        # 거래량이 양수인 경우를 표시
        df['거래량양수'] = df['거래량'] > 0

        # 연속거래그룹 계산
        df['연속거래그룹'] = df['거래량양수'].ne(df.groupby(level='종목코드')['거래량양수'].shift()).groupby(level='종목코드').cumsum() - 1 

        # 연속 거래 일수 계산
        df['연속거래일수'] = df.groupby([pd.Grouper(level='종목코드'), '연속거래그룹']).cumcount() + 1
        df.loc[~df['거래량양수'], '연속거래일수'] = 0
        
        return df
    
    # 리턴값은 수정된 데이터프레임입니다.
    def custom_process_existing_df(self, df: pd.DataFrame) -> pd.DataFrame:
        print(f"Calculating continuous trading days...")

        # 거래량이 양수인 경우를 표시
        df['거래량양수'] = df['거래량'] > 0

        # 1. 특정 날짜에 해당하는 종목코드별 '연속거래그룹' 값 추출
        group_value_at_reading_date = df.loc[self.reading_start_date, '연속거래그룹']

        # 2. 연속거래그룹 계산
        df['연속거래그룹'] = df['거래량양수'].ne(df.groupby(level='종목코드')['거래량양수'].shift()).groupby(level='종목코드').cumsum() - 1 

        # 3. 종목코드별로 특정 날짜의 '연속거래그룹' 값을 더해줌
        # 특정 날짜에 해당하는 종목코드가 없는 경우는 NaN이 발생하므로 fillna(0)으로 처리
        df['연속거래그룹'] += df.index.get_level_values('종목코드').map(group_value_at_reading_date).fillna(0)

        # 연속 거래 일수 계산
        # 1. 특정 날짜에 해당하는 종목코드별 '연속거래일수' 값 추출
        ctd_values_at_reading_date = df.loc[self.reading_start_date, '연속거래일수']
        
        # cumcount() 결과값이 0부터 시작함
        df['연속거래일수'] = df.groupby([pd.Grouper(level='종목코드'), '연속거래그룹']).cumcount()
        df['연속거래일수'] += df.index.get_level_values('종목코드').map(ctd_values_at_reading_date).fillna(0)
        df.loc[~df['거래량양수'], '연속거래일수'] = 0
        
        return df
    
    # 금일 데이터를 refresh합니다.
    # df를 받아와서 변경된 데이터를 다시 df에 저장합니다.
    def custom_refresh(self, df: pd.DataFrame, today_df: pd.DataFrame)->pd.DataFrame:
        """Returns: refresh된 df"""
        prev_date = odi.get_prev_open_day(odi.today)
        # 종목코드를 인덱스로 가지는 df 생성
        # tdf에서는 '거래량양수', '연속거래그룹', '연속거래일수' 칼럼이 없다. RAW의 data와 동일하기 때문.
        tdf = today_df.loc[(slice(odi.today),slice(None))]
        tdf.reset_index(drop=False, inplace=True)
        tdf.set_index('종목코드', inplace=True)
        pdf = df.loc[prev_date]
        mdf = tdf.merge(pdf[self.columns], how='left', on='종목코드', suffixes=('', '_prev'))
        mdf['거래량양수'] = mdf['거래량'] > 0
        mdf['연속거래그룹'] = np.where(mdf['거래량양수'], mdf['연속거래그룹'].fillna(1), mdf['연속거래그룹'].fillna(1) +1)
        mdf['연속거래일수'] = np.where(mdf['거래량양수'], mdf['연속거래일수'].fillna(0)+1, 0)
        mdf.reset_index(drop=False, inplace=True)
        mdf.set_index(['일자', '종목코드'], inplace=True)
        df.loc[mdf.index, self.columns] = mdf[self.columns].values
        return df
        
class cal_limit_processor(PPD_Processor):
    def custom_init(self):
        self.reading_depth = 0
        self.writing_depth = 0
        self.columns = ['상한가', '하한가', '종가상한가여부', '종가하한가여부', '시가상한가여부', '시가하한가여부', '종가상하한가', '시가상하한가']
        self.dtype_mapping = {
            '종가상한가여부': 'bool',
            '종가하한가여부': 'bool',
            '시가상한가여부': 'bool',
            '시가하한가여부': 'bool'
        }
    # 리턴값은 수정된 데이터프레임입니다.
    def custom_process_new_df(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Calculating price limits for new df...")
        df = df.copy()
        # 2023-1-25부로 호가단위 변경, 2015-06-15 기준으로 상한가, 하한가 계산
        # Create a timestamp column from the index for vectorized comparison
        dates = df.index.get_level_values(0)
        
        # Apply different conditions based on dates
        condition_new = dates >= pd.Timestamp('2023-01-25')
        condition_mid = (dates >= pd.Timestamp('2015-06-15')) & (dates < pd.Timestamp('2023-01-25'))
        condition_kospi = df['마켓구분'].isin(['Kospi', 'kospi', 'KOSPI', '코스피'])

        # Calculate price limits in a vectorized manner
        df['상한가'] = np.where(
            condition_new, 
            np.where(condition_kospi, round_down_price_with_series_kospi_current(df['기준가'] * 1.3), round_down_price_with_series_kosdaq_current(df['기준가'] * 1.3)
                     ),
            np.where(condition_mid, 
                     np.where(condition_kospi, round_down_price_with_series_kospi_old(df['기준가'] * 1.3), round_down_price_with_series_kosdaq_old(df['기준가'] * 1.3)),
                     np.where(condition_kospi, round_down_price_with_series_kospi_old(df['기준가'] * 1.15), round_down_price_with_series_kosdaq_old(df['기준가'] * 1.15))
                     )
            )
        
        # 하한가를 벡터화 방식으로 계산
        df['하한가'] = np.where(
            condition_new,
            np.where(condition_kospi, round_up_price_with_series_kospi_current(df['기준가'] * 0.7), round_up_price_with_series_kosdaq_current(df['기준가'] * 0.7)),
            np.where(
                condition_mid,
                np.where(condition_kospi, round_up_price_with_series_kospi_old(df['기준가'] * 0.7), round_up_price_with_series_kosdaq_old(df['기준가'] * 0.7)),
                np.where(condition_kospi, round_up_price_with_series_kospi_old(df['기준가'] * 0.85), round_up_price_with_series_kosdaq_old(df['기준가'] * 0.85))
            )
        )

        # 종가와 시가 상한가 및 하한가 여부 확인
        df['종가상한가여부'] = df['종가'] == df['상한가']
        df['종가하한가여부'] = df['종가'] == df['하한가']
        df['시가상한가여부'] = df['시가'] == df['상한가']
        df['시가하한가여부'] = df['시가'] == df['하한가']
        
        # 상하한가 열 설정
        df['종가상하한가'] = np.where(df['종가상한가여부'], '상한가', np.where(df['종가하한가여부'], '하한가', '정상가'))
        df['시가상하한가'] = np.where(df['시가상한가여부'], '상한가', np.where(df['시가하한가여부'], '하한가', '정상가'))
        
        return df

    def custom_refresh(self, df: pd.DataFrame, today_df: pd.DataFrame)->pd.DataFrame:
        """Returns: refresh된 df"""
        df = df.copy()
        today_df = today_df.copy()
        today_df = self.custom_process_new_df(today_df)
        df.loc[today_df.index, self.columns] = today_df[self.columns].values
        return df
        
custom_processors = PPD_Processor.__subclasses__()