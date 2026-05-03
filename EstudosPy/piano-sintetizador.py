import numpy as np
import sounddevice as sd
from pynput import keyboard

# Configurações
amostragem = 44100
frequencia = 440.0
volume_alvo = 0.0 
volume_atual = 0.0
fase = 0

# Notas (Frequências reais)
notas = {
    'a': 261.63, 's': 293.66, 'd': 329.63, 'f': 349.23,
    'g': 392.00, 'h': 440.00, 'j': 493.88, 'k': 523.25
}

def audio_callback(outdata, frames, time, status):
    global fase, volume_atual, volume_alvo
    
    indices = np.arange(frames) + fase
    
    # Suavização simples para evitar estalos no volume 2.0
    # O volume atual tenta "alcançar" o volume alvo gradualmente
    volume_atual = volume_atual + 0.1 * (volume_alvo - volume_atual)
    
    onda = volume_atual * np.sin(2 * np.pi * frequencia * indices / amostragem)
    outdata[:, 0] = onda
    fase += frames

def ao_pressionar(key):
    global frequencia, volume_alvo
    try:
        if key.char in notas:
            frequencia = notas[key.char]
            volume_alvo = 2.0  # Arrochado no 2.0!
    except AttributeError:
        pass

def ao_soltar(key):
    global volume_alvo
    volume_alvo = 0.0
    if key == keyboard.Key.esc:
        return False

print("--- PIANO TURBINADO (VOL 2.0) ---")
print("Toque A, S, D, F, G, H, J, K | Esc para sair")

with sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem):
    with keyboard.Listener(on_press=ao_pressionar, on_release=ao_soltar) as listener:
        listener.join()
# COMMITS FUNCIONAM?