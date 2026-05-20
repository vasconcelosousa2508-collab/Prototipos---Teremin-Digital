# Salve como: hud_lateral.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image
from motor import params

# Configura globalmente o Matplotlib para usar a fonte matemática como Times New Roman
plt.rcParams.update({
    "mathtext.fontset": "stix",  # Clone perfeito da Times New Roman para equações
    "font.family": "serif",
    "font.serif": ["Times New Roman"]
})

COR_FUNDO_HEX = '#0b032c'
COR_FUNDO_RGB = (11/255, 3/255, 44/255)
COR_DINAMICA = '#eb68a6' 

class HudLateral(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        # --- COLUNA DA ESQUERDA (SENSOR 1 - VOLUME) ---
        self.col_esquerda = ctk.CTkFrame(self, fg_color="transparent")
        self.col_esquerda.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=0.40)

        self.lbl_dist1_tit = ctk.CTkLabel(self.col_esquerda, text="Distancia 1", font=("Arial", 22, "bold"), text_color="#ffffff")
        self.lbl_dist1_tit.pack(pady=(20, 5), anchor="center")
        
        self.lbl_dist1_val = ctk.CTkLabel(self.col_esquerda, text="x cm", font=("Arial", 32, "bold"), text_color=COR_DINAMICA)
        self.lbl_dist1_val.pack(pady=(0, 15), anchor="center")

        self.img_eq1_din = ctk.CTkLabel(self.col_esquerda, text="")
        self.img_eq1_din.pack(anchor="center")

        # --- COLUNA DA DIREITA (SENSOR 2 - NOTA) ---
        self.col_direita = ctk.CTkFrame(self, fg_color="transparent")
        self.col_direita.place(relx=0.5, rely=0.0, relwidth=0.5, relheight=0.40)

        self.lbl_dist2_tit = ctk.CTkLabel(self.col_direita, text="Distancia 2", font=("Arial", 22, "bold"), text_color="#ffffff")
        self.lbl_dist2_tit.pack(pady=(20, 5), anchor="center")
        
        self.lbl_dist2_val = ctk.CTkLabel(self.col_direita, text="x cm", font=("Arial", 32, "bold"), text_color=COR_DINAMICA)
        self.lbl_dist2_val.pack(pady=(0, 15), anchor="center")

        self.img_eq2_din = ctk.CTkLabel(self.col_direita, text="")
        self.img_eq2_din.pack(anchor="center")

        # --- SEÇÃO INFERIOR: EQUAÇÕES DA ONDA ---
        self.col_inferior = ctk.CTkFrame(self, fg_color="transparent")
        self.col_inferior.place(relx=0.0, rely=0.40, relwidth=1.0, relheight=0.60)

        # Texto explicativo estático cinza (Distancia = Vel. Som . Tempo / 2)
        self.img_eq_expl = ctk.CTkLabel(self.col_inferior, text="")
        self.img_eq_expl.pack(pady=(40, 30), anchor="center")

        # y = A . sin(2pi . f . t) estática em cinza
        self.img_onda_fixa = ctk.CTkLabel(self.col_inferior, text="")
        self.img_onda_fixa.pack(pady=10, anchor="center")
        
        # y = A . sin(2pi . f . t) dinâmica em branco e negrito
        self.img_onda_din = ctk.CTkLabel(self.col_inferior, text="")
        self.img_onda_din.pack(pady=10, anchor="center")

        # Inicializa as renderizações estáticas
        self.gerar_formulas_estaticas()
        
        # Dispara o loop de atualização em tempo real
        self.atualizar_hud()

    def latex_para_ctk_image(self, formula_latex, cor_texto, tamanho_fonte=24, largura_img=420, altura_img=90):
        """Transforma códigos LaTeX em imagens de alta resolução (Sem borrar)"""
        fig = plt.figure(figsize=(largura_img/100, altura_img/100), dpi=120) # Aumentado o DPI para nitidez máxima
        fig.patch.set_facecolor(COR_FUNDO_RGB)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor(COR_FUNDO_RGB)
        ax.axis('off')

        ax.text(0.5, 0.5, f"$\\mathbf{{\\mathit{{{formula_latex}}}}}$", 
                color=cor_texto, 
                fontsize=tamanho_fonte, 
                va='center', 
                ha='center')

        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        rgba = canvas.buffer_rgba()
        
        im = Image.frombuffer("RGBA", canvas.get_width_height(), rgba, "raw", "RGBA", 0, 1)
        plt.close(fig)
        
        return ctk.CTkImage(light_image=im, dark_image=im, size=(largura_img, altura_img))

    def gerar_formulas_estaticas(self):
        """Gera os elementos de texto fixos na parte inferior da tela em tamanho grande"""
        # Distancia = (Vel. Som . Tempo) / 2
        formula_explicativa = r"\mathit{\mathbf{Distancia}} = \frac{\mathit{\mathbf{Vel. Som}} \cdot \mathit{\mathbf{Tempo}}}{2}"
        img_fixa = self.latex_para_ctk_image(formula_explicativa, cor_texto='#6e6a86', tamanho_fonte=20, largura_img=420, altura_img=80)
        self.img_eq_expl.configure(image=img_fixa)

        # y = A . sin(2pi . f . t) estática em cinza
        formula_onda_cinza = r"y = A \cdot \sin(2\pi \cdot f \cdot t)"
        img_onda_f = self.latex_para_ctk_image(formula_onda_cinza, cor_texto='#6e6a86', tamanho_fonte=24, largura_img=400, altura_img=60)
        self.img_onda_fixa.configure(image=img_onda_f)

    def atualizar_hud(self):
        d1 = params['leitura1']
        d2 = params['leitura2']

        # 1. Atualiza as distâncias nos labels superiores (Tamanho de destaque 32)
        self.lbl_dist1_val.configure(text=f"{d1} cm" if d1 != 999 else "---")
        self.lbl_dist2_val.configure(text=f"{d2} cm" if d2 != 999 else "---")

        # 2. EQUAÇÃO DINÂMICA D1
        if d1 != 999 and d1 > 0:
            tempo_us1 = int((d1 * 2) / 0.034)
            latex_d1 = rf"d1 = \frac{{340 \cdot {tempo_us1}\mu s}}{{2}}"
        else:
            latex_d1 = r"d1 = \frac{340 \cdot \text{---}\mu s}{2}"
        img_d1 = self.latex_para_ctk_image(latex_d1, cor_texto='#ffffff', tamanho_fonte=24, largura_img=240, altura_img=90)
        self.img_eq1_din.configure(image=img_d1)

        # 3. EQUAÇÃO DINÂMICA D2
        if d2 != 999 and d2 > 0:
            tempo_us2 = int((d2 * 2) / 0.034)
            latex_d2 = rf"d2 = \frac{{340 \cdot {tempo_us2}\mu s}}{{2}}"
        else:
            latex_d2 = r"d2 = \frac{340 \cdot \text{---}\mu s}{2}"
        img_d2 = self.latex_para_ctk_image(latex_d2, cor_texto='#ffffff', tamanho_fonte=24, largura_img=240, altura_img=90)
        self.img_eq2_din.configure(image=img_d2)

        # 4. EQUAÇÃO DINÂMICA DA ONDA (y = A . sin(2pi . f . t))
        vol = params['vol_atual']
        freq = int(params['freq_atual'])
        latex_onda = rf"y = {vol:.2f} \cdot \sin(2\pi \cdot {freq} \cdot t)"
        img_din_onda = self.latex_para_ctk_image(latex_onda, cor_texto='#ffffff', tamanho_fonte=26, largura_img=420, altura_img=70)
        self.img_onda_din.configure(image=img_din_onda)

        self.after(40, self.atualizar_hud)


# --- SCRIPT DE TESTE RE-ESTILIZADO PARA TELA CHEIA ---
if __name__ == "__main__":
    import motor
    from pynput import keyboard

    app = ctk.CTk()
    app.title("HUD Lateral - Versão Painel Gigante")
    # Agora simulamos ele ocupando metade de uma tela Full HD (600x700)
    app.geometry("550x700")
    app.configure(fg_color=COR_FUNDO_HEX)

    hud = HudLateral(app)
    hud.pack(fill="both", expand=True, padx=20, pady=20)

    stream = motor.iniciar_audio()
    def ao_pressionar(key):
        if key == keyboard.Key.esc:
            app.destroy()
            return False
    ouvinte = keyboard.Listener(on_press=ao_pressionar)
    ouvinte.start()
    
    try:
        iniciar_conexao_arduino = __import__('arduino_serial').iniciar_conexao_arduino
        iniciar_conexao_arduino(ouvinte)
    except:
        pass

    app.mainloop()
    stream.stop()