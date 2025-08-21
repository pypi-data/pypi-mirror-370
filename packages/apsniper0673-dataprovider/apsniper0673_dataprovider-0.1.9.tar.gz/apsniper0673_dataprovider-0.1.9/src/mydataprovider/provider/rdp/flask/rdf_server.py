# public imports
import os
import pickle

from flask import Flask, Response, jsonify, request
from flask_apscheduler import APScheduler
# private imports
from mystockutil.logging.logging_setup import CustomAdapter
from mystockutil.logging.logging_setup import logger as original_logger

logger = CustomAdapter(original_logger, {'prefix': 'rdf_server'})

"""
Data Provider Server
"""

# essential imports
from mydataprovider.frame.odi.df_odi import odi

# from mydataprovider.frame.raw.df_raw import DF_RAW_Recent, DF_RAW_All
# from mydataprovider.frame.ppd.df_ppd import DF_PPD
# from mydataprovider.provider.rdp.rdf.df_rdf import RDF, rdf_recent, rdf_all

# rdf = rdf_recent  # rdf를 rdf_recent로 설정
# rdf = rdf_all # rdf를 rdf_all로 설정

# Main Codes
# Data Loading
logger.info("Starting Data Provider Server...")
logger.info("Loading DataFrames by rdf")
from mydataprovider.provider.rdp.flask.singleton_provider import stp
# rdf.ready()
logger.info("Finished loading DataFrames.")

app = Flask(__name__)

# 홈 페이지
@app.route('/', methods=['GET'])
def home():
    return "Hello, World!, this is the Data Provider Server."

@app.route('/test', methods=['GET'])
def test():
    return "Test endpoint is working!"

# 데이터 요청 API
@app.route('/fetch_df', methods=['POST'])
def fetch_df():
    """
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
    # 패러미터 확인
    if request.is_json:
        req_json = request.get_json()
        start_date = req_json.get('start_date')
        end_date = req_json.get('end_date', None)
    else:
        logger.error('Invalid request method')
        return jsonify({"error": "Invalid request method"}), 400
    
    # 필수 패러미터 검증 (시작날짜만 필수)
    if not all([start_date, end_date]):
        return jsonify({"error": "Missing required parameters: type, start_date"}), 400
    
    rdf = stp.get_rdf()  # SingletonProvider에서 RDF 객체를 가져옴
    filtered_data = rdf.dh.df_from_to(from_date=start_date, to_date=end_date)
    if filtered_data.empty:
        return jsonify({"message": "No data found for the given parameters"}), 404
    
    # Response 객체를 통해 바이너리 데이터를 반환
    return Response(
        pickle.dumps(filtered_data),
        content_type='application/octet-stream'  # 바이너리 데이터 MIME 타입
    )

@app.route('/add_acc', methods=['POST'])
def add_acc():
    """
    symbols를 정확히 측정하는 종목으로 추가한다. 
    """
    if not request.is_json:
        return jsonify({"error": "Invalid request method. Use POST with JSON data."}), 400
    
    req_json = request.get_json()
    symbols = req_json.get('symbols', [])
    if not symbols:
        return jsonify({"error": "Missing required parameter: symbols"}), 400
    rdf = stp.get_rdf()
    added_symbols = rdf.add_acc(symbols)
    return jsonify({
        "message": f"Symbols {added_symbols} added to accurate list.",
        "added_symbols": added_symbols,
        }), 200

# 업데이트 작업 정의
def refresh_rdf():
    # 업데이트 로직 예시 (데이터 재처리 또는 테이블 갱신)
    stp.refresh()  # SingletonProvider의 refresh 메서드를 호출

# 서버 재시작 API
# 모든 인스턴스를 재정의해서 사용
def reboot_rdf():
    """
    RDF를 재시작하는 함수입니다.
    """
    logger.info("Rebooting RDF...")
    stp.reboot()  # SingletonProvider의 reboot 메서드를 호출
    logger.info("RDF rebooted successfully.")

# Flask-APScheduler 설정
class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config)
scheduler = APScheduler()
scheduler.init_app(app)

# 스케줄러 작업 추가
# Refresh RDF 작업
scheduler.add_job(
    id='update_RDF_job',
    func=refresh_rdf,
    trigger='interval',
    seconds=30,  # 30초마다 실행
)

# 서버 재시작 작업
# 일자 업데이트를 위해서 00시 01분에 재실행
# 혹시 모를 업데이트를 위해서 07시 40분에 재실행
scheduler.add_job(
    id='reboot_job1',
    func=reboot_rdf,
    trigger='cron',
    hour=20,
    minute=10
)
scheduler.add_job(
    id='reboot_job2',
    func=reboot_rdf,
    trigger='cron',
    hour=0,
    minute=1
)
scheduler.add_job(
    id='reboot_job3',
    func=reboot_rdf,
    trigger='cron',
    hour=7,
    minute=40
)

# 스케줄러 시작
scheduler.start()

# 서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=False, use_reloader=False)