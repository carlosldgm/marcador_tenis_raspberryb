#include <esp_now.h>
#include <WiFi.h>

#define LED_PIN 12

typedef struct Mensaje {
  char texto[32];
} Mensaje;

Mensaje datoRecibido;

// Esta función se ejecuta automáticamente al recibir un mensaje
void onRecibir(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  memcpy(&datoRecibido, data, sizeof(datoRecibido));

  Serial.print("Mensaje recibido: ");
  Serial.println(datoRecibido.texto);

  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error iniciando ESP-NOW");
    return;
  }

  esp_now_register_recv_cb(onRecibir);
}

void loop() {
  // No necesita hacer nada aquí, todo pasa en onRecibir()
}