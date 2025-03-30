"""
서버 관리 모듈 - 웹소켓 서버 및 클라이언트 연결 관리
"""
import asyncio
import json
import threading
import websockets
from utils import get_local_ip

class ServerManager:
    def __init__(self, input_simulator, state_manager, port=8765):
        # 의존성 주입
        self.input_simulator = input_simulator
        self.state_manager = state_manager
        
        # 기본 설정
        self.port = port
        self.ip = get_local_ip()
        self.password = "default123"
        
        # 서버 상태 변수
        self.current_client = None
        self.client_lock = threading.Lock()
        self.server_loop = None
        self.running = False
        
        # UI 콜백
        self.gui_callback = None
    
    def set_gui_callback(self, callback):
        """
        GUI 업데이트 콜백 설정
        """
        self.gui_callback = callback
    
    def get_server_info(self):
        """
        서버 연결 정보 반환
        """
        return {
            'ip': self.ip,
            'port': self.port,
            'running': self.running
        }
    
    def get_state_info(self):
        """
        현재 상태 정보 반환
        """
        return {
            'active_keys': self.state_manager.active_keys,
            'is_mouse_active': self.state_manager.is_mouse_active,
            'current_mouse_command': self.state_manager.current_mouse_command
        }
    
    def get_password(self):
        """
        현재 인증 비밀번호 반환
        """
        return self.password
    
    def set_password(self, new_password):
        """
        인증 비밀번호 변경
        """
        self.password = new_password
    
    def disconnect_client(self):
        """
        현재 연결된 클라이언트 연결 종료
        """
        if self.current_client is not None and self.server_loop is not None:
            def close_conn():
                if self.current_client is not None:
                    asyncio.create_task(self.current_client.close())
            self.server_loop.call_soon_threadsafe(close_conn)
            return True
        return False
    
    def is_client_connected(self):
        """
        클라이언트 연결 상태 확인
        """
        return self.current_client is not None
    
    async def handle_client(self, websocket):
        """
        클라이언트 연결 처리
        """
        with self.client_lock:
            if self.current_client is not None:
                await websocket.send("현재 하나의 클라이언트만 허용됩니다. 연결을 종료합니다...")
                await websocket.close()
                return
            self.current_client = websocket

        # GUI 업데이트
        if self.gui_callback:
            self.gui_callback.update_status(f"연결됨: {websocket.remote_address}")
            self.gui_callback.add_log(f"클라이언트 연결됨: {websocket.remote_address}")

        try:
            # 인증: 10초 이내에 AUTH 메시지 받기
            auth_msg = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            if not auth_msg.startswith("AUTH:"):
                await websocket.send("인증이 필요합니다. 연결을 종료합니다.")
                await websocket.close()
                return
            pwd = auth_msg[5:].strip()
            if pwd != self.password:
                await websocket.send("AUTH_FAILED")
                await websocket.close()
                if self.gui_callback:
                    self.gui_callback.add_log(f"클라이언트 인증 실패: {websocket.remote_address}")
                return
            else:
                await websocket.send("AUTH_SUCCESS")
                print("클라이언트 인증됨:", websocket.remote_address)
                if self.gui_callback:
                    self.gui_callback.add_log(f"클라이언트 인증 성공: {websocket.remote_address}")

            # 인증 후 메시지 처리
            async for message in websocket:
                print("수신:", message)
                if self.gui_callback:
                    self.gui_callback.add_log(f"수신: {message[:50]}{'...' if len(message) > 50 else ''}")
                
                # KEY 프로토콜: 단일 키 입력
                if message.startswith("KEY:"):
                    key_value = message[4:].strip()
                    
                    # 마우스 관련 명령인지 확인
                    if key_value.startswith("MOUSE_"):
                        result = self.input_simulator.handle_mouse_action(key_value)
                    else:
                        # 키보드 관련 명령 처리
                        # 단일 키는 누르고 바로 떼는 동작 수행
                        self.input_simulator.simulate_key_press(key_value)
                        self.input_simulator.simulate_key_release(key_value)
                        result = f"Key {key_value} pressed and released"
                    
                    await websocket.send(result)
                
                # STATE 프로토콜: 다중 키 및 마우스 상태 업데이트
                elif message.startswith("STATE:"):
                    try:
                        state_json = message[6:].strip()
                        state_data = json.loads(state_json)
                        
                        keys = state_data.get("keys", [])
                        mouse_command = state_data.get("mouse", None)
                        scroll_speed = state_data.get("scroll", None)
                        
                        result = self.state_manager.update_key_state(keys, mouse_command, scroll_speed)
                        await websocket.send(result)
                    except json.JSONDecodeError:
                        await websocket.send("Error: Invalid JSON in STATE message")
                        if self.gui_callback:
                            self.gui_callback.add_log("오류: STATE 메시지의 JSON 형식이 잘못되었습니다.")
                    except Exception as e:
                        await websocket.send(f"Error processing state: {str(e)}")
                        if self.gui_callback:
                            self.gui_callback.add_log(f"오류: 상태 처리 중 예외 발생: {str(e)}")
                else:
                    await websocket.send("Unknown command")
                    if self.gui_callback:
                        self.gui_callback.add_log(f"알 수 없는 명령: {message}")
        except Exception as e:
            print("예외 발생:", e)
            if self.gui_callback:
                self.gui_callback.add_log(f"예외 발생: {str(e)}")
        finally:
            # 연결 종료 시 모든 상태 초기화
            self.state_manager.clear_all_states()
            
            with self.client_lock:
                self.current_client = None
            if self.gui_callback:
                self.gui_callback.update_status("클라이언트 연결 없음")
                self.gui_callback.add_log(f"연결 종료: {websocket.remote_address}")
            print("연결 종료:", websocket.remote_address)

    async def start_server(self):
        """
        웹소켓 서버 시작
        """
        self.running = True
        server = await websockets.serve(self.handle_client, self.ip, self.port)
        print(f"웹소켓 서버가 {self.ip}:{self.port}에서 시작되었습니다.")
        self.server_loop = asyncio.get_running_loop()
        await server.wait_closed()

    def run_server(self):
        """
        비동기 웹소켓 서버 실행 (별도 스레드에서 호출됨)
        """
        asyncio.run(self.start_server()) 