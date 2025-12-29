import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext

class ChatClient:
    def __init__(self):
        self.multicast_group = '233.0.0.1'
        self.port_udp = 1502
        self.server_host = 'localhost'
        self.server_port = 1504
        
    def create_multicast_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind(('', self.port_udp))
        except Exception as e:
            print(f"Ошибка привязки: {e}")
            return None
            
        group = socket.inet_aton(self.multicast_group)
        mreq = group + socket.inet_aton('0.0.0.0')
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        return sock
        
    def udp_listener(self, text_widget):
        sock = self.create_multicast_socket()
        if not sock:
            return
            
        print("Клиент слушает multicast...")
        
        while True:
            try:
                data, address = sock.recvfrom(4096)
                messages = data.decode('utf-8')
                
                text_widget.after(0, self.update_chat, text_widget, messages)
                
            except Exception as e:
                print(f"Ошибка приема: {e}")
                
    def update_chat(self, text_widget, messages):
        text_widget.insert(tk.END, messages + "\n")
        text_widget.see(tk.END)
        
    def send_message(self, message_entry):
        message = message_entry.get().strip()
        if not message:
            return
            
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.server_host, self.server_port))
            client_socket.send(message.encode('utf-8'))
            client_socket.close()
            
            message_entry.delete(0, tk.END)
        except Exception as e:
            print(f"Ошибка отправки: {e}")
            
    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("Чат клиент")
        self.root.geometry("600x400")
        
        chat_frame = ttk.Frame(self.root)
        chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.chat_text = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, width=70, height=20)
        self.chat_text.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.Frame(self.root)
        input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.message_entry = ttk.Entry(input_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind('<Return>', lambda e: self.send_message(self.message_entry))
        
        ttk.Button(input_frame, text="Отправить", 
                  command=lambda: self.send_message(self.message_entry)).pack(side=tk.RIGHT)
                  
    def start(self):
        self.create_gui()
        
        # Запускаем UDP listener в отдельном потоке
        udp_thread = threading.Thread(target=self.udp_listener, args=(self.chat_text,), daemon=True)
        udp_thread.start()
        
        self.root.mainloop()

if __name__ == "__main__":
    client = ChatClient()
    client.start()