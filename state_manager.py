"""
상태 관리 모듈 - 키보드와 마우스의 현재 상태를 관리
"""

class StateManager:
    def __init__(self, input_simulator):
        self.input_simulator = input_simulator
        self.active_keys = set()  # 현재 눌린 키를 추적
        self.is_mouse_active = False  # 마우스 이동 활성화 여부
        self.current_mouse_command = ""  # 현재 실행 중인 마우스 명령
    
    def update_key_state(self, keys, mouse_command, scroll_speed):
        """
        키 및 마우스 상태를 업데이트하고 변경된 상태에 따라 액션 수행
        """
        # 새로 눌린 키 확인 및 처리
        new_keys = set(keys) - self.active_keys
        for key in new_keys:
            self.input_simulator.simulate_key_press(key)
        
        # 뗀 키 확인 및 처리
        released_keys = self.active_keys - set(keys)
        for key in released_keys:
            self.input_simulator.simulate_key_release(key)
        
        # 현재 활성화된 키 업데이트
        self.active_keys = set(keys)
        
        # 마우스 명령 처리
        if mouse_command != self.current_mouse_command:
            if mouse_command:
                self.input_simulator.handle_mouse_action(mouse_command)
                self.is_mouse_active = True
            else:
                self.is_mouse_active = False
            self.current_mouse_command = mouse_command
        
        # 스크롤 처리
        if scroll_speed is not None:
            self.input_simulator.handle_scroll_action(scroll_speed)
        
        return "State updated"
    
    def clear_all_states(self):
        """
        모든 상태 초기화 (연결 종료 시 호출)
        """
        # 모든 키 해제
        for key in self.active_keys:
            self.input_simulator.simulate_key_release(key)
        self.active_keys.clear()
        self.is_mouse_active = False
        self.current_mouse_command = "" 