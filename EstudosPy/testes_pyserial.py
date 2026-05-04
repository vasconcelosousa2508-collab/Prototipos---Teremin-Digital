import serial

import numpy as np
import sounddevice as sd
from pynput import keyboard

porta = serial.Serial('/dev/ttyACM0', 9600)

while(1):
    dados = porta.readline()
    print(dados.decode('utf-8'))