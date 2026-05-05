import numpy as np
import sounddevice as sd

# Configurações globais
amostragem = 44100
frequencia = 440.0  #  Lá
volume = 3.0
fase = 0  # para o som não estalar

def audio_callback(outdata, frames, time, status):
    #Esta função é chamada pela placa de som toda vez que ela precisa de mais dados
    global fase
    
    # Criamos os índices de tempo para este bloco específico
    indices = np.arange(frames) + fase
    
    # Geramos a onda senoidal pura
    # outdata[:] é o "cano" que vai para a sua caixa de som
    outdata[:, 0] = volume * np.sin(2 * np.pi * frequencia * indices / amostragem)
    
    # Atualizamos a fase para o próximo bloco começar exatamente onde este terminou
    fase += frames

# Abre o fluxo (Stream) de áudio
# O 'with' garante que o som pare quando você fechar o programa
print("Pressione Enter para desligar.")

try:
    with sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem):
        while True:
            # Aqui você pode mudar a frequência em tempo real!
            nova_freq = input("Digite uma nova frequência (ex: 261, 440, 880) ou Enter para sair: ")
            if nova_freq == "":
                break
            frequencia = float(nova_freq)
except Exception as e:
    print(f"Erro: {e}")
    
