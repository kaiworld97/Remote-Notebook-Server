"""
원격 키 매퍼 서버 - 메인 모듈
클라이언트에서 전송된 키 및 마우스 입력을 시뮬레이션합니다.
"""
import threading
import tkinter as tk
import os

# 모듈 가져오기
from input_simulator import InputSimulator
from state_manager import StateManager
from server_manager import ServerManager
from gui_manager import ServerGUI

def ensure_icon_directory():
    """아이콘 디렉토리가 존재하는지 확인하고 없으면 생성"""
    icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
    if not os.path.exists(icon_dir):
        os.makedirs(icon_dir)
        print(f"아이콘 디렉토리 생성됨: {icon_dir}")
    return icon_dir

def main():
    print("원격 키 매퍼 서버 시작 중...")
    
    # 아이콘 디렉토리 확인
    icon_dir = ensure_icon_directory()
    print(f"아이콘 디렉토리: {icon_dir}")
    
    # 의존성 생성 및 주입
    input_simulator = InputSimulator()
    state_manager = StateManager(input_simulator)
    server_manager = ServerManager(input_simulator, state_manager)
    
    # 웹소켓 서버 시작 (백그라운드 스레드에서)
    server_thread = threading.Thread(target=server_manager.run_server, daemon=True)
    server_thread.start()
    
    # GUI 시작 (메인 스레드에서)
    root = tk.Tk()
    root.geometry("600x500")  # GUI 창 크기 설정
    gui = ServerGUI(root, server_manager)
    
    # GUI 콜백 등록
    server_manager.set_gui_callback(gui)
    
    # Tkinter 이벤트 루프 시작
    root.mainloop()

if __name__ == "__main__":
    main()
