import serial
import numpy as np
import sounddevice as sd
from pynput import keyboard
import customtkinter as ctk
import threading
import math

# --- CONFIGURAÇÕES DO THEREMIN & ARDUINO ---
porta_config = '/dev/ttyACM0' 
amostragem = 44100
limiteDistancia = 30
volumeMaximo = 1.0

# Cores do layout
COR_FUNDO_RGB = (11, 3, 44)       # #0b032c
COR_FUNDO_HEX = '#0b032c'

# Dicionário de parâmetros oficial unificado
params = {
    'freq_alvo': 261.63,
    'freq_atual': 261.63,
    'freq_visual': 261.63, # Mantém a inércia elástica da animação
    'vol_alvo': 0.0,
    'vol_atual': 0.0,        
    'fase': 0.0
}

# Escala fixada no seu Arduino
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

# Escala visual ajustada sem sustenidos
escala_completa = [
    ('C', 261.63),  # Índice 0
    ('D', 293.66),  # Índice 1
    ('E', 329.63),  # Índice 2
    ('F', 349.23),  # Índice 3
    ('G', 392.00),  # Índice 4
    ('A', 440.00),  # Índice 5
    ('B', 493.88),  # Índice 6
    ('C ', 523.25)  # Índice 7
]

# Extrai as listas de frequências e índices para o mapeamento da animação
freqs_escala = [nota[1] for nota in escala_completa]
indices_escala = list(range(len(escala_completa)))

# Conexão de entrada USB
try:
    porta = serial.Serial(porta_config, 9600, timeout=0.05)
except Exception as e:
    print(f"Erro: Verifique se o Arduino está na porta {porta_config}\nDetalhe: {e}")
    exit()

# --- MOTOR DE ÁUDIO DO THEREMIN ---
def audio_callback(outdata, frames, time, status):
    t = np.arange(frames) / amostragem
    
    params['vol_atual'] += 0.1 * (params['vol_alvo'] - params['vol_atual'])
    params['freq_atual'] += 0.08 * (params['freq_alvo'] - params['freq_atual'])
    
    f = params['freq_atual']
    v = params['vol_atual']
    
    arg = 2 * np.pi * f * t + params['fase']
    outdata[:, 0] = v * np.sin(arg)
    
    params['fase'] = (arg[-1] + (2 * np.pi * f / amostragem)) % (2 * np.pi)

# --- TRATAMENTO DOS VALORES DOS SENSORES ---
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
        params['freq_alvo'] = 261.63

# --- THREAD DE LEITURA USB (SERIAL) ---
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
        print(f"\nErro na leitura serial: {e}")
    finally:
        porta.close()

def ao_pressionar(key):
    if key == keyboard.Key.esc:
        app.destroy()
        return False

# --- COMPONENTE: CARROSSEL DESLIZANTE ADAPTADO CORRETAMENTE ---
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
        distancia_entre_notas = 110 # Espaçamento maior e mais limpo
        
        # --- FÍSICA E MOVIMENTO DA FITA ---
        params['freq_visual'] += 0.12 * (params['freq_atual'] - params['freq_visual'])
        
        # CORREÇÃO CRÍTICA: Mapeia de forma contínua a frequência para a nossa escala real de índices (0 a 7)
        indice_atual_continuo = float(np.interp(params['freq_visual'], freqs_escala, indices_escala))
            
        for nome_nota, dados in self.labels_notas.items():
            label = dados['objeto']
            idx_nota = dados['indice_escala']
            
            # Distância baseada no índice real corrigido
            distancia_indices = idx_nota - indice_atual_continuo
            posicao_x = centro_x + (distancia_indices * distancia_entre_notas)
            
            distancia_do_centro = abs(posicao_x - centro_x)
            
            # Efeito de foco (Tamanho e Opacidade)
            fator_foco = 1.0 - (distancia_do_centro / 220)
            fator_foco = max(0.0, min(1.0, fator_foco))
            fator_escala = math.pow(fator_foco, 2)
            
            tamanho_fonte = int(18 + (28 * fator_escala)) 
            
            # Transição suave para o Branco Puro
            r = int(COR_FUNDO_RGB[0] + (255 - COR_FUNDO_RGB[0]) * fator_foco)
            g = int(COR_FUNDO_RGB[1] + (255 - COR_FUNDO_RGB[1]) * fator_foco)
            b = int(COR_FUNDO_RGB[2] + (255 - COR_FUNDO_RGB[2]) * fator_foco)
            cor_hex = f"#{r:02x}{g:02x}{b:02x}"
            
            label.configure(font=("Arial", tamanho_fonte, "bold"), text_color=cor_hex)
            label.place(x=posicao_x, y=45, anchor='center')
            
        self.after(16, self.atualizar_posicoes)

# --- MOLDURA PRINCIPAL DE TESTES ---
class JanelaTeste(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Fita Volante Theremin - Alinhamento Corrigido")
        self.geometry("800x150")
        self.configure(fg_color=COR_FUNDO_HEX)
        
        # Marcador mecânico fixo do centro (Muda para branco para destacar a mira)
        self.marcador = ctk.CTkLabel(self, text="▼", font=("Arial", 14), text_color="#ffffff")
        self.marcador.place(x=400, y=12, anchor='center')
        
        self.carrossel = CarrosselDeslizante(self, width=800, height=120)
        self.carrossel.pack(fill="both", expand=True)

if __name__ == "__main__":
    stream = sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem)
    stream.start()
    
    ouvinte = keyboard.Listener(on_press=ao_pressionar)
    ouvinte.start()
    
    thread_usb = threading.Thread(target=loop_arduino, args=(ouvinte,), daemon=True)
    thread_usb.start()
    
    app = JanelaTeste()
    app.mainloop()
    stream.stop()