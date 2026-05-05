# Arduino está enviando dados da leitura de sombra do LRD.

import serial

import numpy as np
import sounddevice as sd
from pynput import keyboard

porta = serial.Serial('/dev/ttyACM0', 9600)

amostragem = 44100
frequencia = 440.0
volume_atual = 0.0  
fase = 0

limiteSombra = 400


def audio_callback(outdata, frames, time, status):
    global fase, volume_atual
    
    indices = np.arange(frames) + fase
    
    outdata[:, 0] = volume_atual * np.sin(2 * np.pi * frequencia * indices / amostragem)
    
    fase += frames


while(1):
    dados = porta.readline()
    print(dados.decode('utf-8'))

    if dados < limiteSombra:
        volume_atual = 2.0
            with sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem):
    else:
        volume_atual = 0.0
    
