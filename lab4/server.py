import socket
import time
import threading

class WeatherServer:
    def __init__(self):
        self.multicast_group = '233.0.0.1'
        self.port = 1502
        self.interval = 3
        
    def create_multicast_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        return sock
        
    def read_weather_message(self):
        try:
            with open('weather.txt', 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return "Погода: солнечно, +25°C"
            
    def start(self):
        print("Сервер погоды запущен...")
        sock = self.create_multicast_socket()
        
        while True:
            message = self.read_weather_message()
            print(f"Отправка сообщения: {message}")
            sock.sendto(message.encode('utf-8'), (self.multicast_group, self.port))
            time.sleep(self.interval)

if __name__ == "__main__":
    server = WeatherServer()
    server.start()