import serial
import numpy as np
import sounddevice as sd
from pynput import keyboard

# --- CONFIGURAÇÕES ---
porta_config = '/dev/ttyACM0' # String para a conexão inicial
amostragem = 44100
limiteDistancia = 30
volumeMaximo = 1.0

params = {
    'freq_alvo': 261.63,
    'freq_atual': 261.63,
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


try:
    porta = serial.Serial(porta_config, 9600, timeout=0.05)
except:
    print(f"Erro: Verifique se o Arduino está na porta {porta_config}")
    exit()

def audio_callback(outdata, frames, time, status):
    t = np.arange(frames) / amostragem
    
    params['vol_atual'] += 0.1 * (params['vol_alvo'] - params['vol_atual'])
    params['freq_atual'] += 0.08 * (params['freq_alvo'] - params['freq_atual'])
    
    f = params['freq_atual']
    v = params['vol_atual']
    
    arg = 2 * np.pi * f * t + params['fase']
    outdata[:, 0] = v * np.sin(arg)
    
    params['fase'] = (arg[-1] + (2 * np.pi * f / amostragem)) % (2 * np.pi)

def processar(leitura1, leitura2):
    if leitura1 <= limiteDistancia:
        proporcao = (limiteDistancia - leitura1) / limiteDistancia
        params['vol_alvo'] = (proporcao ** 2) * volumeMaximo
        
        if leitura2 <= limiteDistancia:
            for limiar, frequencia in ESCALA_MUSICAL:
                if leitura2 < limiar:
                    params['freq_alvo'] = frequencia
                    break
    else:
        params['vol_alvo'] = 0.0

def ao_pressionar(key):
    if key == keyboard.Key.esc:
        return False
    

with sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem):
    with keyboard.Listener(on_press=ao_pressionar) as listener:
        print(f"Sintetizador 45cm rodando... (Escala Lá Menor) | ESC para sair.")
        try:
            while listener.running:
                linha = porta.readline().decode('utf-8', errors='ignore').strip()
                if ',' in linha:
                    dados = linha.split(',')
                    if len(dados) == 2:
                        v1, v2 = dados[0], dados[1]
                        if v1.isdigit() and v2.isdigit():
                            # print(f"Freq: {v1} | Vol: {v2}")
                            processar(int(v1), int(v2))
                            
        except Exception as e:
            print(f"\nErro: {e}")
        finally:
            porta.close()