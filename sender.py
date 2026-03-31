import socket
import time
from datetime import datetime

# Define o grupo multicast e a porta
MULTICAST_GROUP = ('224.1.1.1', 5007)
# Cria o socket UDP para multicast
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# Define o TTL para o pacote multicast
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

print("Iniciando transmissao de métricas...")

# Bloco principal para transmissão
try:
    while True:
        # Obtém o timestamp atual no formato ISO
        now = datetime.now().isoformat()
        # Envia o timestamp via multicast
        sock.sendto(now.encode(), MULTICAST_GROUP)
        
        # Importa o módulo random para gerar números aleatórios
        import random
        # Aguarda um tempo aleatório entre 2 e 5 segundos
        time.sleep(random.uniform(2, 5))
except KeyboardInterrupt:
    # Fecha o socket ao interromper o programa
    sock.close()