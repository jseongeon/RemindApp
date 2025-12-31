# 📱 Google Messages 리마인드 발송기

Google Messages를 통해 자동으로 리마인드 문자를 발송하는 데스크톱 애플리케이션입니다.

## ✨ 주요 기능

- 📝 **텍스트 전용 전송**: 텍스트 메시지만 전송
- 🖼️ **이미지 + 텍스트 전송**: 변리사별 이미지와 함께 전송
- 📊 **Google Sheets 연동**: 리마인드 데이터 자동 로드
- 🔄 **자동 재시도**: 전송 실패 시 자동 재시도
- 📈 **전송 로그**: 전송 내역 자동 기록

## 🚀 빠른 시작

### 1. 실행 파일 만들기

```bash
# 방법 1: 간단한 빌드
build_exe.bat

# 방법 2: 배포 패키지 생성 (추천)
create_package.bat
```

### 2. 앱 실행

`배포패키지/GoogleMessages_리마인드발송기.exe` 파일을 더블클릭하세요.

## 📋 사용 방법

### 초기 설정

1. **Chrome 설치**: Google Chrome이 설치되어 있어야 합니다
2. **QR 코드 스캔**: 처음 실행 시 Google Messages QR 코드를 스캔하세요
3. **전송 모드 선택**:
   - 📝 텍스트만 전송
   - 🖼️ 이미지 + 텍스트 전송

### 전송 실행

1. **연결 테스트**: 먼저 연결 테스트를 실행하세요
2. **테스트 전송**: 한 명에게 테스트 전송을 해보세요
3. **전체 전송**: 문제 없으면 전체 리마인드 전송을 실행하세요

## 🖼️ 이미지 설정

`remind image` 폴더에 이미지 파일을 넣으세요:

```
remind image/
  ├── 테헤란.jpg      (변리사별 이미지)
  ├── 홍길동.png      (변리사별 이미지)
  └── 기본.jpg        (기본 이미지)
```

## 📁 프로젝트 구조

```
remind/
├── app/
│   ├── gui_app.py                          # GUI 메인 앱
│   ├── desktop_automation.py               # 텍스트 전용 엔진
│   ├── desktop_automation_with_image.py    # 이미지 포함 엔진
│   └── remind-465308-775406c8a2f1.json    # Google API 인증키
├── build_exe.bat                           # 빌드 스크립트
├── create_package.bat                      # 배포 패키지 생성
├── build_app.spec                          # PyInstaller 설정
└── requirements.txt                        # Python 패키지 목록
```

## 🔧 개발 환경 설정

### 필수 요구사항

- Python 3.8 이상
- Google Chrome
- 인터넷 연결

### 설치

```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 개발 모드로 실행

```bash
# GUI 모드
python app/gui_app.py

# 콘솔 모드 (텍스트 전용)
python app/desktop_automation.py

# 콘솔 모드 (이미지 포함)
python app/desktop_automation_with_image.py
```

## 📦 의존성

- `gspread`: Google Sheets API
- `oauth2client`: Google OAuth 인증
- `selenium`: Chrome 자동화
- `tkinter`: GUI (Python 기본 포함)

## ⚠️ 주의사항

1. **Chrome 브라우저**: Google Messages Web은 Chrome에서만 작동합니다
2. **인터넷 연결**: 안정적인 인터넷 연결이 필요합니다
3. **QR 코드**: 첫 실행 시 QR 코드 스캔이 필요합니다
4. **전송 중 조작 금지**: 문자 전송 중에는 Chrome을 건드리지 마세요

## 🐛 문제 해결

### Chrome 드라이버 오류
- Chrome 브라우저를 최신 버전으로 업데이트하세요

### QR 코드가 나타나지 않음
- Chrome을 완전히 종료하고 다시 시작하세요
- Google Messages에서 로그아웃 후 다시 시도하세요

### 이미지가 전송되지 않음
- `remind image` 폴더 경로를 확인하세요
- 이미지 파일 형식(jpg, png)을 확인하세요


---

© 2024 Jeong Seong Eon. All rights reserved.
