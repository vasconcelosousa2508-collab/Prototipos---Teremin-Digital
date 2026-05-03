import numpy as np
import sounddevice as sd
from pynput import keyboard

amostragem = 44100
frequencia = 440.0
volume_atual = 0.0  # Controle direto
fase = 0

notas = {
    'a': 261.63, 's': 293.66, 'd': 329.63, 'f': 349.23,
    'g': 392.00, 'h': 440.00, 'j': 493.88, 'k': 523.25, 'l': 587.33
}

def audio_callback(outdata, frames, time, status):
    global fase, volume_atual
    
    indices = np.arange(frames) + fase
    
    # SOM PURO: Sem rampas, sem suavização. 
    # Multiplicação direta do volume pela onda.
    outdata[:, 0] = volume_atual * np.sin(2 * np.pi * frequencia * indices / amostragem)
    
    fase += frames

def ao_pressionar(key):
    global frequencia, volume_atual
    try:
        if key.char in notas:
            frequencia = notas[key.char]
            volume_atual = 2.0  # Valor bruto
    except AttributeError:
        pass

def ao_soltar(key):
    global volume_atual
    # Corta o som na hora
    volume_atual = 0.0
    if key == keyboard.Key.esc:
        return False

print("--- SOM PURO E DIRETO (SEM SUAVIZAÇÃO) ---")
print("Toque A, S, D, F, G, H, J, K | Esc para sair")

with sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem):
    with keyboard.Listener(on_press=ao_pressionar, on_release=ao_soltar) as listener:
        listener.join()
