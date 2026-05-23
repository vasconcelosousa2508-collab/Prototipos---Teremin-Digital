import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pynput import keyboard
import sounddevice as sd

import motor
from motor import params, fila_onda, CHUNK

COR_FUNDO_HEX = '#0b032c'

escala_cores = [
    (261.63, (255, 0, 90)),    # Dó - Vermelho Neon
    (293.66, (255, 125, 0)),   # Ré - Laranja Elétrico
    (329.63, (230, 255, 0)),   # Mi - Amarelo Neon
    (349.23, (0, 255, 140)),   # Fá - Verde Mentolado
    (392.00, (0, 235, 255)),   # Sol - Ciano Puro
    (440.00, (80, 140, 255)),  # Lá - Azul Elétrico
    (493.88, (210, 90, 255)),  # Si - Roxo Claro
    (523.25, (255, 0, 190))    # Dó Agudo - Rosa Choque
]

def obter_cor_da_frequencia(freq):
    """Calcula matematicamente a cor exata da linha baseado na frequência atual"""
    if freq <= escala_cores[0][0]:
        r, g, b = escala_cores[0][1]
        return f"#{r:02x}{g:02x}{b:02x}"
    if freq >= escala_cores[-1][0]:
        r, g, b = escala_cores[-1][1]
        return f"#{r:02x}{g:02x}{b:02x}"
        
    for i in range(len(escala_cores) - 1):
        f_inf, cor_inf = escala_cores[i]
        f_sup, cor_sup = escala_cores[i+1]
        
        if f_inf <= freq <= f_sup:
            fator = (freq - f_inf) / (f_sup - f_inf)
            r = int(cor_inf[0] + (cor_sup[0] - cor_inf[0]) * fator)
            g = int(cor_inf[1] + (cor_sup[1] - cor_inf[1]) * fator)
            b = int(cor_inf[2] + (cor_sup[2] - cor_inf[2]) * fator)
            return f"#{r:02x}{g:02x}{b:02x}"
            
    return "#ff005a"


# --- CLASSE ---
class OsciloscopioNeon(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        plt.rcParams['toolbar'] = 'None' 
        
        self.fig, self.ax = plt.subplots(figsize=(10, 3.5))
        self.x = np.arange(0, CHUNK)
        self.line, = self.ax.plot(self.x, np.zeros(CHUNK), '-', lw=3, color='#ff005a') 
        
        self.ax.set_facecolor(COR_FUNDO_HEX)
        self.fig.patch.set_facecolor(COR_FUNDO_HEX)
        self.ax.set_ylim(-1.1, 1.1)
        self.ax.set_xlim(0, CHUNK)
        self.ax.axis('off') 
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.atualizar_onda()

    def atualizar_onda(self):
        dados_da_onda = None
        while not fila_onda.empty():
            dados_da_onda = fila_onda.get()
        
        if dados_da_onda is not None:
            self.line.set_ydata(dados_da_onda)
            
            if params['vol_atual'] > 0.001:
                cor_dinamica = obter_cor_da_frequencia(params['freq_atual'])
                self.line.set_color(cor_dinamica)
            
            try:
                self.canvas.draw_idle() 
            except:
                return 
                
        self.after(16, self.atualizar_onda)


# --- TESTE INDEPENDENTE ---
if __name__ == "__main__":
    import arduino_serial

    # 1. Cria a janela do CustomTkinter
    app = ctk.CTk()
    app.title("Teste Isolado - Osciloscópio Neon")
    app.geometry("800x350")
    app.configure(fg_color=COR_FUNDO_HEX)
    
    # Instancia o osciloscópio direto na tela
    oscilo = OsciloscopioNeon(app)
    oscilo.pack(fill="both", expand=True, padx=10, pady=10)

    # 2. Inicializa as saídas físicas de som
    stream = motor.iniciar_audio()
    
    # 3. Configura a terminação segura por ESC
    def ao_pressionar(key):
        if key == keyboard.Key.esc:
            app.destroy()
            return False

    ouvinte = keyboard.Listener(on_press=ao_pressionar)
    ouvinte.start()
    
    # 4. Conecta no receptor USB do Arduino
    arduino_serial.iniciar_conexao_arduino(ouvinte)
    
    # 5. Roda a interface de teste
    app.mainloop()
    stream.stop()
    plt.close('all') # Fecha os processos do pyplot em background com segurança