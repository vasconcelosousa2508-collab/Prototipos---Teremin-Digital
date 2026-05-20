import serial
import numpy as np
import sounddevice as sd
from pynput import keyboard
import matplotlib.pyplot as plt
from queue import Queue
import threading

# --- CONFIGURAÇÕES ---
porta_config = '/dev/ttyACM0' 
amostragem = 44100
CHUNK = 1024  
limiteDistancia = 30
volumeMaximo = 0.8
COR_FUNDO_HEX = '#0b032c'

params = {
    'freq_alvo': 261.63,
    'freq_atual': 261.63,
    'vol_alvo': 0.0,
    'vol_atual': 0.0,        
    'fase': 0.0
}

ESCALA_MUSICAL = [
    (4,  261.63),  # Dó (C4)
    (8, 293.66),  # Ré (D4)
    (12, 329.63),  # Mi (E4)
    (16, 349.23),  # Fá (F4)  
    (20, 392.00),  # Sol (G4)
    (24, 440.00),  # Lá (A4)
    (28, 493.88),  # Si (B4)
    (float('inf'), 523.25) # Dó Agudo (C5)
]

# Osciloscópio 
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

fila_onda = Queue()

# --- SERIAL COM ARDUINO ---
try:
    porta = serial.Serial(porta_config, 9600, timeout=0.05)
except Exception as e:
    print(f"Erro: Verifique se o Arduino está na porta {porta_config}\nDetalhe: {e}")
    exit()

# ---AJUSTE DE COR ---
def obter_cor_da_frequencia(freq):
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
            
    r, g, b = escala_cores[-1][1]
    return f"#{r:02x}{g:02x}{b:02x}"

# --- MOTOR DE ÁUDIO ---
def audio_callback(outdata, frames, time_info, status):
    t = np.arange(frames) / amostragem
    
    params['vol_atual'] += 0.1 * (params['vol_alvo'] - params['vol_atual'])
    params['freq_atual'] += 0.08 * (params['freq_alvo'] - params['freq_atual'])
    
    f = params['freq_atual']
    v = params['vol_atual']
    
    arg = 2 * np.pi * f * t + params['fase']
    onda = v * np.sin(arg)
    outdata[:, 0] = onda
    
    params['fase'] = (arg[-1] + (2 * np.pi * f / amostragem)) % (2 * np.pi)
    
    fila_onda.put(onda.copy())

# --- LÓGICA DE PROCESSAMENTO DOS SENSORES ---
def processar(leitura_vol, leitura_freq):
    # Sensor 1 controla o volume por aproximação (proporção quadrática)
    if leitura_vol <= limiteDistancia:
        proporcao = (limiteDistancia - leitura_vol) / limiteDistancia
        params['vol_alvo'] = (proporcao ** 2) * volumeMaximo
        
        # Sensor 2 chaveia a frequência alvo baseado nos limiares da escala
        if leitura_freq <= limiteDistancia:
            for limiar, frequencia in ESCALA_MUSICAL:
                if leitura_freq < limiar:
                    params['freq_alvo'] = frequencia
                    break
    else:
        params['vol_alvo'] = 0.0

def ao_pressionar(key):
    if key == keyboard.Key.esc:
        return False

# --- MATPLOTLIB ---
plt.rcParams['toolbar'] = 'None' 
fig, ax = plt.subplots(figsize=(10, 4))
fig.canvas.manager.set_window_title('Osciloscópio Cyberpunk - Modo Theremin')

x = np.arange(0, CHUNK)
line, = ax.plot(x, np.zeros(CHUNK), '-', lw=3, color='#ff005a') 

ax.set_facecolor(COR_FUNDO_HEX)
fig.patch.set_facecolor(COR_FUNDO_HEX)
ax.set_ylim(-1.1, 1.1)
ax.set_xlim(0, CHUNK)
ax.axis('off') 

plt.show(block=False)

# --- INICIALIZAÇÃO DO SISTEMA ---
print(f"Sintetizador Theremin rodando... | ESC no teclado para sair.")

with sd.OutputStream(channels=1, callback=audio_callback, samplerate=amostragem, blocksize=CHUNK):
    with keyboard.Listener(on_press=ao_pressionar) as listener:
        try:
            while listener.running:
                #LEITURA DA SERIAL
                linha = porta.readline().decode('utf-8', errors='ignore').strip()
                if ',' in linha:
                    dados = linha.split(',')
                    if len(dados) == 2:
                        v1, v2 = dados[0], dados[1]
                        if v1.isdigit() and v2.isdigit():
                            # v1 e v2 passados corretamente para a função do Theremin
                            processar(int(v1), int(v2))
                
                #ATUALIZAÇÃO OSCILOSCÓPIO
                dados_da_onda = None
                while not fila_onda.empty():
                    dados_da_onda = fila_onda.get()
                
                if dados_da_onda is not None:
                    line.set_ydata(dados_da_onda)
                    
                    if params['vol_atual'] > 0.001:
                        cor_dinamica = obter_cor_da_frequencia(params['freq_atual'])
                        line.set_color(cor_dinamica)
                    
                    try:
                        fig.canvas.draw_idle() 
                        fig.canvas.flush_events() 
                    except:
                        break
                
                fig.canvas.start_event_loop(0.001)
                
        except Exception as e:
            print(f"\nErro no loop principal: {e}")
        finally:
            print("\nFechando conexões...")
            porta.close()