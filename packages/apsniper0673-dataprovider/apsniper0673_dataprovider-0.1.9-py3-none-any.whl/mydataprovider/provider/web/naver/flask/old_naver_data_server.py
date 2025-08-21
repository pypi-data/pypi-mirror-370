from flask import Flask, request, jsonify, Response
import pickle
import pandas as pd
from threading import Thread, Lock
import time
from flask_apscheduler import APScheduler

# essential imports
from mydatahandler.handler.stock_data_handler import StockDataHandler
from mydataprovider.provider.web.naver.flask.naver_data_fetcher import ndf, NaverDataFetcher


app = Flask(__name__)
print("Starting NDP server...")
ndf.ready()  # 준비 상태로 설정

# --- 락 생성 (ndf.df 접근 보호용) ---
ndf_lock = Lock()

# --- auto_update를 백그라운드에서 실행 ---
def run_auto_update():
    while True:
        try:
            # with ndf_lock:  # df 업데이트 시 락 걸기
            #     ndf._update()
            ndf._update() # 락 없이 시도
        except Exception as e:
            print(f"Auto update error: {e}")
        time.sleep(20)
        try:
            # with ndf_lock:
            #     ndf._update_acc()
            ndf._update_acc()
        except Exception as e:
            print(f"Auto update acc error: {e}")
        time.sleep(20)

# 백그라운드 스레드 시작
Thread(target=run_auto_update, daemon=True).start()

# --- Routes ---
@app.route('/', methods=['GET'])
def home():
    return "Hello, World! This is NDP server."

"""
fetch_acc:
    symbols에 해당하는 종목들의 정확한 정보를 DataFrame 형태로 반환합니다.
"""
@app.route("/fetch_acc", methods=["POST"])
def fetch_acc():
    symbols = request.json.get("symbols") if request.is_json else None
    if not symbols:
        return jsonify({"error": "symbols parameter is required"}), 400
    try:
        with ndf_lock:  # df 읽기 시에도 락
            acc_symbols = ndf.acc_symbols
            new_symbols = [sym for sym in symbols if sym not in acc_symbols]
            for sym in new_symbols:
                ndf.add_symbol_in_acc(sym)
            dh = StockDataHandler(df=ndf.acc_df)
        df = dh.by_symbols(symbols)
        return Response(
            pickle.dumps(df),
            content_type='application/octet-stream'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

"""
fetch_all:
    모든 종목 정보를 client에 DataFrame 형태로 반환합니다.
    ndf.df: pd.DataFrame - 모든 종목정보를 가진 DataFrame
        index = ['일자', '종목코드']
    
    Args:
        Preview: bool - True인 경우, DataFrame을 JSON 형태로 반환합니다.
"""
@app.route('/fetch_all', methods=['GET'])
def fetch_all():
    preview = request.args.get('preview', 'false').lower() == 'true'
    
    with ndf_lock:  # df 읽기 시 락
        df = ndf.df.copy()
    
    if preview:
        df.reset_index(inplace=True, drop=True)
        df['일자'] = pd.to_datetime(df['일자']).dt.strftime('%Y-%m-%d')
        return Response(
            df.to_html(index=False),
            content_type='text/html; charset=utf-8'
            )
    else:
        return Response(
            pickle.dumps(df),
            content_type='application/octet-stream'
        )

"""
fetch_some:
    symbols 종목 정보를 client에 DataFrame 형태로 반환합니다.
    ndf.df: pd.DataFrame - 모든 종목정보를 가진 DataFrame
        index = ['일자', '종목코드']
"""
@app.route('/fetch_some', methods=['POST'])
def fetch_some():
    # POST JSON body에서 symbols 가져오기
    data = request.get_json()
    symbols = data.get('symbols') if data else None
    
    if not symbols:
        return jsonify({"error": "symbols parameter is required"}), 400
    
    with ndf_lock:  # df 읽기 시 락
        df = ndf.df.copy()
    
    dh = StockDataHandler(df=df)
    df = dh.by_symbols(symbols)  # 여기서 symbols는 리스트여야 함
    
    return Response(
        pickle.dumps(df),
        content_type='application/octet-stream'
    )

"""
get_acc_symbols:
    정확한 종목 정보를 가진 종목들의 리스트를 반환합니다.
"""
@app.route('/get_acc_symbols', methods=['GET'])
def get_acc_symbols():
    with ndf_lock:
        acc_symbols = ndf.acc_symbols
    return jsonify({"acc_symbols": acc_symbols})


def restart_ndf():
    """
    ndf를 재시작합니다.
    """
    global ndf
    print("Rebooting NDF...")
    
    ndf = NaverDataFetcher()
    ndf.ready()
    
    print("NDF rebooted successfully.")

# Flask-APScheduler 설정
class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config)
scheduler = APScheduler()
scheduler.init_app(app)

# 스케줄러 작업 추가
scheduler.add_job(
    id='restart_ndf',
    func=restart_ndf,
    trigger='cron',
    hour=0,
    minute=1
)

# --- 서버 실행 ---
if __name__ == "__main__":
    print("NDP server is running as 'main' code on port 5002...")
    app.run(host="0.0.0.0", port=5002)