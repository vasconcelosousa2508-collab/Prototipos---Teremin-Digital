import numpy as np
import sounddevice as sd
from queue import Queue

# --- CONFIGURAÇÕES GERAIS ---
amostragem = 44100
CHUNK = 1024  
limiteDistancia = 30
volumeMaximo = 1.0  

params = {
    'freq_alvo': 261.63,
    'freq_atual': 261.63,
    'freq_visual': 261.63, 
    'vol_alvo': 0.0,
    'vol_atual': 0.0,        
    'fase': 0.0
}

ESCALA_MUSICAL = [
    (4,  261.63),  # Dó (C4)
    (8, 293.66),  # Ré (D4)
    (12, 329.63),  # Mi (E4)
    (16, 349.23),  # Fá (F4)  
    (20, 392.00),  # Sol (G4)
    (24, 440.00),  # Lá (A4)
    (28, 493.88),  # Si (B4)
    (float('inf'), 523.25) # Dó Agudo (C5)
]



fila_onda = Queue()

def audio_callback(outdata, frames, time_info, status):
    t = np.arange(frames) / amostragem
    
    params['vol_atual'] += 0.1 * (params['vol_alvo'] - params['vol_atual'])
    params['freq_atual'] += 0.08 * (params['freq_alvo'] - params['freq_atual'])
    
    f = params['freq_atual']
    v = params['vol_atual']
    
    arg = 2 * np.pi * f * t + params['fase']
    onda = v * np.sin(arg)
    outdata[:, 0] = onda
    
    params['fase'] = (arg[-1] + (2 * np.pi * f / amostragem)) % (2 * np.pi)
    
    
    fila_onda.put(onda.copy())

def iniciar_audio():
    """Função utilitária para ligar os alto-falantes de forma limpa"""
    stream = sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem, blocksize=CHUNK)
    stream.start()
    return stream