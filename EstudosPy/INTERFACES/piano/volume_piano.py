import numpy as np
import sounddevice as sd
from pynput import keyboard
import customtkinter as ctk
import threading
import time

# --- CORES  ---
COR_FUNDO_RGB = (11, 3, 44)       #0b032c
COR_ROSA_RGB = (235, 104, 166)     #eb68a6

# --- ENGINE ---
amostragem = 44100
params = {
    'freq': 0.0,
    'vol_alvo': 0.0,
    'vol_atual': 0.0,
    'vol_maximo': 1.0,
    'fase': 0
}

notas = {
    'a': 261.63, 's': 293.66, 'd': 329.63, 'f': 349.23,
    'g': 392.00, 'h': 440.00, 'j': 493.88, 'k': 523.25,
    'w': 277.18, 'e': 311.13, 'r': 369.99, 't': 415.30, 'y': 466.16  
}

volumes = {
    '1': 0.1, '2': 0.2, '3': 0.3, '4': 0.4, '5': 0.5, '6': 0.6, '7': 0.7, '8': 0.8, '9': 0.9, '0': 1.0,
    'z': 0.15, 'x': 0.25, 'c': 0.35, 'v': 0.45, 'b': 0.55, 'n': 0.65, 'm': 0.75, ',': 0.85, '.': 0.95, '/': 0.0
} 

def audio_callback(outdata, frames, time_info, status):
    indices = np.arange(frames) + params['fase']
    params['vol_atual'] += 0.1 * (params['vol_alvo'] - params['vol_atual'])
    onda = params['vol_atual'] * np.sin(2 * np.pi * params['freq'] * indices / amostragem)
    outdata[:, 0] = onda
    params['fase'] += frames

def ao_pressionar(key):
    try:
        letra = key.char
        if letra in volumes:
            params['vol_maximo'] = volumes[letra]
        elif letra in notas:
            params['freq'] = notas[letra]
            params['vol_alvo'] = params['vol_maximo']
    except AttributeError: pass

def ao_soltar(key):
    try: 
        if key.char in notas:
            params['vol_alvo'] = 0.0
    except AttributeError: pass
    if key == keyboard.Key.esc:
        app.destroy() 
        return False

# --- FADE ---
def calcular_fade_cor(vol_atual, inicio_bloco):
    #o quanto o volume preencheu este bloco  (0.0 a 1.0)
    fator = (vol_atual - inicio_bloco) / 0.1
    fator = max(0.0, min(1.0, fator)) # entre 0 e 1
    
    # Mistura dos canais R, G, B baseado no fator
    r = int(COR_FUNDO_RGB[0] + (COR_ROSA_RGB[0] - COR_FUNDO_RGB[0]) * fator)
    g = int(COR_FUNDO_RGB[1] + (COR_ROSA_RGB[1] - COR_FUNDO_RGB[1]) * fator)
    b = int(COR_FUNDO_RGB[2] + (COR_ROSA_RGB[2] - COR_FUNDO_RGB[2]) * fator)
    
    return f"#{r:02x}{g:02x}{b:02x}"

# --- CONSTRUTOR ---
class BarraVolumeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Protótipo VU Meter")
        self.geometry("450x200")
        self.configure(fg_color="#0b032c") 
        
        # Texto indicador
        self.label = ctk.CTkLabel(self, text="Vol", font=("Arial", 14, "bold"), text_color="#ffffff")
        self.label.pack(pady=(40, 5))
        
        # Frame horizontal ==> 10 blocos
        self.frame_vu = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_vu.pack(pady=10)
        
        # dinamico
        self.blocos = []
        for i in range(10):
            bloco = ctk.CTkFrame(self.frame_vu, width=25, height=35, corner_radius=4, fg_color="#0b032c")
            bloco.pack(side="left", padx=3)
            self.blocos.append(bloco)
            
        # atualização tempo real
        self.atualizar_visual()

    def atualizar_visual(self):
        vol_atual = params['vol_atual']
        
        # a cada 10 blocos mudando cor 
        for i in range(10):
            inicio_bloco = i * 0.1
            nova_cor = calcular_fade_cor(vol_atual, inicio_bloco)
            self.blocos[i].configure(fg_color=nova_cor)
            
        
        self.after(15, self.atualizar_visual)

# --- PROGRAMA ---
if __name__ == "__main__":
    # som
    stream = sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem)
    stream.start()
    
    # teclado em uma Thread paralela 
    ouvinte = keyboard.Listener(on_press=ao_pressionar, on_release=ao_soltar)
    thread_teclado = threading.Thread(target=ouvinte.start, daemon=True)
    thread_teclado.start()
    
    # ctk
    app = BarraVolumeApp()
    app.mainloop()
    
    # Desliga o som 
    stream.stop()
