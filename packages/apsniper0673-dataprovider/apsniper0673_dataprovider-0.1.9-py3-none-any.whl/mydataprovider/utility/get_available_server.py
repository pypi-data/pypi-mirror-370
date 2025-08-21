import requests
from typing import List

server_candidates = [
        'http://brstk.com:5001',
        'http://brstk.iptime.org:5001',
        'http://localhost:5001',
        # 'http://192.168.0.181:5001',  # Silence - Main Computer
    ]

# 사용가능한 서버를 찾는 함수
def get_available_server(server_candidates: List[str], port: int = 5001):
    for url in server_candidates:
        # http/https 붙었는지 확인
        has_scheme = url.startswith("http://") or url.startswith("https://")
        url_body = url.split("//")[-1] if has_scheme else url

        # 포트가 이미 포함되어 있는지 확인
        has_port = ':' in url_body and url_body.rsplit(':', 1)[-1].isdigit()

        if has_scheme:
            full_url = url if has_port else f"{url}:{port}"
        else:
            full_url = f"http://{url}" if has_port else f"http://{url}:{port}"

        try:
            response = requests.get(full_url, timeout=2)
            if response.status_code == 200:
                return full_url
        except requests.exceptions.RequestException:
            continue
    return None