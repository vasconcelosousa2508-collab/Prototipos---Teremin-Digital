import serial
import numpy as np
import sounddevice as sd
from pynput import keyboard
import customtkinter as ctk
import threading

# --- CONFIGURAÇÕES DO THEREMIN & ARDUINO ---
porta_config = '/dev/ttyACM0' 
amostragem = 44100
limiteDistancia = 30
volumeMaximo = 1.0

# Cores do VU Meter
COR_FUNDO_RGB = (11, 3, 44)       # #0b032c
COR_ROSA_RGB = (235, 104, 166)    # #eb68a6

# Parâmetros oficiais do motor unificados
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
except Exception as e:
    print(f"Erro: Verifique se o Arduino está na porta {porta_config}\nDetalhe: {e}")
    exit()

# --- MOTOR DE ÁUDIO DO THEREMIN ---
def audio_callback(outdata, frames, time, status):
    t = np.arange(frames) / amostragem
    
    # Rampa contínua para volume e frequência evitando estalos
    params['vol_atual'] += 0.1 * (params['vol_alvo'] - params['vol_atual'])
    params['freq_atual'] += 0.08 * (params['freq_alvo'] - params['freq_atual'])
    
    f = params['freq_atual']
    v = params['vol_atual']
    
    arg = 2 * np.pi * f * t + params['fase']
    outdata[:, 0] = v * np.sin(arg)
    
    params['fase'] = (arg[-1] + (2 * np.pi * f / amostragem)) % (2 * np.pi)

# --- LÓGICA DE TRATAMENTO DOS SENSORES ---
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

# --- THREAD DE LEITURA SERIAL ---
def loop_arduino(listener):
    try:
        while listener.running:
            linha = porta.readline().decode('utf-8', errors='ignore').strip()
            if ',' in linha:
                dados = linha.split(',')
                if len(dados) == 2:
                    v1, v2 = dados[0], dados[1]
                    if v1.isdigit() and v2.isdigit():
                        processar(int(v1), int(v2))
    except Exception as e:
        print(f"\nErro na leitura do Arduino: {e}")
    finally:
        porta.close()

def ao_pressionar(key):
    if key == keyboard.Key.esc:
        app.destroy()
        return False

# --- CÁLCULO VISUAL DO FADE DE COR ---
def calcular_fade_cor(vol_atual, inicio_bloco):
    fator = (vol_atual - inicio_bloco) / 0.1
    fator = max(0.0, min(1.0, fator)) 
    
    r = int(COR_FUNDO_RGB[0] + (COR_ROSA_RGB[0] - COR_FUNDO_RGB[0]) * fator)
    g = int(COR_FUNDO_RGB[1] + (COR_ROSA_RGB[1] - COR_FUNDO_RGB[1]) * fator)
    b = int(COR_FUNDO_RGB[2] + (COR_ROSA_RGB[2] - COR_FUNDO_RGB[2]) * fator)
    
    return f"#{r:02x}{g:02x}{b:02x}"

# --- SEU COMPONENTE CUSTOMTKINTER ---
class BarraVolumeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VU Meter - Modo Theremin")
        self.geometry("450x200")
        self.configure(fg_color="#0b032c") 
        
        self.label = ctk.CTkLabel(self, text="Volume do Sensor", font=("Arial", 14, "bold"), text_color="#ffffff")
        self.label.pack(pady=(40, 5))
        
        self.frame_vu = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_vu.pack(pady=10)
        
        self.blocos = []
        for i in range(10):
            bloco = ctk.CTkFrame(self.frame_vu, width=25, height=35, corner_radius=4, fg_color="#0b032c")
            bloco.pack(side="left", padx=3)
            self.blocos.append(bloco)
            
        self.atualizar_visual()

    def atualizar_visual(self):
        vol_atual = params['vol_atual']
        
        # Passa varrendo os 10 blocos aplicando a cor calculada pela rampa do Arduino
        for i in range(10):
            inicio_bloco = i * 0.1
            nova_cor = calcular_fade_cor(vol_atual, inicio_bloco)
            self.blocos[i].configure(fg_color=nova_cor)
            
        self.after(15, self.atualizar_visual)

# --- EXECUÇÃO ---
if __name__ == "__main__":
    # 1. Ativa a saída do alto-falante
    stream = sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem)
    stream.start()
    
    # 2. Configura o escutador do teclado para gerenciar a saída do app pelo ESC
    ouvinte = keyboard.Listener(on_press=ao_pressionar)
    ouvinte.start()
    
    # 3. Dispara a Thread que cuida da USB (Serial) sem travar a interface
    thread_usb = threading.Thread(target=loop_arduino, args=(ouvinte,), daemon=True)
    thread_usb.start()
    
    # 4. Inicia a janela gráfica
    app = BarraVolumeApp()
    app.mainloop()
    
    # Desliga tudo ao fechar a janela
    stream.stop()