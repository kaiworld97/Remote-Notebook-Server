"""
입력 시뮬레이션 모듈 - 키보드와 마우스 입력을 시뮬레이션하는 기능
"""
import pyautogui
from key_codes import get_key_mapping, parse_mouse_move_command, MouseCommands

class InputSimulator:
    def __init__(self):
        # 마우스 속도 팩터 설정
        self.mouse_speed_factors = {1: 5, 2: 15, 3: 30}  # 속도 레벨별 픽셀 이동량
    
    def simulate_key_press(self, key_str):
        """
        키를 누르는 동작 시뮬레이션 (KeyDown만 수행)
        """
        try:
            # 키코드 모듈을 사용하여 매핑 가져오기
            key_mapping = get_key_mapping(key_str)
            
            # 조합키 처리 (튜플로 반환됨)
            if isinstance(key_mapping, tuple):
                modifier, key = key_mapping
                pyautogui.keyDown(modifier)
                pyautogui.keyDown(key)
                # 조합키는 즉시 복구 (이것은 설계 결정에 따라 변경 가능)
                pyautogui.keyUp(key)
                pyautogui.keyUp(modifier)
                print(f"Simulated key combo: {modifier}+{key}")
                return f"Key combo {key_str} pressed"
            
            # 일반 키
            pyautogui.keyDown(key_mapping)
            print(f"Simulated key down: {key_mapping}")
            return f"Key {key_str} pressed"
        except Exception as ex:
            print(f"Error simulating key press: {ex}")
            return f"Error: Cannot press key {key_str}"

    def simulate_key_release(self, key_str):
        """
        키를 떼는 동작 시뮬레이션 (KeyUp만 수행)
        """
        try:
            # 조합키는 이미 simulate_key_press에서 처리됨
            if '+' in key_str:
                return f"Key combo {key_str} released"
            
            # 키코드 모듈을 사용하여 매핑 가져오기
            key_mapping = get_key_mapping(key_str)
            
            # 일반 키
            pyautogui.keyUp(key_mapping)
            print(f"Simulated key up: {key_mapping}")
            return f"Key {key_str} released"
        except Exception as ex:
            print(f"Error simulating key release: {ex}")
            return f"Error: Cannot release key {key_str}"

    def handle_mouse_action(self, command):
        """
        마우스 관련 명령 처리
        """
        # 클릭 관련 명령
        if command == MouseCommands.LEFT_CLICK:
            pyautogui.click(button='left')
            return "Mouse left clicked"
        elif command == MouseCommands.RIGHT_CLICK:
            pyautogui.click(button='right')
            return "Mouse right clicked"
        elif command == MouseCommands.MIDDLE_CLICK:
            pyautogui.click(button='middle')
            return "Mouse middle clicked"
        elif command == MouseCommands.DOUBLE_CLICK:
            pyautogui.doubleClick()
            return "Mouse double clicked"
        
        # 스크롤 관련 명령 (개별 명령으로 처리하는 경우)
        elif command.startswith("MOUSE_SCROLL_UP"):
            parts = command.split("_")
            speed_level = int(parts[-1]) if len(parts) > 3 and parts[-1].isdigit() else 1
            pyautogui.scroll(speed_level * 5)  # 위로 스크롤
            return f"Mouse scrolled up at speed {speed_level}"
        elif command.startswith("MOUSE_SCROLL_DOWN"):
            parts = command.split("_")
            speed_level = int(parts[-1]) if len(parts) > 3 and parts[-1].isdigit() else 1
            pyautogui.scroll(-speed_level * 5)  # 아래로 스크롤
            return f"Mouse scrolled down at speed {speed_level}"
        elif command == "MOUSE_SCROLL_STOP":
            return "Mouse scroll stopped"
        
        # 마우스 이동 명령
        elif command.startswith(MouseCommands.MOVE_PREFIX):
            # 키코드 모듈의 함수를 사용하여 방향과 속도 파싱
            direction, speed_level = parse_mouse_move_command(command)
            
            if not direction:
                return f"Invalid mouse move command: {command}"
            
            # 속도 인자 결정
            speed = self.mouse_speed_factors.get(speed_level, 10)
            
            # 각 방향별 이동량 계산
            dx, dy = 0, 0
            if "UP" in direction:
                dy = -speed
            if "DOWN" in direction:
                dy = speed
            if "LEFT" in direction:
                dx = -speed
            if "RIGHT" in direction:
                dx = speed
            
            # 마우스 이동
            pyautogui.moveRel(dx, dy)
            return f"Mouse moved {direction} at speed {speed_level}"
        
        return f"Unknown mouse command: {command}"

    def handle_scroll_action(self, speed):
        """
        스크롤 액션 처리
        
        Args:
            speed (int): 스크롤 속도 및 방향 (-3~+3)
        """
        if speed == 0:
            return "Scroll stopped"
        
        # 스크롤 방향 결정 (양수: 아래로, 음수: 위로)
        direction = -1 if speed < 0 else 1
        
        # 속도 레벨에 따른 스크롤 양 결정
        scroll_amount = abs(speed) * 3  # 속도 레벨 당 3픽셀 스크롤
        
        # pyautogui를 사용하여 스크롤 적용
        pyautogui.scroll(direction * scroll_amount)
        
        return f"Scrolled {'up' if direction < 0 else 'down'} at speed {abs(speed)}" 