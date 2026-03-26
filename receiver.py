import socket
import struct
import threading
import queue
from datetime import datetime
import os

# Configurações
MULTICAST_GROUP = '224.1.1.1'
PORT = 5007

# Fila para comunicação entre as threads
data_queue = queue.Queue()

def listener_thread():
    """Thread 1: Responsável apenas por capturar os pacotes da rede"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', PORT))

    mreq = struct.pack('4sL', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    # Timeout para não travar a thread eternamente se ninguém enviar nada
    sock.settimeout(1.0)

    while True:
        try:
            data, address = sock.recvfrom(1024)
            arrival_time = datetime.now()
            # Coloca o dado, o IP e o horário de chegada na fila
            data_queue.put((data, address[0], arrival_time))
        except socket.timeout:
            continue

def processor_thread():
    """Thread 2: Responsável por calcular métricas e imprimir no terminal"""
    last_arrival = None
    acertos = 0
    falhas = 0
    
    # Limpa o terminal do Mac no início
    os.system('clear')
    print(f"{'Data/Hora':^15} | {'IP Origem':^15} | {'Delta':^8} | {'Razão F/A':^8}")
    print("-" * 65)

    while True:
        try:
            # Tenta pegar um item da fila com timeout de 6s (nossa detecção de falha)
            data, ip, now = data_queue.get(timeout=6.0)
            acertos += 1
            
            delta_str = "N/A"
            if last_arrival:
                delta = (now - last_arrival).total_seconds()
                delta_str = f"{delta:.2f}s"
            
            last_arrival = now
            razao = falhas / acertos if acertos > 0 else 0
            
            # Impressão formatada com o IP solicitado
            print(f"{now.strftime('%H:%M:%S'):^15} | {ip:^15} | {delta_str:^8} | {razao:^10.2f}")
            
        except queue.Empty:
            # Se a fila ficar vazia por mais de 6s, contamos como falha
            falhas += 1
            print(f"{datetime.now().strftime('%H:%M:%S')} | !!! FALHA DETECTADA (TIMEOUT) !!!")

# Inicia as threads
t1 = threading.Thread(target=listener_thread, daemon=True)
t2 = threading.Thread(target=processor_thread, daemon=True)

t1.start()
t2.start()

# Mantém o programa principal vivo
try:
    while True:
        import time
        time.sleep(1)
except KeyboardInterrupt:
    print("\nEncerrando receptor...")