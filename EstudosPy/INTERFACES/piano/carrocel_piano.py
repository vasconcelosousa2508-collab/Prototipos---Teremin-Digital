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
    'freq_visual': 261.63, # Nova variável que cria a animação e a inércia!
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
            # Ao soltar, define a frequência alvo de volta para o Dó base para o carrossel recuar
            params['freq'] = 261.63
    except AttributeError: pass
    if key == keyboard.Key.esc:
        app.destroy()
        return False

# --- COMPONENTE: CARROSSEL DESLIZANTE COM INÉRCIA VISUAL ---
class CarrosselDeslizante(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
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
        largura_componente = self.winfo_width()
        if largura_componente <= 1:
            largura_componente = 800 
            
        centro_x = largura_componente / 2
        distancia_entre_notas = 75 # Espaçamento elegante entre as letras
        
        # --- MOTOR DA ANIMAÇÃO (FÍSICA DE INTERPOLAÇÃO) ---
        # A freq_visual corre atrás da freq_alvo de forma suavizada (0.12 dita a velocidade do deslize)
        params['freq_visual'] += 0.12 * (params['freq'] - params['freq_visual'])
        
        # Converte a frequência visual amortecida para a escala contínua de índices
        indice_atual_continuo = 12 * math.log2(params['freq_visual'] / escala_completa[0][1])
            
        # Atualiza a posição física de cada label na fita
        for nome_nota, dados in self.labels_notas.items():
            label = dados['objeto']
            idx_nota = dados['indice_escala']
            
            # Calcula o deslocamento linear baseado na frequência amortecida
            distancia_indices = idx_nota - indice_atual_continuo
            posicao_x = centro_x + (distancia_indices * distancia_entre_notas)
            
            # Distância do centro para aplicar escala e opacidade
            distancia_do_centro = abs(posicao_x - centro_x)
            
            # Fator de foco: 1.0 no centro, vai sumindo conforme se afasta
            fator_foco = 1.0 - (distancia_do_centro / 200)
            fator_foco = max(0.0, min(1.0, fator_foco))
            
            # Curva matemática para o crescimento ficar mais agressivo e lindo no centro
            fator_escala = math.pow(fator_foco, 2)
            
            # Redimensionamento suave da fonte Arial Bold
            tamanho_fonte = int(18 + (28 * fator_escala)) 
            
            # Esmaecimento contínuo da cor (Branco para Roxo de fundo)
            r = int(COR_FUNDO_RGB[0] + (255 - COR_FUNDO_RGB[0]) * fator_foco)
            g = int(COR_FUNDO_RGB[1] + (255 - COR_FUNDO_RGB[1]) * fator_foco)
            b = int(COR_FUNDO_RGB[2] + (255 - COR_FUNDO_RGB[2]) * fator_foco)
            cor_hex = f"#{r:02x}{g:02x}{b:02x}"
            
            # Aplica os resultados visuais gerados pela física
            label.configure(font=("Arial", tamanho_fonte, "bold"), text_color=cor_hex)
            label.place(x=posicao_x, y=45, anchor='center')
            
        # Roda a 60 FPS estáveis para a animação ficar ultra fluida
        self.after(16, self.atualizar_posicoes)

# --- MOLDURA PRINCIPAL ---
class JanelaTeste(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Fita Volante Animada - Visão Teclado/Theremin")
        self.geometry("800x150")
        self.configure(fg_color=COR_FUNDO_HEX)
        
        # Marcador discreto do centro do velocímetro
        self.marcador = ctk.CTkLabel(self, text="▼", font=("Arial", 14), text_color="#3a2575")
        self.marcador.place(x=400, y=12, anchor='center')
        
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