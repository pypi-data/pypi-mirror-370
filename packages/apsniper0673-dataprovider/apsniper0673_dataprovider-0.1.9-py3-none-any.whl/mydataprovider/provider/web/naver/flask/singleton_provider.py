# ndf_provider.py
from threading import Lock
from mydatahandler.handler.stock_data_handler import StockDataHandler
from mydataprovider.provider.web.naver.flask.naver_data_fetcher import NaverDataFetcher

class SingletonProvider:
    """
    NaverDataFetcher와 관련된 모든 로직(생성, 업데이트, 락 관리)을
    처리하는 싱글톤 클래스.
    """
    def __init__(self):
        print("Initializing NdfProvider singleton...")
        self._ndf:NaverDataFetcher = None
        self.reboot()  # 클래스 생성 시 초기 설정을 위해 reboot 호출

    def reboot(self):
        """
        NaverDataFetcher 인스턴스를 초기화하거나 재시작합니다.
        모든 작업은 스레드에 안전하게 락 내부에서 수행됩니다.
        """
        print("Rebooting NDF instance...")
        self._ndf = NaverDataFetcher()
        self._ndf.ready()
        print("NDF instance is ready.")

    def _update(self):
        """내부적으로 기본 데이터프레임을 업데이트합니다."""
        print("Starting main data update...")
        self._ndf._update()
        print("Main data update finished.")

    def _update_acc(self):
        """내부적으로 정확한 데이터프레임을 업데이트합니다."""
        print("Starting accurate data update...")
        self._ndf._update_acc()
        print("Accurate data update finished.")

    def get_df(self):
        """스레드에 안전하게 기본 데이터프레임의 복사본을 반환합니다."""
        return self._ndf.df.copy()

    def get_acc_symbols(self):
        """스레드에 안전하게 정확한 종목 심볼 리스트의 복사본을 반환합니다."""
        # 리스트도 복사본을 반환하여 외부에서 원본을 변경하는 것을 방지
        return self._ndf.acc_symbols[:]

    def fetch_acc_df_for_symbols(self, symbols: list):
        """
        '/fetch_acc' 라우트의 로직 전체를 캡슐화한 메서드.
        심볼을 acc_list에 추가하고 데이터를 가져오는 과정을 모두 처리합니다.
        """
        # 1. 새로운 심볼을 확인하고 추가
        current_acc_symbols = self._ndf.acc_symbols
        new_symbols = [sym for sym in symbols if sym not in current_acc_symbols]
        for sym in new_symbols:
            self._ndf.add_symbol_in_acc(sym)

        # 2. 데이터 핸들러를 사용하여 데이터 추출
        dh = StockDataHandler(df=self._ndf.acc_df)
        return dh.by_symbols(symbols)

# --- 여기가 핵심 ---
# 모듈이 로드될 때 단 한 번 실행되어, 공유될 단일 인스턴스를 생성합니다.
stp = SingletonProvider()