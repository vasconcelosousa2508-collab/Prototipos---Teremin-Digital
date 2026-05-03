const int pinoSIG = 7;     // Pino de sinal único
const int pinoPot = A1;    // Seu potenciômetro de ajuste
const int pinoBuzzer = 9;

void setup() {
  pinMode(pinoBuzzer, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // 1. Disparar o pulso (Pino como SAÍDA) ---
  pinMode(pinoSIG, OUTPUT);
  digitalWrite(pinoSIG, LOW);
  delayMicroseconds(2);
  digitalWrite(pinoSIG, HIGH);
  delayMicroseconds(5);
  digitalWrite(pinoSIG, LOW);

  // 2. Ouvir o eco (Pino como ENTRADA) ---
  pinMode(pinoSIG, INPUT);
  long duracao = pulseIn(pinoSIG, HIGH);

  // Matemática: Distância em cm
  int distancia = duracao * 0.034 / 2;

  // Ajuste de sensibilidade pelo potenciômetro
  int alcanceMax = map(analogRead(pinoPot), 0, 1023, 10, 100);

  // Lógica do Som
  if (distancia > 2 && distancia < alcanceMax) {
    // Mapeia: mais perto = mais agudo
    int frequencia = map(distancia, 2, alcanceMax, 1000, 261);
    tone(pinoBuzzer, frequencia);
  } else {
    noTone(pinoBuzzer);
  }

  Serial.print("Distancia: ");
  Serial.print(distancia);
  Serial.println(" cm");

  delay(50); 
}
