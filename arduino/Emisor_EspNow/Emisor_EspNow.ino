#include <esp_now.h>
#include <WiFi.h>

#define LED_PIN 12
#define BOTON_J1 4

// Reemplaza con la MAC de tu ESP32 receptor
uint8_t macReceptor[] = {0xA0, 0xDD, 0x6C, 0x10, 0x5B, 0xE4};//A0:DD:6C:10:5B:E4

typedef struct Mensaje {
  char texto[32];
} Mensaje;

Mensaje datoEnviar;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BOTON_J1, INPUT_PULLUP);

  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error iniciando ESP-NOW");
    return;
  }

  // Registrar al receptor como "peer"
  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, macReceptor, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  esp_now_add_peer(&peerInfo);
}

void loop() {
  /*
  Las acciones que tendran los distintos botones seran
  1 = Punto jugador 1
  2 = Punto jugador 2
  3 = Undo
  4 = Reset
  5 = Test Display
  */
  int estadoBoton_J1 = digitalRead(BOTON_J1);

  if (estadoBoton_J1 == LOW) {
    digitalWrite(LED_PIN, HIGH); // Enciende LED local 

    strcpy(datoEnviar.texto, "1");
    Serial.println("Boton Presionado punto J1");
    esp_now_send(macReceptor, (uint8_t *) &datoEnviar, sizeof(datoEnviar));

    delay(300); // Evita enviar el mensaje demasiadas veces seguidas
  } else {
    digitalWrite(LED_PIN, LOW);
  }
}