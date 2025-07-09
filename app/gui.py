import sys
import os
import threading
import subprocess
import time
import urllib.parse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import PySimpleGUI as sg

# ─────────────────────────────────────────────────────
# PyInstaller one‑dir 번들용 리소스 경로 설정
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "remind-465308-53c5d289ad3b.json")

# GUI 로직

def send_all(window, sheet_key):
    try:
        window['-LOG-'].update("📡 구글 시트 연결 중...\n", append=True)
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_key).sheet1
        rows = sheet.get_all_values()[1:]

        for row in rows:
            name = row[0].strip()
            phone = row[1].replace("-", "").strip()
            field = row[2].strip()
            lawyer = row[3].strip() or "테헤란"
            tpl = row[4].strip()
            msg = tpl.replace("{이름}", name).replace("{분야}", field).replace("{변리사}", lawyer)

            window['-LOG-'].update(f"📨 {phone} 전송: {msg[:20]}...\n", append=True)

            encoded = urllib.parse.quote(msg, safe='')
            subprocess.run(
                f'adb shell am start -a android.intent.action.SENDTO -d "smsto:{phone}?body={encoded}"',
                shell=True
            )
            time.sleep(2)
            subprocess.run("adb shell input keyevent 111", shell=True)
            time.sleep(1)
            subprocess.run("adb shell input tap 1010 2214", shell=True)
            time.sleep(2)
        window['-LOG-'].update("✅ 전체 전송 완료!\n", append=True)
    except Exception as e:
        window['-LOG-'].update(f"❌ 에러: {e}\n", append=True)

# GUI 레이아웃
sg.ChangeLookAndFeel('DarkBlue12')  # sg.theme() 대신 사용
layout = [
    [sg.Text('Google Sheet ID:'), sg.Input(key='-SHEET-')],
    [sg.Button('전송 시작', key='-RUN-'), sg.Button('종료')],
    [sg.Frame('로그', [[sg.Multiline(size=(60,15), key='-LOG-', autoscroll=True, disabled=True)]])]
]

window = sg.Window('SMS 자동 발송기', layout)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, '종료'):
        break
    if event == '-RUN-':
        sheet_key = values['-SHEET-'].strip()
        if not sheet_key:
            sg.popup('시트 ID를 입력하세요.')
            continue
        threading.Thread(target=send_all, args=(window, sheet_key), daemon=True).start()

window.close()
