import customtkinter as ctk
from pynput import keyboard
import sounddevice as sd

from motor import params

COR_FUNDO_HEX = '#0b032c'

# --- CLASSE ---
class MostradorFrequencia(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        self.conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.conteudo.pack(expand=True)
        
        self.label_numero = ctk.CTkLabel(
            self.conteudo, 
            text="000.00", 
            font=("Arial", 48, "bold"), 
            text_color="#ffffff"
        )
        self.label_numero.pack(pady=(0, 0))
        
        self.label_unidade = ctk.CTkLabel(
            self.conteudo, 
            text="FREQUÊNCIA (Hz)", 
            font=("Arial", 11, "bold"), 
            text_color="#00ebff" 
        )
        self.label_unidade.pack(pady=(0, 0))
        
        self.atualizar_frequencia()

    def atualizar_frequencia(self):
        freq_atual = params['freq_atual']
        
        self.label_numero.configure(text=f"{freq_atual:.2f}")
        
        self.after(16, self.atualizar_frequencia)


# --- TESTE INDEPENDENTE ---
if __name__ == "__main__":
    import motor
    import arduino_serial

    # 1. Configura a janela de testes isolada
    app = ctk.CTk()
    app.title("Teste Isolado - Mostrador de Frequência")
    app.geometry("400x200")
    app.configure(fg_color=COR_FUNDO_HEX)
    
    # Instancia o mostrador centralizado na janela de teste
    mostrador = MostradorFrequencia(app)
    mostrador.pack(fill="both", expand=True, pady=40)

    # 2. Inicializa o motor de áudio centralizado
    stream = motor.iniciar_audio()
    
    # 3. Configura o encerramento seguro ao pressionar ESC
    def ao_pressionar(key):
        if key == keyboard.Key.esc:
            app.destroy()
            return False

    ouvinte = keyboard.Listener(on_press=ao_pressionar)
    ouvinte.start()
    
    # 4. Inicia a escuta da porta USB do Arduino
    arduino_serial.iniciar_conexao_arduino(ouvinte)
    
    # 5. Roda a interface gráfica de testes
    app.mainloop()
    stream.stop()