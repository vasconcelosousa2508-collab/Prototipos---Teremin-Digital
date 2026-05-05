# Arduino está enviando dados da leitura de sombra do LRD.

# Configurações da Serial
try:
    porta = serial.Serial('/dev/ttyACM0', 9600, timeout=0.1)
except:
    print("Erro: Verifique se o Arduino está na porta /dev/ttyACM0")
    exit()

# Configurações de Áudio
amostragem = 44100
frequencia = 440.0
volume_atual = 0.0  
fase = 0

limiteSombra = 400

def audio_callback(outdata, frames, time, status):
    global fase, volume_atual
    indices = np.arange(frames) + fase
    # Gerando a onda
    outdata[:, 0] = volume_atual * np.sin(2 * np.pi * frequencia * indices / amostragem)
    fase += frames


while True:
    dados = porta.readline()
    print(dados.decode('utf-8'))

    if int(dados) < limiteSombra:
        volume_atual = 2.0
    else:        volume_atual = 0.0

    with sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem):
        pass