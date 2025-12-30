@echo off
chcp 65001 >nul
echo ======================================
echo Google Messages 리마인드 발송기
echo 실행 파일 생성 중...
echo ======================================
echo.

REM 가상환경 활성화
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo 가상환경을 찾을 수 없습니다. 전역 Python 사용...
)

REM PyInstaller 설치 확인
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller를 설치합니다...
    pip install pyinstaller
)

REM 이전 빌드 정리
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM PyInstaller로 빌드
echo.
echo 빌드 시작...
pyinstaller build_app.spec

if errorlevel 1 (
    echo.
    echo ❌ 빌드 실패!
    pause
    exit /b 1
)

echo.
echo ======================================
echo ✅ 빌드 완료!
echo ======================================
echo.
echo 실행 파일 위치:
echo dist\GoogleMessages_리마인드발송기.exe
echo.
echo 이 파일을 더블클릭하면 앱이 실행됩니다!
echo.
pause
