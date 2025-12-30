import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import sys
import os
from datetime import datetime
import queue
import subprocess

# desktop_automation.py import - 두 가지 버전
try:
    import desktop_automation as text_only_module
    import desktop_automation_with_image as image_module
except ImportError as e:
    print(f"모듈을 찾을 수 없습니다: {e}")
    sys.exit(1)

class RemindGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📱 Google Messages 리마인드 전송 시스템")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # 아이콘 설정 (있다면)
        try:
            self.root.iconbitmap(default="app.ico")
        except:
            pass
        
        # 변수 초기화
        self.sender = None
        self.is_running = False
        self.log_queue = queue.Queue()
        self.send_mode = tk.StringVar(value="text_only")  # 기본값: 텍스트만
        
        # UI 생성
        self.create_widgets()
        
        # 로그 업데이트 스레드 시작
        self.update_log()
        
    def create_widgets(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="📱 Google Messages 리마인드 전송", 
                               font=("맑은 고딕", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 설정 프레임
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ 설정", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 전송 모드 선택
        mode_label = ttk.Label(settings_frame, text="📤 전송 모드:", font=("맑은 고딕", 10, "bold"))
        mode_label.grid(row=0, column=0, sticky=tk.W, pady=5)

        mode_frame = ttk.Frame(settings_frame)
        mode_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)

        text_only_radio = ttk.Radiobutton(mode_frame, text="📝 텍스트만 전송",
                                         variable=self.send_mode, value="text_only")
        text_only_radio.grid(row=0, column=0, padx=(0, 20))

        with_image_radio = ttk.Radiobutton(mode_frame, text="🖼️ 이미지 + 텍스트 전송",
                                          variable=self.send_mode, value="with_image")
        with_image_radio.grid(row=0, column=1)

        # 디버그 모드
        self.debug_var = tk.BooleanVar(value=False)
        debug_check = ttk.Checkbutton(settings_frame, text="🐛 디버그 모드",
                                     variable=self.debug_var)
        debug_check.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # 상태 표시
        status_frame = ttk.LabelFrame(main_frame, text="📊 상태", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="🔴 대기 중", 
                                     font=("맑은 고딕", 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # 실행 버튼들
        self.start_all_btn = ttk.Button(button_frame, text="🚀 전체 리마인드 전송", 
                                       command=self.start_all_reminders,
                                       style="Accent.TButton")
        self.start_all_btn.grid(row=0, column=0, padx=5)
        
        self.test_btn = ttk.Button(button_frame, text="🧪 테스트 전송", 
                                  command=self.start_test)
        self.test_btn.grid(row=0, column=1, padx=5)
        
        self.connect_btn = ttk.Button(button_frame, text="🔗 연결 테스트", 
                                     command=self.start_connection_test)
        self.connect_btn.grid(row=0, column=2, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ 중지", 
                                  command=self.stop_process, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=3, padx=5)
        
        # 로그 프레임
        log_frame = ttk.LabelFrame(main_frame, text="📝 실행 로그", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 로그 텍스트 영역
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80,
                                                  font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 로그 제어 버튼
        log_btn_frame = ttk.Frame(log_frame)
        log_btn_frame.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        ttk.Button(log_btn_frame, text="🗑️ 로그 지우기", 
                  command=self.clear_log).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(log_btn_frame, text="💾 로그 저장", 
                  command=self.save_log).grid(row=0, column=1, padx=5)
        
        # 푸터
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Label(footer_frame, text="📱 Google Messages 리마인드 시스템 v2.0 | 특허법인 테헤란", 
                 font=("맑은 고딕", 8)).grid(row=0, column=0)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        settings_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def log_message(self, message):
        """로그 메시지를 큐에 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}")
    
    def update_log(self):
        """로그 큐에서 메시지를 읽어와 UI 업데이트"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message + "\\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # 100ms마다 다시 체크
        self.root.after(100, self.update_log)
    
    def clear_log(self):
        """로그 텍스트 지우기"""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """로그를 파일로 저장"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")],
                title="로그 저장"
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("저장 완료", f"로그가 저장되었습니다:\\n{filename}")
        except Exception as e:
            messagebox.showerror("저장 실패", f"로그 저장 중 오류가 발생했습니다:\\n{e}")
    
    def set_running_state(self, running):
        """실행 상태 설정"""
        self.is_running = running
        
        if running:
            self.status_label.config(text="🟢 실행 중")
            self.progress.start()
            self.start_all_btn.config(state=tk.DISABLED)
            self.test_btn.config(state=tk.DISABLED)
            self.connect_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="🔴 대기 중")
            self.progress.stop()
            self.start_all_btn.config(state=tk.NORMAL)
            self.test_btn.config(state=tk.NORMAL)
            self.connect_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def start_all_reminders(self):
        """전체 리마인드 전송 시작"""
        if self.is_running:
            return

        def run_task():
            try:
                mode = self.send_mode.get()
                if mode == "with_image":
                    self.log_message("🚀 전체 리마인드 전송을 시작합니다... (이미지 + 텍스트)")
                    self.sender = image_module.GoogleMessagesSender(debug_mode=self.debug_var.get())
                else:
                    self.log_message("🚀 전체 리마인드 전송을 시작합니다... (텍스트만)")
                    self.sender = text_only_module.GoogleMessagesSender(debug_mode=self.debug_var.get())
                
                # 로그 메시지 리다이렉션
                import sys
                from io import StringIO
                
                # stdout 캡처
                old_stdout = sys.stdout
                sys.stdout = captured_output = StringIO()
                
                try:
                    self.sender.send_all_reminders()
                finally:
                    sys.stdout = old_stdout
                    
                # 캡처된 출력을 로그에 추가
                output = captured_output.getvalue()
                for line in output.split('\\n'):
                    if line.strip():
                        self.log_message(line)
                
                self.log_message("✅ 전체 리마인드 전송이 완료되었습니다!")
                
            except Exception as e:
                self.log_message(f"❌ 오류 발생: {e}")
            finally:
                self.root.after(0, lambda: self.set_running_state(False))
        
        self.set_running_state(True)
        threading.Thread(target=run_task, daemon=True).start()
    
    def start_test(self):
        """테스트 전송 시작"""
        if self.is_running:
            return
        
        # 테스트 정보 입력 다이얼로그
        test_dialog = TestDialog(self.root)
        self.root.wait_window(test_dialog.dialog)
        
        if test_dialog.result:
            phone, message, lawyer = test_dialog.result
            
            def run_task():
                try:
                    mode = self.send_mode.get()
                    if mode == "with_image":
                        self.log_message(f"🧪 테스트 전송을 시작합니다: {phone} (이미지 + 텍스트)")
                        self.sender = image_module.GoogleMessagesSender(debug_mode=self.debug_var.get())
                    else:
                        self.log_message(f"🧪 테스트 전송을 시작합니다: {phone} (텍스트만)")
                        self.sender = text_only_module.GoogleMessagesSender(debug_mode=self.debug_var.get())

                    if self.sender.setup_driver() and self.sender.login_google_messages():
                        # 모드에 따라 send_message 호출 방식 변경
                        if mode == "with_image":
                            success = self.sender.send_message(phone, message, lawyer)
                        else:
                            success = self.sender.send_message(phone, message)

                        if success:
                            self.log_message("✅ 테스트 전송 성공!")
                        else:
                            self.log_message("❌ 테스트 전송 실패")
                    
                except Exception as e:
                    self.log_message(f"❌ 테스트 중 오류 발생: {e}")
                finally:
                    self.root.after(0, lambda: self.set_running_state(False))
            
            self.set_running_state(True)
            threading.Thread(target=run_task, daemon=True).start()
    
    def start_connection_test(self):
        """연결 테스트 시작"""
        if self.is_running:
            return

        def run_task():
            try:
                self.log_message("🔗 연결 테스트를 시작합니다...")
                # 연결 테스트는 텍스트 전용 모듈 사용 (더 가벼움)
                self.sender = text_only_module.GoogleMessagesSender(debug_mode=self.debug_var.get())
                
                if self.sender.setup_driver():
                    self.log_message("✅ Chrome 드라이버 연결 성공")
                    if self.sender.login_google_messages():
                        self.log_message("✅ Google Messages 로그인 성공")
                        self.log_message("🎉 연결 테스트 완료!")
                    else:
                        self.log_message("❌ Google Messages 로그인 실패")
                else:
                    self.log_message("❌ Chrome 드라이버 연결 실패")
                    
            except Exception as e:
                self.log_message(f"❌ 연결 테스트 중 오류 발생: {e}")
            finally:
                self.root.after(0, lambda: self.set_running_state(False))
        
        self.set_running_state(True)
        threading.Thread(target=run_task, daemon=True).start()
    
    def stop_process(self):
        """실행 중인 프로세스 중지"""
        if self.sender:
            try:
                self.sender.close()
                self.log_message("⏹️ 프로세스가 중지되었습니다.")
            except:
                pass
        
        self.set_running_state(False)
    
    def on_closing(self):
        """프로그램 종료 시 정리"""
        if self.is_running:
            result = messagebox.askyesno("종료 확인", 
                                       "실행 중인 작업이 있습니다. 정말 종료하시겠습니까?")
            if not result:
                return
        
        if self.sender:
            try:
                self.sender.close()
            except:
                pass
        
        self.root.destroy()

class TestDialog:
    def __init__(self, parent):
        self.result = None
        
        # 다이얼로그 창 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🧪 테스트 전송 설정")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()  # 모달 다이얼로그
        
        # 중앙에 위치
        self.dialog.transient(parent)
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx()+100, parent.winfo_rooty()+100))
        
        # UI 생성
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 전화번호
        ttk.Label(main_frame, text="📞 전화번호:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.phone_entry = ttk.Entry(main_frame, width=30)
        self.phone_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.phone_entry.insert(0, "010-1234-5678")
        
        # 변리사
        ttk.Label(main_frame, text="👨‍💼 변리사:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.lawyer_entry = ttk.Entry(main_frame, width=30)
        self.lawyer_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.lawyer_entry.insert(0, "테헤란")
        
        # 메시지
        ttk.Label(main_frame, text="💬 메시지:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=5)
        self.message_text = tk.Text(main_frame, width=30, height=8)
        self.message_text.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        self.message_text.insert(1.0, "안녕하세요.\\n테스트 메시지입니다.\\n특허법인 테헤란")
        
        # 버튼
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="✅ 전송", command=self.ok_clicked).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="❌ 취소", command=self.cancel_clicked).grid(row=0, column=1, padx=5)
        
        # 그리드 설정
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def ok_clicked(self):
        phone = self.phone_entry.get().strip()
        lawyer = self.lawyer_entry.get().strip()
        message = self.message_text.get(1.0, tk.END).strip()
        
        if not phone or not message:
            messagebox.showerror("입력 오류", "전화번호와 메시지를 모두 입력해주세요.")
            return
        
        self.result = (phone, message, lawyer)
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()

def main():
    """GUI 앱 메인 실행 함수"""
    try:
        root = tk.Tk()
        
        # Windows에서 DPI 인식 개선
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        app = RemindGUI(root)
        
        # 종료 이벤트 처리
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # GUI 실행
        root.mainloop()
        
    except Exception as e:
        print(f"GUI 실행 중 오류 발생: {e}")
        input("Enter를 눌러 종료...")

if __name__ == "__main__":
    main()