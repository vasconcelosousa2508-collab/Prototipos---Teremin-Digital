# Salve como: main.py
import matplotlib.pyplot as plt
import numpy as np
from pynput import keyboard
import customtkinter as ctk

# Importações dos módulos que criamos
import motor
import arduino_serial
from componentes import ComponenteVuMeter, ComponenteCarrossel

# Configurações do Osciloscópio (Matplotlib)
motor.plt.rcParams['toolbar'] = 'None'
fig, ax = plt.subplots(figsize=(10, 3))
fig.canvas.manager.set_window_title('Osciloscópio Cyberpunk - Unificado')

x_dados = np.arange(0, motor.CHUNK)
line, = ax.plot(x_dados, np.zeros(motor.CHUNK), '-', lw=3, color='#ff005a')

ax.set_facecolor(motor.COR_FUNDO_HEX)
fig.patch.set_facecolor(motor.COR_FUNDO_HEX)
ax.set_ylim(-1.1, 1.1)
ax.set_xlim(0, motor.CHUNK)
ax.axis('off')

plt.show(block=False)

escala_cores = [
    (261.63, (255, 0, 90)), (293.66, (255, 125, 0)), (329.63, (230, 255, 0)),
    (349.23, (0, 255, 140)), (392.00, (0, 235, 255)), (440.00, (80, 140, 255)),
    (493.88, (210, 90, 255)), (523.25, (255, 0, 190))
]

def obter_cor_da_frequencia(freq):
    if freq <= escala_cores[0][0]: return f"#{escala_cores[0][1][0]:02x}{escala_cores[0][1][1]:02x}{escala_cores[0][1][2]:02x}"
    if freq >= escala_cores[-1][0]: return f"#{escala_cores[-1][1][0]:02x}{escala_cores[-1][1][1]:02x}{escala_cores[-1][1][2]:02x}"
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

# --- CONSTRUÇÃO DA MOLDURA TKINTER ---
class JanelaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Painel Integrado - IFCE Theremin")
        self.geometry("850x400")
        self.configure(fg_color=motor.COR_FUNDO_HEX)
        
        # Seta do velocímetro
        self.marcador = ctk.CTkLabel(self, text="▼", font=("Arial", 14), text_color="#ffffff")
        self.marcador.pack(pady=(10, 0))
        
        # Instancia Componente 1: Carrossel
        self.carrossel = ComponenteCarrossel(self, width=800, height=120)
        self.carrossel.pack(fill="x", padx=20, pady=5)
        
        # Instancia Componente 2: VU Meter
        self.vu_meter = ComponenteVuMeter(self)
        self.vu_meter.pack(fill="x", padx=20, pady=20)
        
        # Loop do Osciloscópio acoplado ao ciclo do Tkinter
        self.atualizar_osciloscopio()

    def atualizar_osciloscopio(self):
        dados_da_onda = None
        while not motor.fila_onda.empty():
            dados_da_onda = motor.fila_onda.get()
            
        if dados_da_onda is not None:
            line.set_ydata(dados_da_onda)
            if motor.params['vol_atual'] > 0.001:
                cor_dinamica = obter_cor_da_frequencia(motor.params['freq_atual'])
                line.set_color(cor_dinamica)
            try:
                fig.canvas.draw_idle()
                fig.canvas.flush_events()
            except:
                pass
                
        fig.canvas.start_event_loop(0.001)
        self.after(16, self.atualizar_osciloscopio)

def ao_pressionar(key):
    if key == keyboard.Key.esc:
        app.destroy()
        return False

# --- FLUXO PRINCIPAL ---
if __name__ == "__main__":
    # 1. Liga o Áudio
    caixas_de_som = motor.iniciar_audio()
    
    # 2. Configura a terminação segura por teclado
    escutador = keyboard.Listener(on_press=ao_pressionar)
    escutador.start()
    
    # 3. Liga a comunicação do Arduino injetando o escutador
    arduino_serial.iniciar_conexao_arduino(escutador)
    
    # 4. Abre a interface gráfica unificada
    app = JanelaPrincipal()
    app.mainloop()
    
    # Limpeza ao fechar
    caixas_de_som.stop()
    plt.close('all')