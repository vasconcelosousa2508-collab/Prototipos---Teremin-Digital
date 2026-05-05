// Definições de pinos
const int pinoLDR_Nota = A0;   // Sensor que escolhe a nota
const int pinoLDR_Sens = A1;   // Sensor que substitui o potenciômetro
const int pinoBuzzer = 9;

void setup() {
  pinMode(pinoBuzzer, OUTPUT);
  Serial.begin(9600); 
}

void loop() {
  // Lê a luz do sensor de nota e a luz do sensor de sensibilidade
  int leituraLuz = analogRead(pinoLDR_Nota);
  int ajusteSensibilidade = analogRead(pinoLDR_Sens);

  // O valor lido no A1 agora define o limite máximo para o map do A0.
  int frequencia = map(leituraLuz, 0, ajusteSensibilidade, 261, 523);

  // Se a sombra no sensor de nota for maior que o limite do sensor de sensibilidade
  if (leituraLuz < ajusteSensibilidade) {
    tone(pinoBuzzer, frequencia);
  } else {
    noTone(pinoBuzzer);
  }

  // Monitor Serial 
  Serial.print("Nota (A0): "); Serial.print(leituraLuz);
  Serial.print(" | Sensibilidade (A1): "); Serial.println(ajusteSensibilidade);

  delay(10); 
}
