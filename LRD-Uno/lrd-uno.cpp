// Definições de pinos
const int pinoLDR = A0;
const int pinoPot = A1;
const int pinoBuzzer = 9;

void setup() {
  pinMode(pinoBuzzer, OUTPUT);
  Serial.begin(9600); 
}

void loop() {
  int leituraLuz = analogRead(pinoLDR);
  int ajusteSensibilidade = analogRead(pinoPot);

  // Mapeia a leitura (ajustada pelo potenciômetro) 
  // para frequências musicais (Ex: 261Hz [Dó] a 523Hz [Dó oitava])
  // O valor 1023 é o máximo de luz, conforme a sombra, o valor cai.
  
  int frequencia = map(leituraLuz, 0, ajusteSensibilidade, 261, 523);

  // Filtro simples para não tocar som se houver muita luz
  if (leituraLuz < ajusteSensibilidade) {
    tone(pinoBuzzer, frequencia);
  } else {
    noTone(pinoBuzzer);
  }

  delay(10); // Estabilidade 
}
