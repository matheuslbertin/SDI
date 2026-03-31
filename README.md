Alunos: Matheus Bertin, Kaua Hopfer.


# 🛰️ Multicast Failure Detector (Python)

Este projeto implementa um **Detector de Falhas de Omissão** utilizando o protocolo **IP Multicast**. O sistema é composto por um Emissor (Sender) que transmite batimentos cardíacos (*heartbeats*) e um Receptor (Receiver) multi-thread que analisa a frequência dessas mensagens para determinar a integridade dos nós na rede.


## 📌 Funcionalidades
* **Comunicação Multicast UDP**: Transmissão eficiente de dados para múltiplos receptores simultâneos.
* **Arquitetura Multi-thread**: Divisão clara entre a thread de escuta (captura de pacotes) e a thread de processamento (cálculo de métricas).
* **Detecção de Omissão**: Monitoramento da taxa de "Suspeito" baseada na frequência de chegada de pacotes.
* **Análise de Delta**: Cálculo do intervalo de tempo real entre as mensagens recebidas.
* **Compatibilidade macOS**: Configuração de sockets otimizada para evitar erros de conexão (`OSError 56`).

## 🗂️ Estrutura do Projeto

* `sender.py`: Script responsável por enviar timestamps via multicast em intervalos aleatórios (2 a 5 segundos).
* `receiver.py`: Script principal que escuta o grupo, calcula o Delta, a Razão Falha/Acerto e o nível de Suspeito.

## 🚀 Como Executar

### Pré-requisitos
* Python 3.x instalado.
* Acesso a uma rede local que suporte tráfego Multicast (ou teste via Localhost).

### Instruções de Uso

1.  **Inicie o Receptor**:
    Abra o terminal e execute:
    ```bash
    python3 receiver.py
    ```
    *O console será limpo e exibirá o cabeçalho da tabela de monitoramento.*

2.  **Inicie o Emissor**:
    Abra uma **nova aba ou janela** do terminal e execute:
    ```bash
    python3 sender.py
    ```

3.  **Interpretação dos Dados**:
    No terminal do Receptor, você verá:
    * **Data/Hora**: Horário local da recepção.
    * **IP Origem**: Endereço IP do dispositivo emissor.
    * **Delta**: Tempo (em segundos) desde a última mensagem recebida deste IP.
    * **Razão F/A**: Taxa acumulada de Falhas (timeouts) sobre Acertos (mensagens recebidas).

## 🧪 O que é o valor "Suspeito"?

O valor de **Suspeito** representa a frequência de mensagens por segundo. 

* **Comportamento Normal**: Com o `sender.py` padrão (intervalo de 2-5s), o valor oscilará entre **0.28 e 0.33**.
* **Detecção de Falha**: Se o valor cair para **0.00**, o detector identifica uma falha de omissão total (nó offline ou rede interrompida).

## 🛠️ Customização

Você pode alterar as seguintes variáveis no topo dos arquivos:
* `MULTICAST_GROUP`: Endereço do grupo (ex: `224.1.1.1`).
* `PORT`: Porta UDP utilizada (ex: `5007`).
* `INTERVALO_CALCULO`: (No receptor) Tempo da janela para o cálculo de frequência.

---
*Desenvolvido para testes de sistemas distribuídos e detecção de falhas em tempo real.*
