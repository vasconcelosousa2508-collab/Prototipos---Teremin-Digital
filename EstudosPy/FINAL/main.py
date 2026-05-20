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

# Configurações de Aparência do Painel Cyberpunk
COR_FUNDO_HEX = '#0b032c'
ctk.set_appearance_mode("Dark")

class PainelThereminDigital(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configura a janela principal para abrir em alta resolução (Estilo Totem/HUD)
        self.title("IFCE - Theremin Digital & Física Ultrassônica")
        self.geometry("1200x700")
        self.configure(fg_color=COR_FUNDO_HEX)
        
        # Opcional: Descomente a linha abaixo para a apresentação abrir em Tela Cheia automática!
        # self.attributes('-fullscreen', True)

        # ---------------------------------------------------------------------
        # COLUNA DA ESQUERDA (60% da Tela - Interface Visual do Instrumento)
        # ---------------------------------------------------------------------
        self.container_esquerdo = ctk.CTkFrame(self, fg_color="transparent")
        self.container_esquerdo.place(relx=0.0, rely=0.0, relwidth=0.58, relheight=1.0)

        # 1. Componente do Topo: Carrossel Deslizante de Notas
        self.carrossel = CarrosselDeslizante(self.container_esquerdo, width=700, height=120)
        self.carrossel.pack(fill="x", pady=(20, 0), padx=10)
        
        # Marcador visual fixo central (Mira branca "▼")
        self.marcador = ctk.CTkLabel(self.container_esquerdo, text="▼", font=("Arial", 16, "bold"), text_color="#ffffff")
        self.marcador.place(relx=0.5, rely=0.02, anchor='center')

        # 2. Componente do Meio: Osciloscópio Neon da Onda
        self.osciloscopio = OsciloscopioNeon(self.container_esquerdo)
        self.osciloscopio.pack(fill="both", expand=True, pady=10, padx=10)

        # Container Inferior Esquerdo (Para alinhar VU Meter e Hz lado a lado)
        self.base_esquerda = ctk.CTkFrame(self.container_esquerdo, fg_color="transparent")
        self.base_esquerda.pack(fill="x", side="bottom", pady=(0, 30), padx=20)

        # 3. Componente Base-Esquerda: VU Meter (Blocos de Volume)
        self.vu_meter = VuMeterTheremin(self.base_esquerda)
        self.vu_meter.pack(side="left", anchor="s")
        
        # Pequeno ajuste de texto estático abaixo do VU como na imagem
        self.lbl_vol_txt = ctk.CTkLabel(self.vu_meter, text="Vol", font=("Arial", 14, "bold"), text_color="#ffffff")
        self.lbl_vol_txt.pack(side="bottom", anchor="w", padx=15)

        # 4. Componente Base-Direita: Registro de Hz Gigante
        self.mostrador_hz = MostradorFrequencia(self.base_esquerda)
        self.mostrador_hz.pack(side="right", padx=(0, 40), anchor="s")


        # ---------------------------------------------------------------------
        # COLUNA DA DIREITA (42% da Tela - O HUD de Equações Matemáticas)
        # ---------------------------------------------------------------------
        self.container_direito = ctk.CTkFrame(self, fg_color="transparent")
        self.container_direito.place(relx=0.58, rely=0.0, relwidth=0.42, relheight=1.0)

        # Linha vertical divisória sutil para separar os ambientes (Visual Laboratório)
        self.divisor = ctk.CTkFrame(self, width=2, fg_color="#1a0b52")
        self.divisor.place(relx=0.58, rely=0.05, relheight=0.9)

        # 5. Componente Único da Direita: HUD Lateral Matemático
        self.hud_física = HudLateral(self.container_direito)
        self.hud_física.pack(fill="both", expand=True, padx=10, pady=10)


# --- EXECUÇÃO E START CENTRAL DO PROJETO ---
if __name__ == "__main__":
    # 1. Instancia a interface unificada
    app = PainelThereminDigital()

    # 2. Inicializa o motor de geração de áudio senoidal
    stream = motor.iniciar_audio()
    
    # 3. Configura a terminação de emergência segura pelo botão ESC
    def ao_pressionar(key):
        if key == keyboard.Key.esc:
            app.destroy()
            return False

    ouvinte = keyboard.Listener(on_press=ao_pressionar)
    ouvinte.start()
    
    # 4. Conecta na escuta USB do Arduino passando os dados para o motor e HUD
    arduino_serial.iniciar_conexao_arduino(ouvinte)
    
    # 5. Abre a tela e inicia os loops de atualização gráfica assíncronos
    app.mainloop()
    
    # --- Fechamento de Segurança ao Sair ---
    stream.stop()
    plt.close('all') # Desliga instâncias fantasmas do Matplotlib da memória RAM
    print("\n[Theremin] Encerrado com sucesso e conexões fechadas.")