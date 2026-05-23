import customtkinter as ctk
from pynput import keyboard
import threading
import sounddevice as sd

from motor import params

COR_FUNDO_RGB = (11, 3, 44)       # #0b032c
COR_FUNDO_HEX = '#0b032c'
COR_ROSA_RGB = (235, 104, 166)    # #eb68a6

# --- CLASSE ---
class VuMeterTheremin(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        self.label = ctk.CTkLabel(self, text="", font=("Arial", 14, "bold"), text_color="#ffffff")
        self.label.pack(pady=(10, 5))
        
        self.frame_vu = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_vu.pack(pady=5)
        
        # 10 blocos
        self.blocos = []
        for i in range(10):
            bloco = ctk.CTkFrame(self.frame_vu, width=25, height=35, corner_radius=4, fg_color=COR_FUNDO_HEX)
            bloco.pack(side="left", padx=3)
            self.blocos.append(bloco)
            
        self.atualizar_visual()

    def calcular_fade_cor(self, vol_atual, inicio_bloco):
        """Calcula a rampa de cor exata para cada bloco individual brilhar no tom certo"""
        fator = (vol_atual - inicio_bloco) / 0.1
        fator = max(0.0, min(1.0, fator)) 
        
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


# --- TESTE INDEPENDENTE ---
if __name__ == "__main__":
    import motor
    import arduino_serial

    # 1. Configura a janela temporária de teste
    app = ctk.CTk()
    app.title("Teste Isolado - VU Meter Volume")
    app.geometry("450x180")
    app.configure(fg_color=COR_FUNDO_HEX)
    
    # Instancia o VU meter diretamente na janela
    vu = VuMeterTheremin(app)
    vu.pack(fill="both", expand=True, pady=20)

    # 2. Inicializa o motor de áudio central
    stream = motor.iniciar_audio()
    
    # 3. Configura o encerramento seguro por ESC
    def ao_pressionar(key):
        if key == keyboard.Key.esc:
            app.destroy()
            return False

    ouvinte = keyboard.Listener(on_press=ao_pressionar)
    ouvinte.start()
    
    # 4. Aciona os sensores do Arduino via cabo serial
    arduino_serial.iniciar_conexao_arduino(ouvinte)
    
    # 5. Roda a interface gráfica
    app.mainloop()
    stream.stop()