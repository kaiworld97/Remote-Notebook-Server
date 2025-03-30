"""
키코드 매핑 모듈

이 모듈은 클라이언트의 키코드와 서버의 pyautogui 키코드 간의 매핑을 제공합니다.
클라이언트의 key_codes.dart와 동일한 키코드를 지원합니다.
"""

# 키코드 종류별 매핑 딕셔너리
KEY_MAP = {
    # 알파벳 키 (A-Z)
    'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd', 'E': 'e',
    'F': 'f', 'G': 'g', 'H': 'h', 'I': 'i', 'J': 'j',
    'K': 'k', 'L': 'l', 'M': 'm', 'N': 'n', 'O': 'o',
    'P': 'p', 'Q': 'q', 'R': 'r', 'S': 's', 'T': 't',
    'U': 'u', 'V': 'v', 'W': 'w', 'X': 'x', 'Y': 'y', 'Z': 'z',

    # 숫자 키 (0-9)
    '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
    '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
    
    # 기능 키
    'F1': 'f1', 'F2': 'f2', 'F3': 'f3', 'F4': 'f4', 
    'F5': 'f5', 'F6': 'f6', 'F7': 'f7', 'F8': 'f8',
    'F9': 'f9', 'F10': 'f10', 'F11': 'f11', 'F12': 'f12',
    
    # 특수 키
    'ENTER': 'enter',
    'SPACE': 'space',
    'BACKSPACE': 'backspace',
    'TAB': 'tab',
    'ESCAPE': 'esc',
    'DELETE': 'delete',
    'CAPSLOCK': 'capslock',
    'SHIFT': 'shift',
    'CTRL': 'ctrl',
    'ALT': 'alt',
    'META': 'win',  # Windows 키 / Command 키
    'INS': 'insert',
    'HOME': 'home',
    'END': 'end',
    'PAGEUP': 'pageup',
    'PAGEDOWN': 'pagedown',
    'PRINTSCRN': 'printscreen',
    'SCROLLLOCK': 'scrolllock',
    'PAUSE': 'pause',
    
    # 방향키
    'UP': 'up',
    'DOWN': 'down',
    'LEFT': 'left',
    'RIGHT': 'right',
    
    # 숫자 키패드
    'NUMPAD0': 'num0', 'NUMPAD1': 'num1', 'NUMPAD2': 'num2',
    'NUMPAD3': 'num3', 'NUMPAD4': 'num4', 'NUMPAD5': 'num5',
    'NUMPAD6': 'num6', 'NUMPAD7': 'num7', 'NUMPAD8': 'num8',
    'NUMPAD9': 'num9',
    'NUMLOCK': 'numlock',
    'NUMPAD_ADD': 'add',
    'NUMPAD_SUBTRACT': 'subtract',
    'NUMPAD_MULTIPLY': 'multiply',
    'NUMPAD_DIVIDE': 'divide',
    'NUMPAD_DECIMAL': 'decimal',
    'NUMPAD_ENTER': 'enter',
    
    # 특수 문자 키
    'TILDE': '`',
    'MINUS': '-',
    'EQUALS': '=',
    'BRACKET_LEFT': '[',
    'BRACKET_RIGHT': ']',
    'BACKSLASH': '\\',
    'SEMICOLON': ';',
    'QUOTE': "'",
    'COMMA': ',',
    'PERIOD': '.',
    'SLASH': '/',
}

# 마우스 명령 상수
class MouseCommands:
    LEFT_CLICK = "MOUSE_LEFT"
    RIGHT_CLICK = "MOUSE_RIGHT"
    MIDDLE_CLICK = "MOUSE_MIDDLE"
    DOUBLE_CLICK = "MOUSE_DOUBLE_LEFT"
    FORWARD = "MOUSE_FORWARD"
    BACK = "MOUSE_BACK"
    DRAG = "MOUSE_DRAG"
    SCROLL_UP = "MOUSE_SCROLL_UP"
    SCROLL_DOWN = "MOUSE_SCROLL_DOWN"
    SCROLL_STOP = "MOUSE_SCROLL_STOP"
    MOVE_PREFIX = "MOUSE_MOVE_"

# 키보드 조합키 처리를 위한 도우미 함수
def get_key_mapping(key_str):
    """
    클라이언트 키코드 문자열을 pyautogui 키코드로 변환
    
    Args:
        key_str (str): 클라이언트에서 전송된 키코드
        
    Returns:
        str: pyautogui에서 사용할 키코드 또는 원래 문자열 (매핑이 없는 경우)
    """
    # 이미 소문자인 알파벳은 그대로 사용 (대소문자 구분)
    if len(key_str) == 1 and 'a' <= key_str <= 'z':
        return key_str
        
    # 조합키 처리 (예: CTRL+C)
    if '+' in key_str:
        parts = key_str.split('+')
        if len(parts) == 2:
            modifier = KEY_MAP.get(parts[0].upper(), parts[0].lower())
            key = KEY_MAP.get(parts[1].upper(), parts[1].lower())
            return (modifier, key)  # 튜플로 반환
    
    # 일반 키 매핑
    return KEY_MAP.get(key_str.upper(), key_str.lower())

# 마우스 방향 및 속도 해석 함수
def parse_mouse_move_command(command):
    """
    마우스 이동 명령을 방향과 속도로 해석
    
    Args:
        command (str): MOUSE_MOVE_UP_RIGHT_2 형식의 명령
        
    Returns:
        tuple: (방향 리스트, 속도 레벨) 예: (['UP', 'RIGHT'], 2)
    """
    if not command.startswith(MouseCommands.MOVE_PREFIX):
        return None, 0
        
    parts = command.split("_")
    if len(parts) < 4:
        return None, 0
        
    # 마지막 부분이 숫자인지 확인 (속도 레벨)
    if parts[-1].isdigit():
        speed_level = int(parts[-1])
        direction = parts[2:-1]  # MOUSE_MOVE_UP_RIGHT_2 → ['UP', 'RIGHT']
    else:
        speed_level = 1
        direction = parts[2:]  # MOUSE_MOVE_UP → ['UP']
        
    return direction, speed_level 