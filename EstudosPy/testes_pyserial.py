import serial

porta = serial.Serial('/dev/ttyACM0', 9600)

while(1):
    dados = porta.readline()
    print(dados.decode('utf-8'))