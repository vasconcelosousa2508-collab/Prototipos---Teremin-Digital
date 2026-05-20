import numpy as np
import sounddevice as sd
from pynput import keyboard
import customtkinter as ctk
import threading
import math

# --- CONFIGURAÇÕES DO MOTOR ---
amostragem = 44100
COR_FUNDO_RGB = (11, 3, 44)       # #0b032c
COR_FUNDO_HEX = '#0b032c'

params = {
    'freq': 261.63, 
    'vol_alvo': 0.0,
    'vol_atual': 0.0,
    'fase': 0
}

notas = {
    'a': 261.63, 's': 293.66, 'd': 329.63, 'f': 349.23,
    'g': 392.00, 'h': 440.00, 'j': 493.88, 'k': 523.25,
    'w': 277.18, 'e': 311.13, 'r': 369.99, 't': 415.30, 'y': 466.16  
}

escala_completa = [
    ('C', 261.63), ('C#', 277.18), ('D', 293.66), ('D#', 311.13),
    ('E', 329.63), ('F', 349.23), ('F#', 369.99), ('G', 392.00),
    ('G#', 415.30), ('A', 440.00), ('A#', 466.16), ('B', 493.88),
    ('C ', 523.25)
]

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

# --- COMPONENTE: CARROSSEL DESLIZANTE CINEMÁTICO ---
class CarrosselDeslizante(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        # Guardamos a posição indexada de cada nota (0 a 12)
        self.labels_notas = {}
        
        for i, (nome_nota, freq_alvo) in enumerate(escala_completa):
            label = ctk.CTkLabel(self, text=nome_nota, font=("Arial", 18, "bold"))
            self.labels_notas[nome_nota] = {
                'objeto': label,
                'frequencia': freq_alvo,
                'indice_escala': i
            }
            
        self.atualizar_posicoes()

    def atualizar_posicoes(self):
        # Largura total disponível para o componente se mover
        largura_componente = self.winfo_width()
        
        # Evita rodar o cálculo antes da janela abrir e medir a largura real
        if largura_componente <= 1:
            largura_componente = 800 
            
        centro_x = largura_componente / 2
        distancia_entre_notas = 70 # Distância em pixels entre cada letra na fita
        
        freq_atual = params['freq']
        vol_atual = params['vol_atual']
        
        # 1. Descobre onde a frequência atual está na nossa escala indexada (0.0 a 12.0)
        # Se nenhuma nota estiver tocando, a fita descansa no centro da primeira nota (Dó)
        indice_atual_continuo = 0.0
        if freq_atual > 0:
            # Encontra a posição contínua baseada no logaritmo musical
            # Isso garante que se a freq estiver entre C e D, o índice vai ser tipo 0.5
            indice_atual_continuo = 12 * math.log2(freq_atual / escala_completa[0][1])
            
        # 2. Atualiza a posição física, tamanho e opacidade de cada nota baseado no deslize
        for nome_nota, dados in self.labels_notas.items():
            label = dados['objeto']
            idx_nota = dados['indice_escala']
            
            # Distância física relativa do índice atual
            distancia_indices = idx_nota - indice_atual_continuo
            
            # Multiplica a distância pelo espaçamento em pixels para achar o X na tela
            posicao_x = centro_x + (distancia_indices * distancia_entre_notas)
            
            # --- CÁLCULO DE DESTAQUE (TAMANHO E OPACIDADE) ---
            # Quanto mais perto do centro_x, maior o fator (1.0 no centro, 0.0 nas bordas)
            distancia_do_centro = abs(posicao_x - centro_x)
            
            # Notas somem/encolhem completamente se passarem de 180 pixels do centro
            fator_foco = 1.0 - (distancia_do_centro / 180)
            fator_foco = max(0.0, min(1.0, fator_foco))
            
            # Ajuste de tamanho dinâmico (Arial Bold Branca)
            tamanho_fonte = int(18 + (26 * fator_foco)) # Vai de 18 a 44 conforme chega no centro
            
            # --- EFEITO DE OPACIDADE (BRANCO PARA ROXO ESCURO) ---
            # Cor alvo: Branco Puro (255, 255, 255)
            r = int(COR_FUNDO_RGB[0] + (255 - COR_FUNDO_RGB[0]) * fator_foco)
            g = int(COR_FUNDO_RGB[1] + (255 - COR_FUNDO_RGB[1]) * fator_foco)
            b = int(COR_FUNDO_RGB[2] + (255 - COR_FUNDO_RGB[2]) * fator_foco)
            cor_hex = f"#{r:02x}{g:02x}{b:02x}"
            
            # Modifica as propriedades visuais
            label.configure(font=("Arial", tamanho_fonte, "bold"), text_color=cor_hex)
            
            # Move fisicamente a nota na tela (centralizando o texto usando anchor='center')
            label.place(x=posicao_x, y=40, anchor='center')
            
        self.after(15, self.atualizar_posicoes)

# --- MOLDURA PRINCIPAL ---
class JanelaTeste(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Carrossel Mecânico Deslizante")
        self.geometry("800x150")
        self.configure(fg_color=COR_FUNDO_HEX)
        
        # Marcador fixo central (opcional, só para mostrar onde é o centro perfeito)
        self.marcador = ctk.CTkLabel(self, text="▼", font=("Arial", 16), text_color="#3a2575")
        self.marcador.place(x=400, y=10, anchor='center')
        
        self.carrossel = CarrosselDeslizante(self, width=800, height=120)
        self.carrossel.pack(fill="both", expand=True)

if __name__ == "__main__":
    stream = sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem)
    stream.start()
    
    ouvinte = keyboard.Listener(on_press=ao_pressionar, on_release=ao_soltar)
    threading.Thread(target=ouvinte.start, daemon=True).start()
    
    app = JanelaTeste()
    app.mainloop()
    stream.stop()