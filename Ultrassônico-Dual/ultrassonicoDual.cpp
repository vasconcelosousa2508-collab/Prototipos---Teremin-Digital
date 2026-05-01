const int pinoS1 = 7; // Sensor da Nota
const int pinoS2 = 6; // Sensor que substitui o Potenciômetro
const int pinoBuzzer = 9;

void setup() {
  pinMode(pinoBuzzer, OUTPUT);
  Serial.begin(9600);
}

// Função para ler o sensor de 3 pinos
long lerDistancia(int pino) {
  pinMode(pino, OUTPUT);
  digitalWrite(pino, LOW);
  delayMicroseconds(2);
  digitalWrite(pino, HIGH);
  delayMicroseconds(5);
  digitalWrite(pino, LOW);
  pinMode(pino, INPUT);
  return pulseIn(pino, HIGH) * 0.034 / 2;
}

void loop() {
  int leituraS1 = lerDistancia(pinoS1);
  int ajusteSensibilidade = lerDistancia(pinoS2); // O sensor 2 faz o papel do Pot

  // usando o valor do sensor 2 como o limite
  int frequencia = map(leituraS1, 2, ajusteSensibilidade, 261, 523);

  // só toca se a distância do S1 for menor que o ajuste do S2
  if (leituraS1 < ajusteSensibilidade && leituraS1 > 2) {
    tone(pinoBuzzer, frequencia);
  } else {
    noTone(pinoBuzzer);
  }

// MONITOR SERIAL
  Serial.print("S1 (Nota): "); Serial.print(leituraS1);
  Serial.print(" | S2 (Limite): "); Serial.println(ajusteSensibilidade);

  delay(50); 
}
