# 보편적 Library
import pandas as pd
import datetime

# User Defined Library
from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(original_logger, {'prefix': 'ODI'})

"""
Opening Day Information (ODI) 관리 클래스
"""

# Essential Imports
import exchange_calendars as ecal

# Essential User Defined Imports
from mydataprovider.table.tm_odi import TM_ODI
from mydataprovider.frame.odi.odi_functions import get_offset_value_with_target

class _ODI():
    def __init__(self) -> None:
        super().__init__()
        
        self.tm = TM_ODI() # ODI 테이블을 관리하는 클래스       
        
        # 개장일에 대한 정보를 저장하는 DataFrame
        # index: date, columns: '개장여부', 'raw', 'ppd'
        # index는 pd.Timestamp로 사용, 오름차순 정렬
        self.df:pd.DataFrame = pd.DataFrame()
        
class ODI_data_ready(_ODI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        # 장시작 후 실시간 데이터 수집 가능 시간
        self.krx_realtime_data_ready_time = datetime.time(hour=9, minute=20)  # KRX 개장 후 20분 후
        self.nxt_realtime_data_ready_time = datetime.time(hour=8, minute=20)  # NXT 개장 후 20분 후

        # KRX와 NXT의 기준시간 데이터
        self.krx_final_data_ready_time = datetime.time(hour=18, minute=30)  # KRX 폐장 후 30분 후
        self.nxt_final_data_ready_time = datetime.time(hour=20, minute=10)  # NXT 폐장 후 30분 후

    def is_krx_realtime_data_ready(self) -> bool:
        """현재 시간이 KRX 실시간 데이터 수집 가능 시간인지 확인
        휴장일인 경우에는 True를 반환한다."""
        if not self.today_is_openday:
            return True
        else:
            return pd.Timestamp.now().time() >= self.krx_realtime_data_ready_time
    def is_nxt_realtime_data_ready(self) -> bool:
        """현재 시간이 NXT 실시간 데이터 수집 가능 시간인지 확인
        휴장일인 경우에는 True를 반환한다."""
        if not self.today_is_openday:
            return True
        else:
            return pd.Timestamp.now().time() >= self.nxt_realtime_data_ready_time            
    def is_today_krx_final_data_ready(self) -> bool:
        if not self.today_is_openday:
            return True
        else:
            return pd.Timestamp.now().time() >= self.krx_final_data_ready_time
    def is_today_nxt_final_data_ready(self) -> bool:
        if not self.today_is_openday:
            return True
        else:
            return pd.Timestamp.now().time() >= self.nxt_final_data_ready_time
    @property
    def today_is_openday(self)-> bool:
        today:pd.Timestamp = pd.Timestamp.today().normalize()
        if today in self.df.index:
            # index에 있으면 그 값을 리턴
            return self.df.loc[[today]]['개장여부'].iloc[0]
            # return self.df.loc[today]['개장여부']
        else:
            raise ValueError("Today's data is not in the DataFrame.")
    @property
    def today_is_holiday(self) -> bool:
        return not self.today_is_openday
    @property
    def today(self) -> pd.Timestamp:
        return pd.Timestamp.today().normalize()
    @property
    def yesterday(self) -> pd.Timestamp:
        return pd.Timestamp.today().normalize() - pd.Timedelta(1, unit='D')
    @property
    def tomorrow(self) -> pd.Timestamp:
        return pd.Timestamp.today().normalize() + pd.Timedelta(1, unit='D')


class ODI_with_df(ODI_data_ready):
    # 금일 주위의 데이터를 보여줌 
    def get_recent_days_df(self, past_days:int = 10, forward_days:int=10) -> pd.DataFrame:
        """금일을 기준으로 최근 days일의 ODI DataFrame을 반환한다."""
        start_date = self.today - pd.Timedelta(past_days, unit='D')
        end_date = self.today + pd.Timedelta(forward_days, unit='D')
        return self.df[(self.df.index >= start_date) & (self.df.index <= end_date)]
    @property
    def df_recent(self) -> pd.DataFrame:
        """금일을 포함한 최근 ODI DataFrame을 반환한다."""
        days = 5
        return self.get_recent_days_df(days, days)
    @property
    def df_past_recent(self) -> pd.DataFrame:
        """금일을 포함한 최근 ODI DataFrame을 반환한다."""
        days = 5
        return self.get_recent_days_df(days, 0)
    @property
    def df_future_recent(self) -> pd.DataFrame:
        """금일을 포함한 최근 ODI DataFrame을 반환한다."""
        days = 5
        return self.get_recent_days_df(0, days)
    @property
    def df_on(self):
        return self.df[self.df['개장여부']==True]
    @property
    def df_off(self):
        return self.df[self.df['개장여부']==False]
    @property
    def days(self):
        return self.df.index
    @property
    def ondays(self):
        return self.df_on.index
    @property
    def offdays(self):
        return self.df_off.index


class ODI_with_TM(ODI_with_df):
    def fetch_whole(self):
        self.df = self.tm.fetch_whole()
            
    def add_onday(self, date: datetime.date):
        """특정일을 개장일로 추가한다."""
        date = pd.to_datetime(date).normalize()
        self._add_date(date, is_open=True)
        
    def add_offday(self, date: datetime.date):
        """특정일을 휴일로 추가한다."""
        date = pd.to_datetime(date)
        self._add_date(date, is_open=False)

    def _add_date(self, date: pd.Timestamp, is_open: bool):
        """특정일을 개장일 또는 휴일로 추가한다.
        is_open이 True인 경우 개장일로, False인 경우 휴일로 추가한다.
        """
        date = pd.to_datetime(date).normalize()
        if date not in self.df.index:
            # 필요한 컬럼만 지정해서 안전하게 추가
            new_row = pd.Series({
                    '일자': date,
                    '개장여부': is_open,
                    '개장시간': pd.Timedelta(hours=9),
                    '폐장시간': pd.Timedelta(hours=15, minutes=30)
                }, name=date)
            index_name = self.df.index.name
            self.df = pd.concat([self.df, new_row.to_frame().T])
            self.df.index.name = index_name  # 또는 '일자'
        else:
            self.df.loc[date, '개장여부'] = True
        self.df.sort_index(inplace=True)
        self._post_date(date)
        
    def _post_date(self, date: datetime.date):
        """특정일을 DB에 업데이트한다."""
        date = pd.to_datetime(date).normalize()
        df = self.df.loc[date:date, :]
        self.tm.post_df(df)


class ODI_premaker(ODI_with_TM):
    def make_base_odi_in_year(self, year:int):
        # 먼저 해당 연도에서 df에 없는 모든 날짜를 추가한다. 
        # 그 후, 토/일 공휴일을 추가한다.
        # krx에서 추가적인 공휴일을 추가한다. 
        
        xkrx = ecal.get_calendar('XKRX')
        
        all_days = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq='D')
        open_days = xkrx.schedule.loc[f'{year}-01-01':f'{year}-12-31']
        # Fixme: 작동 하는지 확인 필요
        open_days = open_days.index.normalize()
        off_days = all_days.difference(open_days)
        
        # 이미 checked된 날짜는 제외한다.
        days_in_df = self.df.index[(self.df.index >= pd.Timestamp(f"{year}-01-01")) & (self.df.index <= pd.Timestamp(f"{year}-12-31"))]
        subset = self.df.loc[days_in_df]
        filtered_subset = subset[subset['checked']]
        days_in_df = filtered_subset.index
        days_not_in_df = all_days.difference(days_in_df)
        for d in days_not_in_df:
            if d in open_days:
                self.add_onday(d)
            elif d in off_days:
                self.add_offday(d)
            else:
                raise ValueError(f"Date {d} is not in open_days or off_days.")


class ODI_base_calculation(ODI_premaker):
    # 인접날짜 조회
    def get_next_day(self, date: pd.Timestamp=None, offset:int=1):
        """date로부터 offset만큼 떨어진 날짜를 반환"""
        date = pd.to_datetime(date).normalize() if date is not None else pd.Timestamp.today().normalize()
        return date+pd.Timedelta(offset, unit='D')
    
    def get_next_open_day(self, date: pd.Timestamp, offset:int=1):
        """date로부터 offset만큼 떨어진 개장일을 반환
        offset이 0이 아닌 경우, 해당 날짜가 개장일 여부는 상관 없음
        """
        # 이 경우, offset이 양수인지, 음수인지에 따라 처리가 달라진다.
        date = pd.to_datetime(date).normalize()
        # offset이 0인 경우, 해당 날짜가 개장일인지 확인
        if offset == 0:
            if date in self.ondays:
                return date
            else:
                # offset이 0인데 개장일이 아닌 경우 에러 발생
                raise ValueError(f"{date} is not an open day.")
        return get_offset_value_with_target(self.ondays, date, offset)
    
    def get_next_off_day(self, date: datetime.date, offset:int=1):
        """date로부터 offset만큼 떨어진 휴일을 반환
        offset이 0이 아닌 경우, 해당 날짜가 개장일 여부는 상관 없음
        """
        date = pd.to_datetime(date).normalize()
        if offset == 0:
            if date in self.offdays:
                return date
            else:
                raise ValueError(f"{date} is not an off day.")
        date = pd.to_datetime(date)
        return get_offset_value_with_target(self.offdays, date, offset)   

    def get_prev_day(self, date: pd.Timestamp, offset:int=1) -> pd.Timestamp:
        """date로부터 offset만큼 떨어진 이전 날짜를 반환"""
        return self.get_next_day(date, -offset)
    def get_prev_open_day(self, date: pd.Timestamp, offset:int=1) -> pd.Timestamp:
        """date로부터 개장일 중 offset만큼 떨어진 이전 개장일을 반환"""
        return self.get_next_open_day(date, -offset)
    def get_prev_off_day(self, date: pd.Timestamp, offset:int=1) -> pd.Timestamp:
        """date로부터 휴일 중 offset만큼 떨어진 이전 휴일을 반환"""
        return self.get_next_off_day(date, -offset)


class ODI_calculation(ODI_base_calculation):
    """
    ODI를 계산하는 클래스
    ---- ODI 조회 ----
    next_day, next_open_day, next_off_day 메쏘드는 자동으로 금일기준으로 조회. offset 사용 가능 
        Fixme: 미래시점의 경우, DB에 없는 경우 처리가 필요.
    get_next_day, get_next_open_day, get_next_off_day 메쏘드의 경우 특정일을 기준으로 사용할 수 있다. 
    """
    @property
    def next_day(self):
        """오늘 기준으로 다음 날을 반환한다."""
        return self.get_next_day(pd.Timestamp.today().normalize())
    @property
    def next_open_day(self):
        """오늘 기준으로 다음 개장일을 반환한다."""
        return self.get_next_open_day(pd.Timestamp.today().normalize())
    @property
    def next_off_day(self):
        """오늘 기준으로 다음 휴일을 반환한다."""
        return self.get_next_off_day(pd.Timestamp.today().normalize())
    @property
    def prev_day(self):
        """오늘 기준으로 이전 날을 반환한다."""
        return self.get_next_day(pd.Timestamp.today().normalize(), -1)
    @property
    def prev_open_day(self):
        """오늘 기준으로 이전 개장일을 반환한다."""
        return self.get_next_open_day(pd.Timestamp.today().normalize(), -1)
    @property
    def recent_open_day(self):
        """금일 포함 최근 개장일을 반환한다."""
        if self.today_is_openday:
            return self.today
        return self.recent_open_day_except_today
    @property
    def recent_open_day_except_today(self):
        """오늘을 제외한 최근 개장일을 반환한다."""
        return self.get_prev_open_day(self.today)
    @property
    def second_recent_open_day(self):
        """금일 포함 두번째로 최근 개장일을 반환한다.
        즉, 오늘이 개장일인 경우, 이전 개장일을 반환하고, 
        오늘이 휴일인 경우, 전전 개장일을 반환한다.
        """
        if self.today_is_openday:
            return self.get_prev_open_day(self.today)
        return self.get_prev_open_day(self.today, 2)
    
    # 최근 개장일 인덱스 반환
    def get_recent_open_days_index(self, past_days:int=5, forward_days:int=5):
        """금일을 기준으로 최근 개장일의 인덱스를 반환한다.
        past_days: 과거 개장일 수
        forward_days: 미래 개장일 수
        """
        past = self.ondays[self.ondays <= self.today][-past_days:]  # 과거 개장일
        forward = self.ondays[self.ondays > self.today][:forward_days]
        return past.append(forward).sort_values()
    def get_recent_past_open_days_index(self, past_days:int=5):
        """금일을 포함한 최근 과거 개장일의 인덱스를 반환한다.
        past_days: 과거 개장일 수
        """
        return self.get_recent_open_days_index(past_days, 0)
    @property
    def recent_open_days_index(self):
        return self.get_recent_open_days_index(5, 5)
    @property
    def recent_past_open_days_index(self):
        return self.get_recent_past_open_days_index(5)
    @property
    def recent_future_open_days_index(self):
        return self.get_recent_open_days_index(0, 5) # 금일 제외 미래 개장일만
    
    # 특정일 개장유무 조회 - 해당일이 index에 없는 경우 에러 발생
    def is_open_day(self, date: datetime.date):
        """특정일이 개장일인지 확인한다."""
        date = pd.to_datetime(date).normalize()
        if date not in self.days:
            raise ValueError(f"{date} is not in the index of ODI DataFrame.")
        return True if date in self.ondays else False
    # 개장일 range 조회
    def get_open_days(self, start_date: pd.Timestamp, end_date: pd.Timestamp):
        """특정 기간 내의 개장일을 반환한다."""
        start_date = pd.to_datetime(start_date).normalize()
        end_date = pd.to_datetime(end_date).normalize()
        return self.ondays[(self.ondays >= start_date) & (self.ondays <= end_date)]


class OpeningDayInformation(ODI_calculation):    
    """
    ODI를 유지하고 사용하는 클래스. 내부적인 작동은 감추도록 한다 > 외부에서 사용하는 함수들에 대해서만 정의할 것
    1. 필요한 기능
    -1. 특정일 추가 - 휴일, 개장일 모두 추가 가능
    -2. 특정일이 개장일인지 확인
    추후
    -3. 특정일의 개장/폐장 시간도 설정 가능
    
    DF의 구조
    - index로 date를 사용. date는 pd.Timestamp
    - columns: '일자', '개장여부', '개장시간', '폐장시간'
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fetch_whole() # ODI DataFrame을 서버에서 가져온다.
        # print(self.df.index)

odi = OpeningDayInformation()

def test_add():
    """ODI에 특정일을 추가하는 테스트"""
    odi.add_onday('2027-01-01')
    
def test_df_recent():
    print("Testing df_recent property...")
    print(odi.df_recent)
    print("Testing df_past_recent property...")
    print(odi.df_past_recent)
    print("Testing df_future_recent property...")
    print(odi.df_future_recent)
    
if __name__ == '__main__':
    print(odi.get_recent_open_days_index())
    print(odi.get_recent_past_open_days_index())
    print("Finished ODI test.")