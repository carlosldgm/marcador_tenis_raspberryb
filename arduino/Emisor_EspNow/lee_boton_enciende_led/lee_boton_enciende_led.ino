#define LED_PIN 12
#define BOTON_PIN 4 //OJO NO USAR EL PIN 2 PARA EL BOTON, ES USADO PARA FINES ESPECIALES POR EL ESP32 Y DA PROBLEMAS

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(BOTON_PIN, INPUT_PULLUP); // Usamos resistencia interna de pull-up
  Serial.begin(115200);
}

void loop() {
  int estadoBoton = digitalRead(BOTON_PIN);

  if (estadoBoton == LOW) {  // LOW porque con INPUT_PULLUP, presionado = 0
    digitalWrite(LED_PIN, HIGH); // Enciende el 
    Serial.println("led encendido");
  } else {
    digitalWrite(LED_PIN, LOW);  // Apaga el LED
    Serial.println("led apagado");
  }
}