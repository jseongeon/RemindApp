@echo off
chcp 65001 >nul
echo ======================================
echo 배포 패키지 생성 중...
echo ======================================
echo.

REM 먼저 빌드 실행
call build_exe.bat

if errorlevel 1 (
    echo 빌드 실패로 배포 패키지를 생성할 수 없습니다.
    pause
    exit /b 1
)

REM 배포 폴더 생성
set PACKAGE_DIR=배포패키지
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"

REM 실행 파일 복사
echo.
echo 실행 파일 복사 중...
copy "dist\GoogleMessages_리마인드발송기.exe" "%PACKAGE_DIR%\"

REM remind image 폴더 복사 (이미지 파일들)
if exist "remind image" (
    echo 이미지 폴더 복사 중...
    xcopy "remind image" "%PACKAGE_DIR%\remind image\" /E /I /Y
) else (
    echo ⚠️  "remind image" 폴더가 없습니다. 이미지 전송 기능을 사용하려면 이 폴더를 추가하세요.
    mkdir "%PACKAGE_DIR%\remind image"
    echo 이 폴더에 변리사별 이미지 파일을 넣어주세요 (예: 테헤란.jpg, 기본.png) > "%PACKAGE_DIR%\remind image\README.txt"
)

REM 사용 설명서 생성
echo.
echo 사용 설명서 생성 중...
(
echo ======================================
echo Google Messages 리마인드 발송기
echo ======================================
echo.
echo 📌 실행 방법:
echo    GoogleMessages_리마인드발송기.exe 파일을 더블클릭하세요.
echo.
echo 📤 전송 모드:
echo    1. 텍스트만 전송 - 텍스트 메시지만 전송
echo    2. 이미지 + 텍스트 전송 - 변리사별 이미지와 함께 전송
echo.
echo 🖼️  이미지 사용 방법:
echo    - "remind image" 폴더에 이미지 파일을 넣으세요
echo    - 파일명: 변리사이름.jpg (예: 테헤란.jpg, 홍길동.png^)
echo    - 기본 이미지: 기본.jpg 또는 기본.png
echo.
echo 🔧 필수 준비사항:
echo    1. Google Chrome 브라우저 설치
echo    2. Google Messages 웹 버전에서 QR 코드 스캔
echo    3. 인터넷 연결 필수
echo.
echo ⚠️  주의사항:
echo    - 처음 실행 시 QR 코드 스캔이 필요합니다
echo    - 문자 전송 중에는 Chrome을 건드리지 마세요
echo    - 안정적인 인터넷 연결이 필요합니다
echo.
echo 📞 문의:
echo    특허법인 테헤란
echo.
) > "%PACKAGE_DIR%\사용설명서.txt"

echo.
echo ======================================
echo ✅ 배포 패키지 생성 완료!
echo ======================================
echo.
echo 📦 배포 폴더: %PACKAGE_DIR%
echo.
echo 이 폴더를 압축하거나 다른 컴퓨터로 복사하여 사용하세요.
echo.
pause
