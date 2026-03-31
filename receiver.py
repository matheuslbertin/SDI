import socket
import struct
import threading
import queue
import time
import os
from datetime import datetime
from collections import Counter

# Configurações de Rede
MULTICAST_GROUP = '224.1.1.1' # Alterado para evitar faixas reservadas do sistema
PORT = 5007
INTERVALO_CALCULO = 60 # Janela de 60 segundos do seu código original

data_queue = queue.Queue()
mapa_suspeitos = {}
mapa_lock = threading.Lock()

def listener_thread():
    """Thread 1: Captura bruta de pacotes"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # No Mac, bind vazio '' ou '0.0.0.0' é o mais estável
    sock.bind(('', PORT))

    # Correção do struct: '4sL' é mais estável no macOS que '4sl'
    mreq = struct.pack('4sL', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    while True:
        try:
            data, address = sock.recvfrom(1024)
            # Coloca (conteúdo, ip_origem) na fila
            data_queue.put((data.decode('utf-8', errors='ignore'), address[0]))
        except Exception as e:
            print(f"Erro no listener: {e}")

def processor_thread():
    """Thread 2: Cálculo de frequência e retransmissão"""
    # Cria o socket de envio FORA do loop para evitar o Erro 56
    sock_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock_sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    os.system('clear')
    print(f"Monitorando grupo {MULTICAST_GROUP}...")

    while True:
        dados_da_janela = []
        # Define o fim da janela de 60 segundos
        tempo_limite = time.time() + INTERVALO_CALCULO
        
        while time.time() < tempo_limite:
            try:
                # Coleta dados da fila com timeout curto para não travar o loop de tempo
                item = data_queue.get(timeout=1)
                dados_da_janela.append(item)
            except queue.Empty:
                continue

        if dados_da_janela:
            # Extrai apenas os IPs para contar a frequência
            ips = [reg[1] for reg in dados_da_janela]
            contagem = Counter(ips)

            with mapa_lock:
                for ip, freq in contagem.items():
                    # Lógica de suspeito: frequência / tempo da janela (60s)
                    valor_suspeito = freq / INTERVALO_CALCULO
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    if ip not in mapa_suspeitos:
                        mapa_suspeitos[ip] = []
                    
                    mapa_suspeitos[ip].append([ts, valor_suspeito])
                    
                    # Retransmissão do cálculo para a rede
                    msg_out = f"{ts}, {ip}, {INTERVALO_CALCULO}, {valor_suspeito:.4f}"
                    sock_sender.sendto(msg_out.encode('utf-8'), (MULTICAST_GROUP, PORT))
                    
                    print(f"[{ts}] IP: {ip} | Freq: {freq} | Suspeito: {valor_suspeito:.4f}")
        
        dados_da_janela.clear()

# Inicialização
if __name__ == "__main__":
    t1 = threading.Thread(target=listener_thread, daemon=True)
    t2 = threading.Thread(target=processor_thread, daemon=True)
    
    t1.start()
    t2.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando...")