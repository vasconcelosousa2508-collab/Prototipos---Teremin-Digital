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
volume_atual = 0.0  
fase = 0

limiteSombra = 400

def audio_callback(outdata, frames, time, status):
    global fase, volume_atual
    indices = np.arange(frames) + fase
    # Gerando a onda
    outdata[:, 0] = volume_atual * np.sin(2 * np.pi * frequencia * indices / amostragem)
    fase += frames




with sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem):
    while True:

        dados = porta.readline().decode('utf-8').strip()
        
        if dados.isdigit(): 
            valor = int(dados)
            print(valor)

        if valor < limiteSombra:
            volume_atual = 0.5
        else:
            volume_atual = 0.0