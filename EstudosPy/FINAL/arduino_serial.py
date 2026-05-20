# Salve como: arduino_serial.py
import serial
import threading
from motor import params, ESCALA_MUSICAL, limiteDistancia, volumeMaximo

porta_config = '/dev/ttyACM0'

try:
    porta = serial.Serial(porta_config, 9600, timeout=0.05)
except Exception as e:
    print(f"Erro: Verifique se o Arduino está na porta {porta_config}\nDetalhe: {e}")
    porta = None

def processar_dados_sensores(leitura_vol, leitura_freq):
    # Sensor 1 - Volume
    if leitura_vol <= limiteDistancia:
        proporcao = (limiteDistancia - leitura_vol) / limiteDistancia
        params['vol_alvo'] = (proporcao ** 2) * volumeMaximo
        
        # Sensor 2 - Notas
        if leitura_freq <= limiteDistancia:
            for limiar, frequencia in ESCALA_MUSICAL:
                if leitura_freq < limiar:
                    params['freq_alvo'] = frequencia
                    break
    else:
        params['vol_alvo'] = 0.0
        params['freq_alvo'] = 261.63

def _loop_leitura(ouvinte_teclado):
    if not porta:
        return
    try:
        while ouvinte_teclado.running:
            linha = porta.readline().decode('utf-8', errors='ignore').strip()
            if ',' in linha:
                dados = linha.split(',')
                if len(dados) == 2:
                    v1, v2 = dados[0], dados[1]
                    if v1.isdigit() and v2.isdigit():
                        processar_dados_sensores(int(v1), int(v2))
    except Exception as e:
        print(f"\nErro no processamento da Serial: {e}")
    finally:
        porta.close()

def iniciar_conexao_arduino(ouvinte_teclado):
    """Dispara a leitura USB em background sem travar o programa principal"""
    thread = threading.Thread(target=_loop_leitura, args=(ouvinte_teclado,), daemon=True)
    thread.start()
    return thread