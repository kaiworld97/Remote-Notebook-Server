"""
GUI 관리 모듈 - Tkinter GUI 관련 기능 구현
"""
import tkinter as tk
import os
import sys
import platform
from tkinter import messagebox

def resource_path(relative_path):
    """
    리소스 파일의 절대 경로를 가져옵니다.
    개발 환경과 PyInstaller로 패키징된 환경 모두에서 작동합니다.
    """
    try:
        # PyInstaller가 생성한 임시 폴더 경로
        base_path = sys._MEIPASS
    except Exception:
        # 개발 환경에서는 현재 디렉토리 사용
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class ServerGUI:
    def __init__(self, master, server_manager):
        self.master = master
        self.server_manager = server_manager
        
        # 창 제목 설정
        master.title("Remote Key Mapper Server")
        
        # 창 아이콘 설정 (OS에 따라 다르게)
        self.set_window_icon(master)
        
        # 서버 정보 표시
        server_info = self.server_manager.get_server_info()
        info_frame = tk.Frame(master)
        info_frame.pack(pady=5, fill=tk.X)
        tk.Label(info_frame, text=f"서버 IP: {server_info['ip']}", font=("Arial", 12)).pack(anchor='w')
        tk.Label(info_frame, text=f"포트: {server_info['port']}", font=("Arial", 12)).pack(anchor='w')

        # 연결 상태 표시
        self.status_label = tk.Label(master, text="클라이언트 연결 없음", font=("Arial", 14))
        self.status_label.pack(pady=10)

        # 연결 관리 버튼
        self.disconnect_button = tk.Button(master, text="클라이언트 연결 끊기", 
                                           command=self.disconnect_client, 
                                           state=tk.DISABLED)
        self.disconnect_button.pack(pady=10)

        # 비밀번호 변경 UI
        self.pwd_frame = tk.Frame(master)
        self.pwd_frame.pack(pady=10)
        tk.Label(self.pwd_frame, text="현재 비밀번호:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
        self.pwd_var = tk.StringVar()
        self.pwd_var.set(self.server_manager.get_password())
        self.pwd_entry = tk.Entry(self.pwd_frame, textvariable=self.pwd_var, show="*")
        self.pwd_entry.grid(row=0, column=1, padx=5)
        self.update_pwd_btn = tk.Button(master, text="비밀번호 업데이트", command=self.update_password)
        self.update_pwd_btn.pack(pady=10)
        
        # 활성 키 상태 표시
        self.key_status_frame = tk.Frame(master)
        self.key_status_frame.pack(pady=10, fill=tk.X)
        tk.Label(self.key_status_frame, text="활성화된 키:", font=("Arial", 12)).pack(anchor='w')
        self.active_keys_var = tk.StringVar()
        self.active_keys_var.set("없음")
        tk.Label(self.key_status_frame, textvariable=self.active_keys_var, font=("Arial", 10)).pack(pady=5)
        
        # 로그 표시
        self.log_frame = tk.Frame(master)
        self.log_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        tk.Label(self.log_frame, text="서버 로그:", font=("Arial", 12)).pack(anchor='w')
        
        self.log_text = tk.Text(self.log_frame, height=10, width=50)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤바 추가
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # 로그 초기화
        self.add_log("서버 시작됨")
        
        # 상태 업데이트 타이머 설정
        self.update_status_display()

    def set_window_icon(self, root):
        """
        운영체제에 따라 창 아이콘을 설정합니다.
        """
        system = platform.system()
        
        try:
            if system == "Windows":
                # Windows에서는 .ico 파일 사용
                icon_path = resource_path(os.path.join("icons", "app_icon.ico"))
                root.iconbitmap(icon_path)
            elif system == "Darwin":  # macOS
                # macOS에서는 .png 파일을 PhotoImage로 설정
                icon_path = resource_path(os.path.join("icons", "app_icon.png"))
                icon = tk.PhotoImage(file=icon_path)
                root.iconphoto(True, icon)
            else:  # Linux 등 기타 OS
                icon_path = resource_path(os.path.join("icons", "app_icon.png"))
                icon = tk.PhotoImage(file=icon_path)
                root.iconphoto(True, icon)
        except Exception as e:
            print(f"아이콘 설정 오류: {e}")

    def update_status(self, status):
        """
        연결 상태 라벨 업데이트
        """
        self.master.after(0, lambda: self._update_status(status))

    def _update_status(self, status):
        """
        실제 상태 업데이트 로직
        """
        self.status_label.config(text=status)
        if status.startswith("연결됨:"):
            self.disconnect_button.config(state=tk.NORMAL)
        else:
            self.disconnect_button.config(state=tk.DISABLED)

    def disconnect_client(self):
        """
        현재 연결된 클라이언트 연결 해제
        """
        if self.server_manager.disconnect_client():
            self.update_status("클라이언트 연결 없음")
            self.add_log("클라이언트 연결 종료")
        else:
            messagebox.showinfo("정보", "연결된 클라이언트가 없습니다.")

    def update_password(self):
        """
        인증 비밀번호 업데이트
        """
        new_pwd = self.pwd_var.get().strip()
        if new_pwd == "":
            messagebox.showwarning("경고", "비밀번호는 비워둘 수 없습니다.")
            return
            
        # 기존 연결 종료
        if self.server_manager.is_client_connected():
            self.server_manager.disconnect_client()
            self.update_status("클라이언트 연결 없음")
            
        # 비밀번호 업데이트
        self.server_manager.set_password(new_pwd)
        messagebox.showinfo("비밀번호 업데이트", f"새 비밀번호 설정: {new_pwd}")
        self.add_log(f"비밀번호가 업데이트되었습니다.")
    
    def update_status_display(self):
        """
        활성 키 상태 표시 업데이트 (주기적으로 호출)
        """
        # 상태 관리자에서 현재 상태 가져오기
        state_info = self.server_manager.get_state_info()
        
        # 활성 키 표시
        keys_text = ", ".join(state_info['active_keys']) if state_info['active_keys'] else "없음"
        status_text = f"키: {keys_text}"
        
        # 마우스 상태 표시
        if state_info['is_mouse_active']:
            mouse_text = f"마우스: {state_info['current_mouse_command']}"
            status_text += f"\n{mouse_text}"
            
        self.active_keys_var.set(status_text)
        
        # 100ms마다 업데이트
        self.master.after(100, self.update_status_display)
    
    def add_log(self, message):
        """
        로그 창에 메시지 추가
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)  # 자동 스크롤 