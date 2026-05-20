# Salve como: componentes.py
import customtkinter as ctk
import math
import numpy as np
from motor import params

COR_FUNDO_RGB = (11, 3, 44)       # #0b032c
COR_ROSA_RGB = (235, 104, 166)    # #eb68a6

escala_completa = [
    ('C', 261.63), ('D', 293.66), ('E', 329.63), ('F', 349.23),
    ('G', 392.00), ('A', 440.00), ('B', 493.88), ('C ', 523.25)
]
freqs_escala = [nota[1] for nota in escala_completa]
indices_escala = list(range(len(escala_completa)))

# --- COMPONENTE 1: VU METER ---
class ComponenteVuMeter(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        self.label = ctk.CTkLabel(self, text="Volume do Sensor", font=("Arial", 14, "bold"), text_color="#ffffff")
        self.label.pack(pady=(10, 5))
        
        self.frame_vu = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_vu.pack(pady=5)
        
        self.blocos = []
        for i in range(10):
            bloco = ctk.CTkFrame(self.frame_vu, width=25, height=35, corner_radius=4, fg_color="#0b032c")
            bloco.pack(side="left", padx=3)
            self.blocos.append(bloco)
            
        self.atualizar_visual()

    def calcular_fade_cor(self, vol_atual, inicio_bloco):
        fator = (vol_atual - inicio_bloco) / 0.1
        fator = max(0.0, min(1.0, faktor:=fator)) 
        r = int(COR_FUNDO_RGB[0] + (COR_ROSA_RGB[0] - COR_FUNDO_RGB[0]) * fator)
        g = int(COR_FUNDO_RGB[1] + (COR_ROSA_RGB[1] - COR_FUNDO_RGB[1]) * fator)
        b = int(COR_FUNDO_RGB[2] + (COR_ROSA_RGB[2] - COR_FUNDO_RGB[2]) * fator)
        return f"#{r:02x}{g:02x}{b:02x}"

    def atualizar_visual(self):
        vol_atual = params['vol_atual']
        for i in range(10):
            inicio_bloco = i * 0.1
            nova_cor = self.calcular_fade_cor(vol_atual, inicio_bloco)
            self.blocos[i].configure(fg_color=nova_cor)
        self.after(15, self.atualizar_visual)

# --- COMPONENTE 2: CARROSSEL DESLIZANTE ---
class ComponenteCarrossel(ctk.CTkFrame):
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
        distancia_entre_notas = 110 
        
        params['freq_visual'] += 0.12 * (params['freq_atual'] - params['freq_visual'])
        indice_atual_continuo = float(np.interp(params['freq_visual'], freqs_escala, indices_escala))
            
        for nome_nota, dados in self.labels_notas.items():
            label = dados['objeto']
            idx_nota = dados['indice_escala']
            
            distancia_indices = idx_nota - indice_atual_continuo
            posicao_x = centro_x + (distancia_indices * distancia_entre_notas)
            distancia_do_centro = abs(posicao_x - centro_x)
            
            fator_foco = 1.0 - (distancia_do_centro / 220)
            fator_foco = max(0.0, min(1.0, fator_foco))
            fator_escala = math.pow(fator_foco, 2)
            
            tamanho_fonte = int(18 + (28 * fator_escala)) 
            
            r = int(COR_FUNDO_RGB[0] + (255 - COR_FUNDO_RGB[0]) * fator_foco)
            g = int(COR_FUNDO_RGB[1] + (255 - COR_FUNDO_RGB[1]) * fator_foco)
            b = int(COR_FUNDO_RGB[2] + (255 - COR_FUNDO_RGB[2]) * fator_foco)
            cor_hex = f"#{r:02x}{g:02x}{b:02x}"
            
            label.configure(font=("Arial", tamanho_fonte, "bold"), text_color=cor_hex)
            label.place(x=posicao_x, y=45, anchor='center')
            
        self.after(16, self.atualizar_posicoes)