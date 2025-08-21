# app.py
from flask import Flask, request, jsonify, Response
import pickle
import pandas as pd
from flask_apscheduler import APScheduler

# --- 여기가 핵심 ---
# ndf_provider.py 파일에서 미리 생성된 단일 인스턴스를 가져옵니다.
from mydataprovider.provider.web.naver.flask.singleton_provider import stp
from mydatahandler.handler.stock_data_handler import StockDataHandler


app = Flask(__name__)
print("Starting NDP server...")

# --- Routes (훨씬 간결해진 라우트 함수들) ---
@app.route('/', methods=['GET'])
def home():
    return "Hello, World! This is NDP server."

@app.route("/fetch_acc", methods=["POST"])
def fetch_acc():
    symbols = request.json.get("symbols") if request.is_json else None
    if not symbols:
        return jsonify({"error": "symbols parameter is required"}), 400
    try:
        # 복잡한 로직을 provider 객체에 모두 위임
        df = stp.fetch_acc_df_for_symbols(symbols)
        return Response(
            pickle.dumps(df),
            content_type='application/octet-stream'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/fetch_all', methods=['GET'])
def fetch_all():
    preview = request.args.get('preview', 'false').lower() == 'true'
    
    # provider로부터 스레드에 안전한 데이터프레임 복사본을 가져옴
    df = stp.get_df()
    
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

@app.route('/fetch_some', methods=['POST'])
def fetch_some():
    data = request.get_json()
    symbols = data.get('symbols') if data else None
    
    if not symbols:
        return jsonify({"error": "symbols parameter is required"}), 400
    
    df_all = stp.get_df()
    dh = StockDataHandler(df=df_all)
    df_some = dh.by_symbols(symbols)
    
    return Response(
        pickle.dumps(df_some),
        content_type='application/octet-stream'
    )

@app.route('/get_acc_symbols', methods=['GET'])
def get_acc_symbols():
    acc_symbols = stp.get_acc_symbols()
    return jsonify({"acc_symbols": acc_symbols})


# --- APScheduler 설정 ---
# 별도의 스레드 대신 스케줄러가 백그라운드 업데이트를 모두 담당합니다.
class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config)
scheduler = APScheduler()
scheduler.init_app(app)

# 47초마다 기본 데이터 업데이트 작업 실행
scheduler.add_job(
    id='update_main_data',
    func=stp._update,  # provider의 메서드를 직접 호출
    trigger='interval',
    seconds=47
)

# 31초마다 정확한 데이터 업데이트 작업 실행
scheduler.add_job(
    id='update_acc_data',
    func=stp._update_acc, # provider의 메서드를 직접 호출
    trigger='interval',
    seconds=31,
    misfire_grace_time=10 # 작업이 밀릴 경우를 대비
)

# 매일 자정에 전체 시스템 재시작
scheduler.add_job(
    id='restart_ndf',
    func=stp.reboot,  # provider의 재시작 메서드 호출
    trigger='cron',
    hour=0,
    minute=1
)

scheduler.start()

# --- 서버 실행 ---
if __name__ == "__main__":
    print("NDP server is running as 'main' code on port 5002...")
    # use_reloader=False는 싱글톤 패턴과 스케줄러를 사용할 때 중요합니다.
    app.run(host="0.0.0.0", port=5002, use_reloader=False)
