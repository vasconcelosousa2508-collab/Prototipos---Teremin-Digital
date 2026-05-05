// Definições de pinos
const int pinoLDR = A0;

// Ajuste aqui a sensibilidade fixa (valor de 0 a 1023)
// Quanto menor o número, mais escuro precisa estar para disparar
const int limiteSombra = 400; 

void setup() {
  Serial.begin(9600); // Inicia a comunicação
}

void loop() {
  int leituraLuz = analogRead(pinoLDR);

  // Enviamos o valor bruto para o Python (para você ver no terminal dele)
  Serial.println(leituraLuz);

  // Dica: No Python, você vai checar:
  // Se leituraLuz < limiteSombra -> Toca som
  // Se leituraLuz >= limiteSombra -> Silêncio

  delay(50); // Estabilidade para não inundar o Python de dados
}