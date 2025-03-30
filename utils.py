"""
유틸리티 함수 모듈 - 공통으로 사용되는 유틸리티 함수들을 포함
"""
import socket

def get_local_ip():
    """
    현재 머신의 외부 네트워크에 사용할 수 있는 IPv4 주소를 반환합니다.
    (8.8.8.8과 같은 외부 주소에 UDP 소켓 연결을 시도하여 알아냅니다.)
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 실제로 데이터를 보내지는 않으므로 연결만 시도함
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip 