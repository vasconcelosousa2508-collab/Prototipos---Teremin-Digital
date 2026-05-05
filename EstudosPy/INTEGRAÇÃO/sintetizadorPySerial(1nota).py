# Arduino está enviando dados da leitura de sombra do LRD.

import serial
import numpy as np
import sounddevice as sd


# Configurações da Serial
try:
    porta = serial.Serial('/dev/ttyACM0', 9600, timeout=0.1)
except:
    print("Erro: Verifique se o Arduino está na porta /dev/ttyACM0")
    exit()

# Configurações de Áudio
amostragem = 44100
frequencia = 440.0
volume_alvo = 0.0 

volume_atual = 0.0
fase = 0

limiteSombra = 250

def audio_callback(outdata, frames, time, status):
    global fase, volume_atual, volume_alvo
    
    indices = np.arange(frames) + fase
    
    # Suavização simples para evitar estalos
    # O volume atual tenta "alcançar" o volume alvo gradualmente
    volume_atual = volume_atual + 0.1 * (volume_alvo - volume_atual)
    
    onda = volume_atual * np.sin(2 * np.pi * frequencia * indices / amostragem)
    outdata[:, 0] = onda
    fase += frames


with sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem):
    while True:
        dados = porta.readline().decode('utf-8').strip()
        if dados.isdigit(): 
            valor = int(dados)
            print(valor)
            
        if valor < limiteSombra:
            volume_alvo = 1.0
        else:
            volume_alvo = 0.0