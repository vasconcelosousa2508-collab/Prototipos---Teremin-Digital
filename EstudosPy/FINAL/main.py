# Salve como: main.py
import customtkinter as ctk
from pynput import keyboard
import matplotlib.pyplot as plt

import motor
import arduino_serial

from carrocel import CarrosselDeslizante
from onda import OsciloscopioNeon
from vu_meter import VuMeterTheremin
from mostrador_frequencia import MostradorFrequencia
from hud_lateral import HudLateral

COR_FUNDO_HEX = '#0b032c'
ctk.set_appearance_mode("Dark")

class PainelThereminDigital(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("IFCE - Theremin Digital & Física Ultrassônica")
        self.overrideredirect(True) # Ocupa a tela cheia e limpa as barras do Linux
        
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        self.geometry(f"{largura_tela}x{altura_tela}+0+0")
        self.configure(fg_color=COR_FUNDO_HEX)

# ESQUERDA 
        self.container_esquerdo = ctk.CTkFrame(self, border_width=0, fg_color="transparent")
        self.container_esquerdo.place(relx=0.08, rely=0.10, relwidth=0.48, relheight=0.80)

        # Carrossel 
        self.carrossel = CarrosselDeslizante(self.container_esquerdo, width=800, height=180)
        self.carrossel.pack(fill="x", pady=(10, 30))
        
                   # Marcador 
        self.marcador = ctk.CTkLabel(self.container_esquerdo, text="▼", font=("Arial", 32, "bold"), text_color="#ffffff")
        self.marcador.place(relx=0.5, rely=0.01, anchor='center')

        # Osciloscópio 
        self.osciloscopio = OsciloscopioNeon(self.container_esquerdo)
        self.osciloscopio.pack(fill="both", expand=True, pady=(10, 40), padx=5)

        # Container Inferior 
        self.base_esquerda = ctk.CTkFrame(self.container_esquerdo, border_width=0, fg_color="transparent")
        self.base_esquerda.pack(fill="x", side="bottom", pady=(10, 10))

        # Volume 
        self.vu_meter = VuMeterTheremin(self.base_esquerda)
        self.vu_meter.pack(side="left", anchor="s", padx=(10, 0))
        
        self.lbl_vol_txt = ctk.CTkLabel(self.vu_meter, text="VOLUME", font=("Arial", 22, "bold"), text_color="#ffffff")
        self.lbl_vol_txt.pack(side="bottom", anchor="w", padx=15, pady=(10, 0))

        # Hz 
        self.mostrador_hz = MostradorFrequencia(self.base_esquerda)
        self.mostrador_hz.pack(side="right", padx=(0, 20), anchor="s")



# DIREITA 
        self.container_direito = ctk.CTkFrame(self, border_width=0, fg_color="transparent")
        self.container_direito.place(relx=0.62, rely=0.14, relwidth=0.32, relheight=0.72)

        self.divisor = ctk.CTkFrame(self, width=2, fg_color="#1a0b52")
        self.divisor.place(relx=0.59, rely=0.15, relheight=0.70)

        # HUD 
        self.hud_física = HudLateral(self.container_direito)
        self.hud_física.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = PainelThereminDigital()
    stream = motor.iniciar_audio()
    
    def ao_pressionar(key):
        if key == keyboard.Key.esc:
            app.destroy()
            return False

    ouvinte = keyboard.Listener(on_press=ao_pressionar)
    ouvinte.start()
    
    arduino_serial.iniciar_conexao_arduino(ouvinte)
    app.mainloop()
    
    stream.stop()
    plt.close('all')
    print("\n[Theremin] Encerrado com sucesso.")