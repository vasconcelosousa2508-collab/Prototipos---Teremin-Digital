# Salve como: hud_lateral.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image
from motor import params

plt.rcParams.update({
    "mathtext.fontset": "stix",
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif", "Liberation Serif"]
})

COR_FUNDO_HEX = '#0b032c'
COR_FUNDO_RGB = (11/255, 3/255, 44/255)
COR_DINAMICA = '#eb68a6' 

class HudLateral(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        # border_width=0 e fg_color transparente matam qualquer linha branca residual
        super().__init__(master, border_width=0, fg_color="transparent", **kwargs)
        
        # Estruturas gráficas com tamanhos de canvas bem maiores (Largura 5.5 e Altura 1.4)
        self.fig_d1, self.ax_d1 = self._criar_figura_base(3.5, 1.4)
        self.fig_d2, self.ax_d2 = self._criar_figura_base(3.5, 1.4)
        self.fig_onda, self.ax_onda = self._criar_figura_base(6.0, 1.3)
        
        # Fontes matemáticas do LaTeX aumentadas para 36 e 40!
        self.txt_mat_d1 = self.ax_d1.text(0.5, 0.5, "", color='#ffffff', fontsize=36, va='center', ha='center')
        self.txt_mat_d2 = self.ax_d2.text(0.5, 0.5, "", color='#ffffff', fontsize=36, va='center', ha='center')
        self.txt_mat_onda = self.ax_onda.text(0.5, 0.5, "", color='#ffffff', fontsize=40, va='center', ha='center')

        # --- SENSOR 1 ---
        self.col_esquerda = ctk.CTkFrame(self, border_width=0, fg_color="transparent")
        self.col_esquerda.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=0.42)

        self.lbl_dist1_tit = ctk.CTkLabel(self.col_esquerda, text="Distancia 1", font=("Arial", 28, "bold"), text_color="#ffffff")
        self.lbl_dist1_tit.pack(pady=(10, 5), anchor="center")
        
        self.lbl_dist1_val = ctk.CTkLabel(self.col_esquerda, text="x cm", font=("Arial", 46, "bold"), text_color=COR_DINAMICA)
        self.lbl_dist1_val.pack(pady=(0, 10), anchor="center")

        self.img_eq1_din = ctk.CTkLabel(self.col_esquerda, text="")
        self.img_eq1_din.pack(anchor="center")

        # --- SENSOR 2 ---
        self.col_direita = ctk.CTkFrame(self, border_width=0, fg_color="transparent")
        self.col_direita.place(relx=0.5, rely=0.0, relwidth=0.5, relheight=0.42)

        self.lbl_dist2_tit = ctk.CTkLabel(self.col_direita, text="Distancia 2", font=("Arial", 28, "bold"), text_color="#ffffff")
        self.lbl_dist2_tit.pack(pady=(10, 5), anchor="center")
        
        self.lbl_dist2_val = ctk.CTkLabel(self.col_direita, text="x cm", font=("Arial", 46, "bold"), text_color=COR_DINAMICA)
        self.lbl_dist2_val.pack(pady=(0, 10), anchor="center")

        self.img_eq2_din = ctk.CTkLabel(self.col_direita, text="")
        self.img_eq2_din.pack(anchor="center")

        # --- SEÇÃO INFERIOR ---
        self.col_inferior = ctk.CTkFrame(self, border_width=0, fg_color="transparent")
        self.col_inferior.place(relx=0.0, rely=0.42, relwidth=1.0, relheight=0.58)

        self.img_eq_expl = ctk.CTkLabel(self.col_inferior, text="")
        self.img_eq_expl.pack(pady=(20, 20), anchor="center")

        self.img_onda_fixa = ctk.CTkLabel(self.col_inferior, text="")
        self.img_onda_fixa.pack(pady=10, anchor="center")
        
        self.img_onda_din = ctk.CTkLabel(self.col_inferior, text="")
        self.img_onda_din.pack(pady=10, anchor="center")

        self.gerar_formulas_estaticas()
        self.atualizar_hud()

    def _criar_figura_base(self, largura, altura):
        fig = plt.figure(figsize=(largura, altura), dpi=130)
        fig.patch.set_facecolor(COR_FUNDO_RGB)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor(COR_FUNDO_RGB)
        ax.axis('off')
        return fig, ax

    def _renderizar_texto_rapido(self, fig, txt_obj, texto_latex, largura_final, altura_final):
        txt_obj.set_text(f"$\\mathbf{{\\mathit{{{texto_latex}}}}}$")
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        rgba = canvas.buffer_rgba()
        im = Image.frombuffer("RGBA", canvas.get_width_height(), rgba, "raw", "RGBA", 0, 1)
        return ctk.CTkImage(light_image=im, dark_image=im, size=(largura_final, altura_final))

    def gerar_formulas_estaticas(self):
        fig_exp, ax_exp = self._criar_figura_base(5.5, 1.2)
        ax_exp.text(0.5, 0.5, r"$\mathbf{\mathit{Distancia = \frac{Vel. Som \cdot Tempo}{2}}}$", color='#6e6a86', fontsize=26, va='center', ha='center')
        canvas_exp = FigureCanvasAgg(fig_exp)
        canvas_exp.draw()
        im_exp = Image.frombuffer("RGBA", canvas_exp.get_width_height(), canvas_exp.buffer_rgba(), "raw", "RGBA", 0, 1)
        self.img_eq_expl.configure(image=ctk.CTkImage(im_exp, im_exp, size=(550, 120)))
        plt.close(fig_exp)

        fig_of, ax_of = self._criar_figura_base(5.5, 1.0)
        ax_of.text(0.5, 0.5, r"$\mathbf{\mathit{y = A \cdot \sin(2\pi \cdot f \cdot t)}}$", color='#6e6a86', fontsize=32, va='center', ha='center')
        canvas_of = FigureCanvasAgg(fig_of)
        canvas_of.draw()
        im_of = Image.frombuffer("RGBA", canvas_of.get_width_height(), canvas_of.buffer_rgba(), "raw", "RGBA", 0, 1)
        self.img_onda_fixa.configure(image=ctk.CTkImage(im_of, im_of, size=(550, 100)))
        plt.close(fig_of)

    def atualizar_hud(self):
        d1 = params['leitura1']
        d2 = params['leitura2']

        self.lbl_dist1_val.configure(text=f"{d1} cm" if d1 != 999 else "---")
        self.lbl_dist2_val.configure(text=f"{d2} cm" if d2 != 999 else "---")

        if d1 != 999 and d1 > 0:
            tempo_us1 = int((d1 * 2) / 0.034)
            latex_d1 = rf"d1 = \frac{{340 \cdot {tempo_us1}\mu s}}{{2}}"
        else:
            latex_d1 = r"d1 = \frac{340 \cdot \text{---}\mu s}{2}"
        
        try:
            img_d1 = self._renderizar_texto_rapido(self.fig_d1, self.txt_mat_d1, latex_d1, 350, 140)
            self.img_eq1_din.configure(image=img_d1)

            if d2 != 999 and d2 > 0:
                tempo_us2 = int((d2 * 2) / 0.034)
                latex_d2 = rf"d2 = \frac{{340 \cdot {tempo_us2}\mu s}}{{2}}"
            else:
                latex_d2 = r"d2 = \frac{340 \cdot \text{---}\mu s}{2}"
            img_d2 = self._renderizar_texto_rapido(self.fig_d2, self.txt_mat_d2, latex_d2, 350, 140)
            self.img_eq2_din.configure(image=img_d2)

            vol = params['vol_atual']
            freq = int(params['freq_atual'])
            latex_onda = rf"y = {vol:.2f} \cdot \sin(2\pi \cdot {freq} \cdot t)"
            img_din_onda = self._renderizar_texto_rapido(self.fig_onda, self.txt_mat_onda, latex_onda, 600, 130)
            self.img_onda_din.configure(image=img_din_onda)
        except:
            return

        self.after(45, self.atualizar_hud)