import os
import time
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import sys
import subprocess
import traceback

# 콘솔 인코딩 설정
if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

class GoogleMessagesSender:
    def __init__(self, debug_mode=False):
        # 기본 설정
        if getattr(sys, "frozen", False):
            self.BASE_DIR = sys._MEIPASS
        else:
            self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        self.SERVICE_ACCOUNT_FILE = os.path.join(self.BASE_DIR, "remind-465308-775406c8a2f1.json")
        
        self.debug_mode = debug_mode
        self.debug_port = 9223
        
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.SERVICE_ACCOUNT_FILE, self.scope)
        self.client = gspread.authorize(self.creds)
        self.driver = None
        
        print("📱 Google Messages Sender 초기화 완료 (텍스트 전용 버전)")
        if debug_mode:
            print("🐛 디버그 모드 활성화")

    def debug_print(self, message):
        if self.debug_mode:
            print(f"🐛 DEBUG: {message}")
    
    def check_session(self):
        """Chrome 세션이 유효한지 확인"""
        try:
            # 간단한 명령으로 세션 확인
            self.driver.current_url
            return True
        except Exception as e:
            print(f"❌ Chrome 세션이 끊어졌습니다: {e}")
            return False
    
    def normalize_phone_number(self, phone_number):
        if not phone_number: return ""
        clean_phone = re.sub(r'[^\d]', '', str(phone_number))
        if clean_phone.startswith('82'):
            clean_phone = '0' + clean_phone[2:]
        self.debug_print(f"전화번호 정규화: {phone_number} → {clean_phone}")
        return clean_phone

    def smart_wait_for_element(self, selectors, timeout=10, clickable=False):
        if isinstance(selectors, str): selectors = [selectors]
        for selector in selectors:
            try:
                if clickable:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                else:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                # 성공 시에만 로그 출력
                if self.debug_mode:
                    print(f"✅ 요소 발견: {selector}")
                return element
            except Exception:
                continue
        # 모든 셀렉터 실패 시에만 로그 출력
        if self.debug_mode:
            print(f"❌ 요소를 찾을 수 없음: {selectors}")
        return None

    def wait_for_page_load(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(1)
            return True
        except: return False

    def kill_existing_messages(self):
        """psutil 없이 Windows 명령으로 프로세스 종료"""
        try:
            # Chrome 프로세스 중 Messages 관련 종료
            cmd = 'taskkill /F /IM chrome.exe /FI "WINDOWTITLE eq *Messages*" 2>nul'
            subprocess.run(cmd, shell=True, capture_output=True)
            
            # 디버그 포트 사용 중인 Chrome 종료
            cmd2 = f'netstat -ano | findstr :{self.debug_port}'
            result = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        subprocess.run(f'taskkill /F /PID {pid} 2>nul', shell=True, capture_output=True)
            
            print("✅ 기존 프로세스 정리 완료")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ 프로세스 종료 중 오류: {e}")

    def find_chrome_path(self):
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
        for path in possible_paths:
            if os.path.exists(path): return path
        try:
            result = subprocess.run(['where', 'chrome.exe'], capture_output=True, text=True, check=False)
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip().split('\n')[0]
        except: pass
        return None

    def start_chrome_debug_mode(self):
        try:
            self.kill_existing_messages()
            chrome_path = self.find_chrome_path()
            if not chrome_path:
                print("❌ Chrome을 찾을 수 없습니다.")
                return False
            
            print(f"🔍 Chrome 경로: {chrome_path}")
            
            import tempfile
            temp_dir = os.path.join(tempfile.gettempdir(), f"GMsgDebug_{self.debug_port}")
            os.makedirs(temp_dir, exist_ok=True)
            
            cmd = [chrome_path, f"--remote-debugging-port={self.debug_port}", f"--user-data-dir={temp_dir}", 
                   "--app=https://messages.google.com/web", "--no-first-run", "--no-default-browser-check"]
            
            print(f"🚀 Google Messages를 디버그 모드로 시작 중...")
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("⏳ 앱 로딩 대기 중...")
            time.sleep(5)
            return True
        except Exception as e:
            print(f"❌ Chrome 시작 실패: {e}")
            return False

    def setup_driver(self):
        try:
            print("🌐 Chrome 디버그 포트에 연결 중...")
            if not self.start_chrome_debug_mode(): return False
            
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            messages_found = False
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                if "messages.google" in self.driver.current_url:
                    print(f"✅ Google Messages 탭 연결 성공!")
                    messages_found = True
                    break
            
            if not messages_found:
                print("❌ Google Messages 탭을 찾을 수 없습니다.")
                return False
            
            print("✅ Chrome 드라이버 설정 완료")
            return True
        except Exception as e:
            print(f"❌ Chrome 드라이버 설정 실패: {e}")
            return False

    def login_google_messages(self):
        try:
            print("🔄 로그인 상태 확인 중...")
            self.wait_for_page_load()
            qr_selectors = "[data-e2e-name='qr-code'], .qr-code, [alt*='QR']"
            qr_code = self.smart_wait_for_element(qr_selectors, timeout=5)

            if qr_code and qr_code.is_displayed():
                print("📱 QR 코드를 스캔해주세요...")
                print("⏳ 로그인 완료를 기다리는 중...")
                WebDriverWait(self.driver, 120).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, qr_selectors.split(',')[0]))
                )
                time.sleep(3)
                print("✅ 로그인 완료!")
            else:
                print("✅ 이미 로그인된 상태입니다.")
            return True
        except Exception:
            print("✅ 이미 로그인된 상태로 간주하고 진행합니다.")
            return True


    def send_message(self, phone_number, message, max_retries=2):
        for attempt in range(max_retries):
            try:
                print(f"📨 {phone_number}에게 메시지 전송 시작... (시도 {attempt + 1}/{max_retries})")
                clean_phone = self.normalize_phone_number(phone_number)
                if not clean_phone:
                    print("❌ 유효하지 않은 전화번호입니다.")
                    return False

                if self.send_message_selenium_fallback(clean_phone, message):
                    print(f"✅ {clean_phone}에게 메시지 전송 완료!")
                    return True
                else:
                    raise Exception("Selenium Fallback 전송 실패")
            except Exception as e:
                print(f"❌ 메시지 전송 실패 (시도 {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ 5초 후 재시도...")
                    time.sleep(5)
                else:
                    print("❌ 최종 전송에 실패했습니다.")
                    return False
        return False

    def send_message_selenium_fallback(self, phone_number, message):
        try:
            print("🔄 메시지 전송 중...")
            self.driver.get("https://messages.google.com/web/conversations")
            self.wait_for_page_load(15)

            # 새 대화 시작
            start_chat_button = self.smart_wait_for_element(
                ['[aria-label*="Start chat"]', '[aria-label*="새 대화"]', '.fab-label'], 
                clickable=True
            )
            if not start_chat_button:
                print("❌ '새 대화' 버튼을 찾을 수 없습니다.")
                return False
            start_chat_button.click()
            time.sleep(1)

            # 전화번호 입력
            recipient_input = self.smart_wait_for_element(
                ['input[placeholder*="Type a name"]', 'input[placeholder*="이름, 전화번호 또는 이메일 입력"]', 'input[type="text"]']
            )
            if not recipient_input:
                print("❌ 전화번호 입력창을 찾을 수 없습니다.")
                return False
            recipient_input.send_keys(phone_number)
            time.sleep(1.5)
            recipient_input.send_keys(Keys.ENTER)
            
            # 대화창 로딩 대기
            time.sleep(3)
            print("📱 대화창 로딩 중...")
            
            # 텍스트만 전송 (텍스트 전용 버전)
            print("📝 텍스트 메시지 전송 중...")
            if not self.send_text_message(message):
                print("❌ 텍스트 메시지 전송 실패")
                return False

            print("✅ 메시지 전송 완료!")
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"❌ 메시지 전송 실패: {e}")
            if self.debug_mode:
                traceback.print_exc()
            return False

    def send_text_message(self, message):
        """텍스트 메시지만 전송 - 개선된 textarea 찾기"""
        try:
            # 페이지 로딩 대기
            time.sleep(2)
            
            # 여러 방법으로 메시지 입력창 찾기
            message_input = None
            
            # 1차: 기본 셀렉터들
            selectors = [
                'textarea[aria-label*="문자 메시지"]',
                'textarea[aria-label*="Text message"]', 
                'textarea[placeholder*="메시지"]',
                'textarea[placeholder*="message"]',
                'div[contenteditable="true"][aria-label*="메시지"]',
                'div[contenteditable="true"][aria-label*="message"]'
            ]
            
            for selector in selectors:
                try:
                    message_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if message_input and message_input.is_displayed():
                        print(f"✅ 메시지 입력창 발견: {selector}")
                        break
                except:
                    continue
            
            # 2차: JavaScript로 textarea 찾기
            if not message_input:
                try:
                    self.driver.execute_script("""
                        var textareas = document.querySelectorAll('textarea');
                        for(var i = 0; i < textareas.length; i++) {
                            if(textareas[i].offsetParent !== null) {
                                textareas[i].setAttribute('data-found-textarea', 'true');
                                break;
                            }
                        }
                    """)
                    
                    message_input = self.driver.find_element(By.CSS_SELECTOR, 'textarea[data-found-textarea="true"]')
                    print("✅ JavaScript로 메시지 입력창 발견")
                except:
                    pass
            
            if not message_input:
                print("❌ 메시지 입력창을 찾을 수 없습니다.")
                return False
            
            # 메시지 입력창 활성화
            self.driver.execute_script("arguments[0].scrollIntoView(true);", message_input)
            time.sleep(0.5)
            message_input.click()
            time.sleep(0.5)
            
            # 기존 텍스트 모두 지우기
            message_input.clear()
            time.sleep(0.3)
            
            # 텍스트를 그대로 입력 (개행 문자 유지)
            print(f"📝 전송할 메시지: {message[:50]}...")
            
            # JavaScript로 텍스트 설정 (개행 문자 유지)
            self.driver.execute_script("arguments[0].value = arguments[1];", message_input, message)
            time.sleep(0.5)
            
            # 입력 이벤트 발생시키기
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", message_input)
            time.sleep(1)

            # 메시지 전송 - 버튼 클릭 우선
            send_button = self.smart_wait_for_element(
                ['button[aria-label*="Send message"]', 'button[aria-label*="메시지 보내기"]'], 
                clickable=True
            )
            if send_button:
                send_button.click()
                print("✅ 전송 버튼으로 메시지 전송")
            else:
                print("⚠️ 전송 버튼을 찾지 못해 Enter키로 전송합니다.")
                message_input.send_keys(Keys.ENTER)
            
            print("✅ 텍스트 메시지 전송 완료!")
            time.sleep(2)  # 전송 완료 대기 시간 단축
            return True
            
        except Exception as e:
            print(f"❌ 텍스트 메시지 전송 실패: {e}")
            return False

    def load_remind_data(self):
        try:
            remind_sheet = self.client.open_by_key("1vmxctnMO7gZfe9_3ZcuaX8peOGvHIo0TAl8DS4wVZqU").worksheet("Remind")
            template_sheet = self.client.open_by_key("1vmxctnMO7gZfe9_3ZcuaX8peOGvHIo0TAl8DS4wVZqU").worksheet("Template")
            header, values = template_sheet.row_values(1), template_sheet.row_values(2)
            templates = dict(zip(header, values))
            rows = remind_sheet.get_all_values()[1:]
            
            remind_data = []
            for row in rows:
                if len(row) >= 4 and any(row):
                    name, phone, field = row[0].strip(), row[1].strip(), row[2].strip()
                    lawyer = row[3].strip() if row[3].strip() else "테헤란"
                    code = row[4].strip() if len(row) > 4 else ""
                    body_template = templates.get(code, f"템플릿 코드({code}) 없음")
                    message = body_template.replace("{이름}", name).replace("{연락처}", phone).replace("{분야}", field).replace("{변리사}", lawyer)
                    remind_data.append({'name': name, 'phone': phone, 'field': field, 'lawyer': lawyer, 'message': message})
            
            print(f"📋 {len(remind_data)}개의 리마인드 데이터 로드 완료")
            return remind_data
        except Exception as e:
            print(f"❌ 리마인드 데이터 로드 실패: {e}")
            return []

    def send_all_reminders(self):
        if not self.setup_driver(): return
        try:
            if not self.login_google_messages(): return
            remind_data = self.load_remind_data()
            if not remind_data:
                print("📝 전송할 리마인드가 없습니다.")
                return
            success_count, total_count = 0, len(remind_data)
            print(f"🚀 {total_count}개의 리마인드 전송 시작")
            for i, data in enumerate(remind_data, 1):
                print(f"\n📨 [{i}/{total_count}] 전송 중: {data['name']} ({data['phone']})")
                if self.send_message(data['phone'], data['message']):
                    success_count += 1
                    self.log_message(data, "성공")
                else:
                    self.log_message(data, "실패")
                
                # 각 고객 전송 후 안전한 정리 작업
                if i < total_count:
                    print(f"⏳ 다음 고객을 위해 2초 대기...")
                    time.sleep(1)
                    
                    try:
                        # 1. 강력한 파일 창 닫기
                        self.safe_close_file_dialog()
                        time.sleep(1)
                        
                        # 2. 추가 정리 작업
                        try:
                            # 모든 파일 관련 요소 강제 제거
                            self.driver.execute_script("""
                                // 모든 파일 입력 제거
                                document.querySelectorAll('input[type="file"]').forEach(el => el.remove());
                                
                                // 모든 모달/팝업 제거
                                document.querySelectorAll('[role="dialog"], .modal, .popup').forEach(el => el.remove());
                                
                                // 높은 z-index 요소들 숨기기
                                Array.from(document.querySelectorAll('*')).forEach(el => {
                                    const style = window.getComputedStyle(el);
                                    if (parseInt(style.zIndex) > 100) {
                                        el.style.display = 'none';
                                    }
                                });
                            """)
                        except:
                            pass
                        
                        # 3. 세션 확인 후 페이지 완전 새로고침
                        if self.check_session():
                            self.driver.get("https://messages.google.com/web/conversations")
                            time.sleep(3)  # 페이지 로딩 충분히 대기
                            
                            # 페이지 로딩 완료 확인
                            self.wait_for_page_load(10)
                            
                            print("✅ 다음 고객을 위한 완전 초기화 완료")
                        else:
                            print("❌ 세션이 끊어져서 다음 고객 전송을 중단합니다.")
                            break
                        
                    except Exception as e:
                        self.debug_print(f"초기화 오류: {e}")
                        # 오류 시에도 세션 확인 후 기본 초기화 시도
                        try:
                            if self.check_session():
                                self.driver.get("https://messages.google.com/web/conversations")
                                time.sleep(2)
                            else:
                                print("❌ 세션 문제로 전송을 중단합니다.")
                                break
                        except:
                            print("❌ 복구할 수 없는 오류로 전송을 중단합니다.")
                            break
            print(f"\n✅ 전송 완료: {success_count}/{total_count}")
        finally:
            self.close()

    def log_message(self, data, result):
        try:
            log_sheet = self.client.open_by_key("1vmxctnMO7gZfe9_3ZcuaX8peOGvHIo0TAl8DS4wVZqU").worksheet("Log")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_row = [data['name'], data['phone'], data['field'], data['lawyer'], data['message'][:100], result, now]
            log_sheet.append_row(log_row)
        except Exception as e:
            print(f"⚠️ 로그 기록 실패: {e}")

    def close(self):
        print("🔄 프로그램 종료 중...")
        self.kill_existing_messages()

def main():
    sender = None
    try:
        print("=" * 60)
        print("📱 Google Messages Sender (최종 버전)")
        print("=" * 60)
        
        debug_choice = input("디버그 모드를 사용하시겠습니까? (y/N): ").strip().lower()
        debug_mode = debug_choice in ['y', 'yes', '예']
        
        sender = GoogleMessagesSender(debug_mode=debug_mode)
        
        print("\n실행할 작업을 선택하세요:")
        print("1: 전체 리마인드 전송")
        print("2: 테스트 전송")
        print("3: 연결 테스트")
        choice = input("선택 (1-3): ").strip()
        
        if choice == "1":
            sender.send_all_reminders()
        elif choice == "2":
            print("🧪 테스트 전송 모드")
            if sender.setup_driver() and sender.login_google_messages():
                test_phone = input("테스트 전화번호 입력: ").strip()
                test_message = input("테스트 메시지 입력 (Enter: 기본): ").strip() or "테스트 메시지입니다."
                test_lawyer = input("변리사 이름 입력 (Enter: 기본): ").strip() or "테헤란"
                if sender.send_message(test_phone, test_message):
                    print("✅ 테스트 전송 성공!")
                else:
                    print("❌ 테스트 전송 실패")
        elif choice == "3":
            if sender.setup_driver():
                sender.login_google_messages()
                input("\n테스트 완료. Enter를 눌러 종료하세요...")
        else:
            print("❌ 잘못된 선택입니다.")
    
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 실행 중 오류: {e}")
        if debug_mode:
            traceback.print_exc()
    finally:
        if sender:
            sender.close()
        print("\n프로그램을 종료합니다.")

if __name__ == "__main__":
    main()