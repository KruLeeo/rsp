import socket
import threading
from collections import deque

class IntermediateClient:
    def __init__(self):
        self.multicast_group = '233.0.0.1'
        self.port_udp = 1502
        self.port_tcp = 1503
        self.last_messages = deque(maxlen=5)
        self.current_message = ""
        
    def create_multicast_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind(('', self.port_udp))
            print(f"UDP сокет привязан к порту {self.port_udp}")
        except Exception as e:
            print(f"Ошибка привязки UDP: {e}")
            return None
            
        # Присоединяемся к multicast группе
        try:
            group = socket.inet_aton(self.multicast_group)
            mreq = group + socket.inet_aton('0.0.0.0')
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            print(f"Присоединились к multicast группе {self.multicast_group}")
        except Exception as e:
            print(f"Ошибка присоединения к multicast: {e}")
            return None
        
        return sock
        
    def udp_listener(self):
        sock = self.create_multicast_socket()
        if not sock:
            return
            
        print("Промежуточный клиент слушает multicast...")
        
        while True:
            try:
                data, address = sock.recvfrom(1024)
                message = data.decode('utf-8')
                print(f"Получено сообщение от {address}: {message}")
                
                if message != self.current_message:
                    print(f"Новое сообщение: {message}")
                    self.current_message = message
                    self.last_messages.append(message)
                    print(f"Текущие сообщения: {list(self.last_messages)}")
                    
            except Exception as e:
                print(f"Ошибка приема: {e}")
                
    def tcp_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_socket.bind(('localhost', self.port_tcp))
            server_socket.listen(5)
            print(f"TCP сервер запущен на порту {self.port_tcp}")
        except Exception as e:
            print(f"Ошибка запуска TCP сервера: {e}")
            return
        
        while True:
            try:
                client_socket, address = server_socket.accept()
                print(f"Конечный клиент подключен: {address}")
                
                if self.last_messages:
                    messages_text = "\n".join(self.last_messages)
                else:
                    messages_text = "Нет сообщений"
                    
                print(f"Отправляем клиенту: {messages_text}")
                client_socket.send(messages_text.encode('utf-8'))
                client_socket.close()
                print("Соединение с конечным клиентом закрыто")
                
            except Exception as e:
                print(f"Ошибка при работе с клиентом: {e}")
            
    def start(self):
        udp_thread = threading.Thread(target=self.udp_listener, daemon=True)
        udp_thread.start()
        self.tcp_server()

if __name__ == "__main__":
    client = IntermediateClient()
    client.start()