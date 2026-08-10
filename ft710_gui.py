import sys
import time
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

class YaesuFT710Power:
    def __init__(self, port, baudrate=38400):
        self.port = port
        self.baudrate = baudrate
        self.handle = None
        
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        self.SETDTR = 5
        self.CLRDTR = 6
        self.SETRTS = 3
        self.CLRRTS = 4
        self.GENERIC_READ = 0x80000000
        self.GENERIC_WRITE = 0x40000000
        self.OPEN_EXISTING = 3
        
        class DCB(ctypes.Structure):
            _fields_ = [
                ("DCBlength", wintypes.DWORD),
                ("BaudRate", wintypes.DWORD),
                ("fBits", wintypes.DWORD),
                ("wReserved", wintypes.WORD),
                ("XonLim", wintypes.WORD),
                ("XoffLim", wintypes.WORD),
                ("ByteSize", wintypes.BYTE),
                ("Parity", wintypes.BYTE),
                ("StopBits", wintypes.BYTE),
                ("XonChar", wintypes.CHAR),
                ("XoffChar", wintypes.CHAR),
                ("ErrorChar", wintypes.CHAR),
                ("EofChar", wintypes.CHAR),
                ("EvtChar", wintypes.CHAR),
                ("wReserved1", wintypes.WORD)
            ]
        self.DCB = DCB
    
    def _open_com_port(self):
        port_name = f"\\\\.\\{self.port}"
        self.handle = self.kernel32.CreateFileW(
            port_name,
            self.GENERIC_READ | self.GENERIC_WRITE,
            0,
            None,
            self.OPEN_EXISTING,
            0,
            None
        )
        if self.handle == -1:
            return False
        
        dcb = self.DCB()
        dcb.DCBlength = ctypes.sizeof(dcb)
        dcb.BaudRate = self.baudrate
        dcb.fBits = 0x00000001
        dcb.ByteSize = 8
        dcb.Parity = 0
        dcb.StopBits = 0
        dcb.XonChar = 0x11
        dcb.XoffChar = 0x13
        
        if not self.kernel32.SetCommState(self.handle, ctypes.byref(dcb)):
            return False
        return True
    
    def _send_break(self, duration_ms=250):
        self.kernel32.EscapeCommFunction(self.handle, 8)
        time.sleep(duration_ms / 1000.0)
        self.kernel32.EscapeCommFunction(self.handle, 9)
    
    def _toggle_dtr_rts(self):
        self.kernel32.EscapeCommFunction(self.handle, self.CLRDTR)
        self.kernel32.EscapeCommFunction(self.handle, self.CLRRTS)
        time.sleep(0.05)
        self.kernel32.EscapeCommFunction(self.handle, self.SETDTR)
        time.sleep(0.05)
        self.kernel32.EscapeCommFunction(self.handle, self.SETRTS)
        time.sleep(0.05)
    
    def _send_command(self, command):
        data = command.encode('ascii')
        bytes_written = wintypes.DWORD()
        result = ctypes.windll.kernel32.WriteFile(
            self.handle, data, len(data),
            ctypes.byref(bytes_written), None
        )
        return bool(result) and bytes_written.value == len(data)
    
    def _close_port(self):
        if self.handle:
            ctypes.windll.kernel32.CloseHandle(self.handle)
            self.handle = None
    
    def power_on(self):
        """Включение трансивера - БЕЗ ОЖИДАНИЯ ОТВЕТА"""
        try:
            # Открываем порт
            if not self._open_com_port():
                return False, "Не удалось открыть COM-порт"
            
            # Отправляем последовательность команд
            self._send_break(250)
            time.sleep(0.15)
            
            self._toggle_dtr_rts()
            time.sleep(0.1)
            
            self._send_command('AI0;')
            time.sleep(0.05)
            
            self._send_command('PS1;')
            time.sleep(0.05)
            
            # Закрываем порт СРАЗУ, не ждем ответа
            self._close_port()
            
            # Считаем что все ок, так как команда отправлена
            return True, "✅ Команда включения отправлена"
            
        except Exception as e:
            self._close_port()
            return False, f"❌ Ошибка: {e}"
    
    def power_off(self):
        """Выключение трансивера"""
        try:
            if not self._open_com_port():
                return False, "Не удалось открыть COM-порт"
            
            self._send_command('PS0;')
            time.sleep(0.1)
            self._close_port()
            
            return True, "✅ Команда выключения отправлена"
            
        except Exception as e:
            self._close_port()
            return False, f"❌ Ошибка: {e}"


class WorkerThread(threading.Thread):
    def __init__(self, controller, action, callback):
        super().__init__()
        self.controller = controller
        self.action = action
        self.callback = callback
        self.daemon = True
    
    def run(self):
        try:
            if self.action == 'on':
                success, msg = self.controller.power_on()
            else:
                success, msg = self.controller.power_off()
            self.callback(success, msg)
        except Exception as e:
            self.callback(False, f"Ошибка: {e}")


class FT710App:
    def __init__(self, root):
        self.root = root
        self.root.title("Yaesu FT-710 Управление питанием")
        self.root.geometry("500x550")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a2e')
        
        self.is_busy = False
        
        # Настройки порта
        frame_settings = tk.Frame(root, bg='#16213e', relief=tk.RIDGE, bd=2)
        frame_settings.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Label(frame_settings, text="COM-порт:", bg='#16213e', fg='white').pack(side=tk.LEFT, padx=5)
        self.port_var = tk.StringVar(value="COM8")
        self.port_combo = ttk.Combobox(frame_settings, textvariable=self.port_var, width=10)
        self.port_combo['values'] = [f'COM{i}' for i in range(1, 11)]
        self.port_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_settings, text="Скорость:", bg='#16213e', fg='white').pack(side=tk.LEFT, padx=10)
        self.baud_var = tk.StringVar(value="38400")
        self.baud_combo = ttk.Combobox(frame_settings, textvariable=self.baud_var, width=8)
        self.baud_combo['values'] = ['4800', '9600', '19200', '38400', '57600', '115200']
        self.baud_combo.pack(side=tk.LEFT, padx=5)
        
        # Кнопки
        frame_buttons = tk.Frame(root, bg='#1a1a2e')
        frame_buttons.pack(pady=15)
        
        self.btn_on = tk.Button(frame_buttons, text="🟢 ВКЛЮЧИТЬ", 
                                bg='#00b894', fg='white', font=('Arial', 14, 'bold'),
                                padx=30, pady=15, command=self.power_on)
        self.btn_on.pack(side=tk.LEFT, padx=15)
        
        self.btn_off = tk.Button(frame_buttons, text="🔴 ВЫКЛЮЧИТЬ",
                                 bg='#e17055', fg='white', font=('Arial', 14, 'bold'),
                                 padx=30, pady=15, command=self.power_off)
        self.btn_off.pack(side=tk.LEFT, padx=15)
        
        # Статус
        self.status_label = tk.Label(root, text="✅ Готов", 
                                     bg='#1a1a2e', fg='#00d4ff', 
                                     font=('Arial', 14, 'bold'))
        self.status_label.pack(pady=10)
        
        # Индикатор
        self.progress = ttk.Progressbar(root, mode='indeterminate', length=300)
        self.progress.pack(pady=5)
        self.progress.pack_forget()
        
        # Лог
        frame_log = tk.Frame(root, bg='#1a1a2e')
        frame_log.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(frame_log, bg='#0f0f1f', fg='#00ff88',
                                                   font=('Consolas', 10), height=12)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_text.insert(tk.END, "=" * 50 + "\n")
        self.log_text.insert(tk.END, "🔌 FT-710 Управление питанием\n")
        self.log_text.insert(tk.END, "=" * 50 + "\n")
        self.log_text.insert(tk.END, "⚠️ Запуск от имени администратора!\n")
        self.log_text.insert(tk.END, "=" * 50 + "\n")
        self.log_text.see(tk.END)
    
    def log(self, msg):
        self.log_text.insert(tk.END, f"{msg}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def set_status(self, text, color='#00d4ff'):
        self.status_label.config(text=text, fg=color)
        self.root.update_idletasks()
    
    def set_busy(self, busy):
        self.is_busy = busy
        state = 'disabled' if busy else 'normal'
        self.btn_on.config(state=state)
        self.btn_off.config(state=state)
        self.port_combo.config(state='disabled' if busy else 'normal')
        self.baud_combo.config(state='disabled' if busy else 'normal')
        
        if busy:
            self.progress.pack(pady=5)
            self.progress.start(10)
        else:
            self.progress.stop()
            self.progress.pack_forget()
        
        self.root.update_idletasks()
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log("📋 Лог очищен")
    
    def on_finished(self, success, msg):
        self.set_busy(False)
        if success:
            self.set_status("✅ Успешно!", '#00ff88')
            self.log(f"✅ {msg}")
        else:
            self.set_status("❌ Ошибка", '#ff4757')
            self.log(f"❌ {msg}")
            messagebox.showerror("Ошибка", msg)
    
    def power_on(self):
        if self.is_busy:
            return
        
        port = self.port_var.get().strip()
        if not port:
            self.log("❌ Нет COM-порта")
            return
        
        try:
            baudrate = int(self.baud_var.get())
        except:
            self.log("❌ Неверная скорость")
            return
        
        self.log(f"🔄 Включение {port}...")
        self.set_status("⏳ Выполняется...", '#ffa502')
        self.set_busy(True)
        
        controller = YaesuFT710Power(port, baudrate)
        thread = WorkerThread(controller, 'on', self.on_finished)
        thread.start()
    
    def power_off(self):
        if self.is_busy:
            return
        
        port = self.port_var.get().strip()
        if not port:
            self.log("❌ Нет COM-порта")
            return
        
        try:
            baudrate = int(self.baud_var.get())
        except:
            self.log("❌ Неверная скорость")
            return
        
        self.log(f"🔄 Выключение {port}...")
        self.set_status("⏳ Выполняется...", '#ffa502')
        self.set_busy(True)
        
        controller = YaesuFT710Power(port, baudrate)
        thread = WorkerThread(controller, 'off', self.on_finished)
        thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = FT710App(root)
    root.mainloop()