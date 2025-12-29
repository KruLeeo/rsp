import socket
import tkinter as tk
from tkinter import ttk, scrolledtext

class FinalClient:
    def __init__(self):
        self.server_host = 'localhost'
        self.server_port = 1503
        self.auto_update = False
        self.auto_update_id = None  # ID для отмены планировщика
        
    def get_messages(self):
        try:
            print(f"Подключаемся к {self.server_host}:{self.server_port}...")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)  # Таймаут 5 секунд
            client_socket.connect((self.server_host, self.server_port))
            
            data = b""
            while True:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                data += chunk
                
            client_socket.close()
            messages = data.decode('utf-8')
            print(f"Получены сообщения: {messages}")
            return messages
            
        except Exception as e:
            error_msg = f"Ошибка подключения: {e}"
            print(error_msg)
            return error_msg
            
    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("Клиент погоды")
        self.root.geometry("500x300")
        
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Обновить", command=self.update_messages).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Автообновление", command=self.toggle_auto_update).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Выход", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=60, height=15)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = ttk.Label(self.root, textvariable=self.status_var)
        status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
    def toggle_auto_update(self):
        self.auto_update = not self.auto_update
        if self.auto_update:
            self.status_var.set("Автообновление включено")
            self.auto_update_loop()
        else:
            self.status_var.set("Автообновление выключено")
            if self.auto_update_id:
                self.root.after_cancel(self.auto_update_id)
                self.auto_update_id = None
        
    def auto_update_loop(self):
        if self.auto_update:
            self.update_messages()
            self.auto_update_id = self.root.after(5000, self.auto_update_loop)
        
    def update_messages(self):
        self.status_var.set("Обновление...")
        messages = self.get_messages()
        self.text_area.delete(1.0, tk.END)
        
        # Разделяем сообщения и добавляем разделители
        if messages:
            # Если сообщение содержит несколько строк, разделяем их
            message_lines = messages.strip().split('\n')
            formatted_messages = []
            
            for i, line in enumerate(message_lines):
                if line.strip():  # Пропускаем пустые строки
                    formatted_messages.append(line)
                    # Добавляем разделитель после каждого сообщения, кроме последнего
                    if i < len(message_lines) - 1:
                        formatted_messages.append("——————————————————————")
            
            # Объединяем все обратно в один текст
            final_text = '\n'.join(formatted_messages)
            self.text_area.insert(1.0, final_text)
        else:
            self.text_area.insert(1.0, messages)
            
        self.status_var.set("Обновлено")
        
    def start(self):
        self.create_gui()
        self.root.after(1000, self.update_messages)
        self.root.mainloop()

if __name__ == "__main__":
    client = FinalClient()
    client.start()