import numpy as np
import sounddevice as sd
from pynput import keyboard
import customtkinter as ctk
import threading

# --- CONFIGURAÇÕES DO SEU MOTOR DE ÁUDIO ---
amostragem = 44100
COR_FUNDO_HEX = '#0b032c'

params = {
    'freq': 0.0,
    'vol_alvo': 0.0,
    'vol_atual': 0.0,
    'fase': 0
}

notas = {
    'a': 261.63, 's': 293.66, 'd': 329.63, 'f': 349.23,
    'g': 392.00, 'h': 440.00, 'j': 493.88, 'k': 523.25,
    'w': 277.18, 'e': 311.13, 'r': 369.99, 't': 415.30, 'y': 466.16  
}

tradutor_notas = {
    'a': 'C',  'w': 'C#', 's': 'D',  'e': 'D#', 'd': 'E', 
    'f': 'F',  'r': 'F#', 'g': 'G',  't': 'G#', 'h': 'A', 
    'y': 'A#', 'j': 'B',  'k': 'C'
}

cores_notas = {
    'C': '#ff005a', 'C#': '#ff4500', 'D': '#ff7d00', 'D#': '#ffa500',
    'E': '#e6ff00', 'F': '#00ff8c', 'F#': '#00ffcc', 'G': '#00ebff',
    'G#': '#26a6ff', 'A': '#508cff', 'A#': '#9400d3', 'B': '#d25aff'
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
        if letra in notas:
            params['freq'] = notas[letra]
            params['vol_alvo'] = 0.8 
    except AttributeError: pass

def ao_soltar(key):
    try:
        letra = key.char
        if letra in notas:
            params['vol_alvo'] = 0.0
    except AttributeError: pass
    if key == keyboard.Key.esc:
        app.destroy()
        return False

# --- MICRO-INTERFACE ---
class MicroCarrosselNotas(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent") 
        
        self.ordem_visual = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        self.labels_notas = {}
        
        for i, nota_musical in enumerate(self.ordem_visual):
            label = ctk.CTkLabel(
                self, 
                text=nota_musical, 
                font=("Impact", 28),         # Fonte de peso pro estilo Synthwave
                text_color="#2a1b5c"         # Cor padrão: apagada (roxo escuro)
            )
            label.grid(row=0, column=i, padx=12, pady=10)
            
            self.labels_notas[nota_musical] = label
            
        self.atualizar_carrossel()

    def atualizar_carrossel(self):
        nota_ativa = None
        if params['vol_atual'] > 0.01:
            for tecla, freq in notas.items():
                if abs(params['freq'] - freq) < 0.01:
                    nota_ativa = tradutor_notas.get(tecla)
                    break
        
        for nota_musical, label in self.labels_notas.items():
            if nota_musical == nota_ativa:
                cor_neon = cores_notas.get(nota_musical, '#ffffff')
                label.configure(text_color=cor_neon, font=("Impact", 42))
            else:
                # SE NÃO FOR: Volta para o estado de repouso apagado
                label.configure(text_color="#2a1b5c", font=("Impact", 28))
                
        # Agenda o próximo frame para daqui a 15 milissegundos
        self.after(15, self.atualizar_carrossel)

# --- MOLDURA PRINCIPAL PARA TESTE ISOLADO ---
class JanelaTeste(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Teste Isolado: Carrossel de Notas")
        self.geometry("650x150")
        self.configure(fg_color=COR_FUNDO_HEX)
        
        # Instancia a nossa micro-interface e centraliza na tela
        self.carrossel = MicroCarrosselNotas(self)
        self.carrossel.pack(expand=True, pady=20)

# --- INICIALIZAÇÃO DO PROGRAMA ---
if __name__ == "__main__":
    # 1. Liga o motor de som
    stream = sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem)
    stream.start()
    
    # 2. Liga o teclado na Thread paralela
    ouvinte = keyboard.Listener(on_press=ao_pressionar, on_release=ao_soltar)
    thread_teclado = threading.Thread(target=ouvinte.start, daemon=True)
    thread_teclado.start()
    
    # 3. Abre a interface de testes
    app = JanelaTeste()
    app.mainloop()
    
    # Desliga o som ao fechar
    stream.stop()