import socket
import time
from datetime import datetime

MULTICAST_GROUP = ('224.1.1.1', 5007)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

print("Iniciando transmissao de métricas...")

try:
    while True:
        # Enviando o timestamp atual como mensagem
        now = datetime.now().isoformat()
        sock.sendto(now.encode(), MULTICAST_GROUP)
        
        # Intervalo aleatório entre 2 e 5 segundos
        import random
        time.sleep(random.uniform(2, 5))
except KeyboardInterrupt:
    sock.close()