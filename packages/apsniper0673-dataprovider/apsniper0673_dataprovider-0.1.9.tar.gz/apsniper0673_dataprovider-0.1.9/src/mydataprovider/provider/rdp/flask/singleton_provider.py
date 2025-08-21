# singleton_provider.py

# 필요한 모든 import 구문을 여기에 추가합니다.
from mydataprovider.frame.odi.df_odi import odi
from mydataprovider.frame.raw.df_raw import DF_RAW_Recent
from mydataprovider.frame.ppd.df_ppd import DF_PPD
from mydataprovider.provider.rdp.rdf.df_rdf import RDF
# ... 기타 필요한 import

class SingletonProvider:
    """
    데이터 관련 모든 로직을 처리하는 단일 창구(Facade) 클래스.
    내부적으로 _rdf 객체를 관리합니다.
    """
    def __init__(self):
        print("SingletonProvider 초기화: RDF 객체를 생성합니다.")
        # 내부 변수임을 나타내기 위해 언더스코어(_) 사용
        self._rdf:RDF = None 
        self._initialize_rdf()

    def _initialize_rdf(self):
        """RDF 객체를 생성하고 준비시키는 내부 메서드"""
        raw_recent = DF_RAW_Recent()
        ppd_recent = DF_PPD(raw=raw_recent, base_feather_name='ppd_recent')
        self._rdf = RDF(ppd=ppd_recent)
        self._rdf.ready()
        print("RDF 객체 준비 완료.")

    def get_rdf(self) -> RDF:
        """
        외부에서 안전하게 RDF 객체에 접근할 수 있도록 하는 Getter 메서드.
        """
        return self._rdf

    def refresh(self):
        """RDF 데이터 새로고침"""
        if odi.today_is_holiday:
            print("오늘은 휴일입니다. 데이터 새로고침을 건너뜁니다.")
            return
        print("데이터 새로고침을 요청합니다...")
        self.get_rdf().refresh()
        print("새로고침 완료.")

    def reboot(self):
        """RDF 시스템 재부팅 (내부 _rdf 객체를 새것으로 교체)"""
        print("RDF 재부팅을 시작합니다...")
        self._initialize_rdf() # 초기화 메서드를 다시 호출하여 객체를 교체
        print("RDF 재부팅 완료.")

# --- 여기가 핵심 ---
# 모듈이 로드될 때 단 한 번 실행되어, stp 인스턴스를 생성합니다.
# 다른 모든 파일에서는 이 'stp' 인스턴스를 import하여 사용합니다.
stp = SingletonProvider()