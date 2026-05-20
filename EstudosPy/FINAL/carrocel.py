import customtkinter as ctk
import math
import numpy as np
from pynput import keyboard
import threading
import sounddevice as sd

from motor import params

# Cores do layout
COR_FUNDO_RGB = (11, 3, 44)       # #0b032c
COR_FUNDO_HEX = '#0b032c'

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

#  cálculo de interpolação linear da física do movimento
freqs_escala = [nota[1] for nota in escala_completa]
indices_escala = list(range(len(escala_completa)))

# --- CLASSE ---
class CarrosselDeslizante(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        self.labels_notas = {}
        
        # texto
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
        distancia_entre_notas = 110  
        
        params['freq_visual'] += 0.12 * (params['freq_atual'] - params['freq_visual'])
        
        indice_atual_continuo = float(np.interp(params['freq_visual'], freqs_escala, indices_escala))
            
        for nome_nota, dados in self.labels_notas.items():
            label = dados['objeto']
            idx_nota = dados['indice_escala']
            
            # posição X com base no índice mapeado
            distancia_indices = idx_nota - indice_atual_continuo
            posicao_x = centro_x + (distancia_indices * distancia_entre_notas)
            
            distancia_do_centro = abs(posicao_x - centro_x)
            
            # foco óptico 
            fator_foco = 1.0 - (distancia_do_centro / 220)
            fator_foco = max(0.0, min(1.0, fator_foco))
            fator_escala = math.pow(fator_foco, 2)
            
            tamanho_fonte = int(18 + (28 * fator_escala)) 
            
            # Fade 
            r = int(COR_FUNDO_RGB[0] + (255 - COR_FUNDO_RGB[0]) * fator_foco)
            g = int(COR_FUNDO_RGB[1] + (255 - COR_FUNDO_RGB[1]) * fator_foco)
            b = int(COR_FUNDO_RGB[2] + (255 - COR_FUNDO_RGB[2]) * fator_foco)
            cor_hex = f"#{r:02x}{g:02x}{b:02x}"
            
            label.configure(font=("Arial", tamanho_fonte, "bold"), text_color=cor_hex)
            label.place(x=posicao_x, y=45, anchor='center')
            
        #  60 FPS (1000ms / 60 ≈ 16.67ms)
        self.after(16, self.atualizar_posicoes)


# --- TESTE INDEPENDENTE ---
if __name__ == "__main__":
    import motor
    import arduino_serial

    # 1. Cria a janela temporária de testes
    app = ctk.CTk()
    app.title("Teste Isolado - Carrossel Deslizante")
    app.geometry("800x150")
    app.configure(fg_color=COR_FUNDO_HEX)
    
    # Marcador fixo central (Mira branca)
    marcador = ctk.CTkLabel(app, text="▼", font=("Arial", 14), text_color="#ffffff")
    marcador.place(x=400, y=12, anchor='center')
    
    # Instancia o carrossel direto na janela
    carrossel = CarrosselDeslizante(app, width=800, height=120)
    carrossel.pack(fill="both", expand=True)

    # 2. Inicia o motor de áudio de background
    stream = motor.iniciar_audio()
    
    # 3. Configura a saída pelo botão ESC
    def ao_pressionar(key):
        if key == keyboard.Key.esc:
            app.destroy()
            return False

    ouvinte = keyboard.Listener(on_press=ao_pressionar)
    ouvinte.start()
    
    # 4. Conecta na leitura serial do Arduino
    arduino_serial.iniciar_conexao_arduino(ouvinte)
    
    # 5. Executa a interface gráfica
    app.mainloop()
    stream.stop()