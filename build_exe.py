"""
exe 빌드 스크립트
PyInstaller를 사용하여 Windows에서 실행 가능한 exe 파일 생성
"""
import PyInstaller.__main__
import os
import shutil
import platform

def build_exe():
    print("원격 키 매퍼 서버 exe 빌드 시작...")
    
    # 빌드 이전에 dist 폴더 삭제
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # 아이콘 경로 설정
    system = platform.system()
    if system == "Windows":
        icon_path = os.path.join("icons", "app_icon.ico")
    elif system == "Darwin":  # macOS
        icon_path = os.path.join("icons", "app_icon.icns")
    else:  # Linux 등
        icon_path = os.path.join("icons", "app_icon.png")
    
    # 아이콘 파일이 존재하는지 확인
    if not os.path.exists(icon_path):
        print(f"경고: {icon_path} 파일이 존재하지 않습니다. 기본 아이콘이 사용됩니다.")
        icon_path = None
    
    # PyInstaller 설정
    pyinstaller_args = [
        'main.py',                          # 메인 스크립트
        '--name=RemoteNotebookServer',     # 출력 파일 이름
        '--onefile',                        # 단일 exe 파일로 생성
        '--windowed',                       # 콘솔 창 없이 실행
        '--add-data=key_codes.py;.',        # 키코드 모듈 포함
        '--add-data=icons/*;icons/',        # 아이콘 폴더 전체 포함
        '--hidden-import=websockets',       # 숨겨진 의존성 포함
        '--hidden-import=pyautogui',
        '--hidden-import=asyncio',
    ]
    
    # 아이콘 경로가 있으면 추가
    if icon_path:
        pyinstaller_args.append(f'--icon={icon_path}')
    
    # 맥OS일 경우 데이터 포맷 변경
    if system == "Darwin":
        # macOS에서는 세미콜론 대신 콜론 사용
        for i, arg in enumerate(pyinstaller_args):
            if arg.startswith('--add-data='):
                pyinstaller_args[i] = arg.replace(';', ':')
    
    # PyInstaller 실행
    PyInstaller.__main__.run(pyinstaller_args)
    
    print("빌드 완료! dist 폴더에서 RemoteKeyMapperServer.exe 파일을 확인하세요.")

if __name__ == "__main__":
    build_exe() 