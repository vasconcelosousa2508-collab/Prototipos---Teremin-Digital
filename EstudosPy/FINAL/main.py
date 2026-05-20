# Salve como: main.py
import customtkinter as ctk
from pynput import keyboard
import matplotlib.pyplot as plt

# Importa o motor de áudio e a serial
import motor
import arduino_serial

# Importa a sua coleção de componentes modulares
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
        
        # ---------------------------------------------------------------------
        # CONFIGURAÇÃO DE TELA CHEIA ABSOLUTA (ESTILO TOTEM/KIOSK)
        # ---------------------------------------------------------------------
        # Remove a barra de título superior, botões de fechar/minimizar e bordas
        self.overrideredirect(True)
        
        # Descobre a resolução exata do seu monitor atual de forma dinâmica
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        
        # Força a janela a ocupar as dimensões exatas do monitor
        self.geometry(f"{largura_tela}x{altura_tela}+0+0")
        self.configure(fg_color=COR_FUNDO_HEX)

        # ---------------------------------------------------------------------
        # COLUNA DA ESQUERDA (60% da Tela - Interface Visual)
        # ---------------------------------------------------------------------
        # Adicionamos padding interno (margem) para os componentes não colarem nos cantos da tela
        self.container_esquerdo = ctk.CTkFrame(self, fg_color="transparent")
        self.container_esquerdo.place(relx=0.03, rely=0.04, relwidth=0.54, relheight=0.92)

        # 1. Componente do Topo: Carrossel Deslizante de Notas
        # Aumentamos o tamanho vertical (height=140) para preencher melhor telas grandes
        self.carrossel = CarrosselDeslizante(self.container_esquerdo, width=750, height=140)
        self.carrossel.pack(fill="x", pady=(10, 20))
        
        # Marcador visual fixo central (Mira branca "▼")
        self.marcador = ctk.CTkLabel(self.container_esquerdo, text="▼", font=("Arial", 20, "bold"), text_color="#ffffff")
        self.marcador.place(relx=0.5, rely=0.01, anchor='center')

        # 2. Componente do Meio: Osciloscópio Neon da Onda (Ganha mais destaque vertical)
        self.osciloscopio = OsciloscopioNeon(self.container_esquerdo)
        self.osciloscopio.pack(fill="both", expand=True, pady=(10, 30))

        # Container Inferior Esquerdo (Para alinhar VU Meter e Hz lado a lado)
        self.base_esquerda = ctk.CTkFrame(self.container_esquerdo, fg_color="transparent")
        self.base_esquerda.pack(fill="x", side="bottom", pady=(10, 10))

        # 3. Componente Base-Esquerda: VU Meter (Blocos de Volume)
        self.vu_meter = VuMeterTheremin(self.base_esquerda)
        self.vu_meter.pack(side="left", anchor="s", padx=(20, 0))
        
        self.lbl_vol_txt = ctk.CTkLabel(self.vu_meter, text="Vol", font=("Arial", 16, "bold"), text_color="#ffffff")
        self.lbl_vol_txt.pack(side="bottom", anchor="w", padx=15, pady=(5, 0))

        # 4. Componente Base-Direita: Registro de Hz Gigante
        self.mostrador_hz = MostradorFrequencia(self.base_esquerda)
        self.mostrador_hz.pack(side="right", padx=(0, 40), anchor="s")


        # ---------------------------------------------------------------------
        # COLUNA DA DIREITA (38% da Tela - O HUD de Equações Matemáticas)
        # ---------------------------------------------------------------------
        self.container_direito = ctk.CTkFrame(self, fg_color="transparent")
        self.container_direito.place(relx=0.60, rely=0.04, relwidth=0.37, relheight=0.92)

        # Linha vertical divisória elegante com uma cor neon sutil
        self.divisor = ctk.CTkFrame(self, width=2, fg_color="#1a0b52")
        self.divisor.place(relx=0.59, rely=0.06, relheight=0.88)

        # 5. Componente Único da Direita: HUD Lateral Matemático
        self.hud_física = HudLateral(self.container_direito)
        self.hud_física.pack(fill="both", expand=True)


# --- EXECUÇÃO E START CENTRAL DO PROJETO ---
if __name__ == "__main__":
    app = PainelThereminDigital()

    stream = motor.iniciar_audio()
    
    # Função de pânico/fechamento: Como não há botão "X" na janela, o ESC é vital!
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
    print("\n[Theremin] Encerrado com sucesso e conexões fechadas.")