# Salve como: hud_lateral.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image
from motor import params

# Configuração robusta de fontes para Linux e Windows
plt.rcParams.update({
    "mathtext.fontset": "stix",  # STIX renderiza fórmulas com estilo Times matemático perfeito
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif", "Liberation Serif"]
})

COR_FUNDO_HEX = '#0b032c'
COR_FUNDO_RGB = (11/255, 3/255, 44/255)
COR_DINAMICA = '#eb68a6' 

class HudLateral(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        # --- PREPARAÇÃO DO MOTOR GRÁFICO (EVITA CRASH DE THREADS) ---
        # Criamos as figuras estáticas e dinâmicas uma única vez na inicialização
        self.fig_d1, self.ax_d1 = self._criar_figura_base(2.4, 0.9)
        self.fig_d2, self.ax_d2 = self._criar_figura_base(2.4, 0.9)
        self.fig_onda, self.ax_onda = self._criar_figura_base(4.2, 0.7)
        
        # Elementos de texto persistentes que apenas terão o conteúdo alterado
        self.txt_mat_d1 = self.ax_d1.text(0.5, 0.5, "", color='#ffffff', fontsize=24, va='center', ha='center')
        self.txt_mat_d2 = self.ax_d2.text(0.5, 0.5, "", color='#ffffff', fontsize=24, va='center', ha='center')
        self.txt_mat_onda = self.ax_onda.text(0.5, 0.5, "", color='#ffffff', fontsize=26, va='center', ha='center')

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

        self.img_eq_expl = ctk.CTkLabel(self.col_inferior, text="")
        self.img_eq_expl.pack(pady=(40, 30), anchor="center")

        self.img_onda_fixa = ctk.CTkLabel(self.col_inferior, text="")
        self.img_onda_fixa.pack(pady=10, anchor="center")
        
        self.img_onda_din = ctk.CTkLabel(self.col_inferior, text="")
        self.img_onda_din.pack(pady=10, anchor="center")

        # Inicializa exibições estáticas e inicia o loop estável
        self.gerar_formulas_estaticas()
        self.atualizar_hud()

    def _criar_figura_base(self, largura, altura):
        """Cria estruturas de canvas invisíveis de forma limpa e isolada da memória gráfica"""
        fig = plt.figure(figsize=(largura, altura), dpi=120)
        fig.patch.set_facecolor(COR_FUNDO_RGB)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor(COR_FUNDO_RGB)
        ax.axis('off')
        return fig, ax

    def _renderizar_texto_rapido(self, fig, txt_obj, texto_latex, largura_final, altura_final):
        """Atualiza o conteúdo interno da equação sem precisar recriar a imagem do zero"""
        txt_obj.set_text(f"$\\mathbf{{\\mathit{{{texto_latex}}}}}$")
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        rgba = canvas.buffer_rgba()
        im = Image.frombuffer("RGBA", canvas.get_width_height(), rgba, "raw", "RGBA", 0, 1)
        return ctk.CTkImage(light_image=im, dark_image=im, size=(largura_final, altura_final))

    def gerar_formulas_estaticas(self):
        """Gera equações fixas usando renderização direta estável de segurança"""
        fig_exp, ax_exp = self._criar_figura_base(4.2, 0.8)
        ax_exp.text(0.5, 0.5, r"$\mathbf{\mathit{Distancia = \frac{Vel. Som \cdot Tempo}{2}}}$", color='#6e6a86', fontsize=20, va='center', ha='center')
        canvas_exp = FigureCanvasAgg(fig_exp)
        canvas_exp.draw()
        im_exp = Image.frombuffer("RGBA", canvas_exp.get_width_height(), canvas_exp.buffer_rgba(), "raw", "RGBA", 0, 1)
        self.img_eq_expl.configure(image=ctk.CTkImage(im_exp, im_exp, size=(420, 80)))
        plt.close(fig_exp)

        fig_of, ax_of = self._criar_figura_base(4.0, 0.6)
        ax_of.text(0.5, 0.5, r"$\mathbf{\mathit{y = A \cdot \sin(2\pi \cdot f \cdot t)}}$", color='#6e6a86', fontsize=24, va='center', ha='center')
        canvas_of = FigureCanvasAgg(fig_of)
        canvas_of.draw()
        im_of = Image.frombuffer("RGBA", canvas_of.get_width_height(), canvas_of.buffer_rgba(), "raw", "RGBA", 0, 1)
        self.img_onda_fixa.configure(image=ctk.CTkImage(im_of, im_of, size=(400, 60)))
        plt.close(fig_of)

    def atualizar_hud(self):
        d1 = params['leitura1']
        d2 = params['leitura2']

        # 1. Labels de texto em centímetros superiores
        self.lbl_dist1_val.configure(text=f"{d1} cm" if d1 != 999 else "---")
        self.lbl_dist2_val.configure(text=f"{d2} cm" if d2 != 999 else "---")

        # 2. Atualização ultra-rápida e segura de D1 sem gerar vazamento de memória
        if d1 != 999 and d1 > 0:
            tempo_us1 = int((d1 * 2) / 0.034)
            latex_d1 = rf"d1 = \frac{{340 \cdot {tempo_us1}\mu s}}{{2}}"
        else:
            latex_d1 = r"d1 = \frac{340 \cdot \text{---}\mu s}{2}"
        
        try:
            img_d1 = self._renderizar_texto_rapido(self.fig_d1, self.txt_mat_d1, latex_d1, 240, 90)
            self.img_eq1_din.configure(image=img_d1)

            # 3. Atualização de D2
            if d2 != 999 and d2 > 0:
                tempo_us2 = int((d2 * 2) / 0.034)
                latex_d2 = rf"d2 = \frac{{340 \cdot {tempo_us2}\mu s}}{{2}}"
            else:
                latex_d2 = r"d2 = \frac{340 \cdot \text{---}\mu s}{2}"
            img_d2 = self._renderizar_texto_rapido(self.fig_d2, self.txt_mat_d2, latex_d2, 240, 90)
            self.img_eq2_din.configure(image=img_d2)

            # 4. Atualização da Equação da Onda Sonora
            vol = params['vol_atual']
            freq = int(params['freq_atual'])
            latex_onda = rf"y = {vol:.2f} \cdot \sin(2\pi \cdot {freq} \cdot t)"
            img_din_onda = self._renderizar_texto_rapido(self.fig_onda, self.txt_mat_onda, latex_onda, 420, 70)
            self.img_onda_din.configure(image=img_din_onda)
        except:
            return # Aborta silenciosamente se a janela estiver fechando para evitar erros no terminal

        # Agenda a próxima renderização estável
        self.after(45, self.atualizar_hud)