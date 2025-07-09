# import sys
# sys.stdout.reconfigure(encoding='utf-8')
# import subprocess
# import time

# def send_sms(phone, message):
#     print(f"📨 {phone}에게 문자 전송 중...")

#     # 1. 문자 작성창 열기
#     subprocess.run(f'adb shell "am start -a android.intent.action.SENDTO -d sms:{phone} --es sms_body \'{message}\' --ez exit_on_sent true"', shell=True)

#     # 2. 앱 로딩 시간 대기 (필요 시 늘려도 됨)
#     time.sleep(2)

#     # 3. 키보드 내리기 (KEYCODE_BACK)
#     subprocess.run("adb shell input keyevent 4", shell=True)  # 4번은 BACK 키
#     time.sleep(1)


#     # 4. 전송 버튼 클릭 (확정된 좌표 사용!)
#     subprocess.run("adb shell input tap 987 2216", shell=True)
#     subprocess.run("adb shell input tap 1010 2214", shell=True)

# # 예시 실행
# send_sms("01083001507", "테스트 문자입니다! Python + ADB로 전송 완료 🎉")

import sys
import subprocess
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import urllib.parse

# ───────────────────────────────────────────────────────
# PyInstaller single‐file 번들링 시 JSON 위치를 잡아주는 코드
if getattr(sys, "frozen", False):
    # EXE로 묶였을 때, 리소스가 풀리는 임시 폴더
    BASE_DIR = sys._MEIPASS
else:
    # 개발 환경(스크립트)으로 실행될 때
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# JSON 키 파일 이름이 바뀌지 않았다면 그대로 사용
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "remind-465308-53c5d289ad3b.json")
# ───────────────────────────────────────────────────────

sys.stdout.reconfigure(encoding='utf-8')

def send_sms(phone, message):
    print(f"📨 {phone}에게 문자 전송 중...\n{message}\n")

    # 1) 메시지 URL-인코딩
    encoded = urllib.parse.quote(message, safe='')

    # 2) 문자작성창 열기 (smsto URI)
    subprocess.run(
        f'adb shell am start -a android.intent.action.SENDTO -d "smsto:{phone}?body={encoded}"',
        shell=True
    )
    time.sleep(2)

    # 3) 키보드 내리기
    subprocess.run("adb shell input keyevent 111", shell=True)
    time.sleep(1)

    # 4) 전송 버튼 클릭
    subprocess.run("adb shell input tap 1010 2214", shell=True)
    print("✅ 전송 완료!\n")



# JSON 키 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "remind-465308-53c5d289ad3b.json")

# 구글 시트 연동
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key("1vmxctnMO7gZfe9_3ZcuaX8peOGvHIo0TAl8DS4wVZqU").sheet1
rows = sheet.get_all_values()[1:]

for row in rows:
    name = row[0].strip()
    phone = row[1].replace("-", "").strip()
    field = row[2].strip()
    lawyer = row[3].strip() if row[3].strip() else "테헤란"
    body_template = row[4].strip()

    message = body_template \
        .replace("{이름}", name) \
        .replace("{연락처}", phone) \
        .replace("{분야}", field) \
        .replace("{변리사}", lawyer)

    send_sms(phone, message)
    time.sleep(2)





