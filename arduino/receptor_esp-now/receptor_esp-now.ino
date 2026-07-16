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

  //Solo informacion de recepcion
  Serial.print("Mensaje recibido: ");
  Serial.println(datoRecibido.texto);

  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);

  //LOGICA DEL MARCADOR
  /*
  switch(datoRecibido.texto) 
  {
  case "1":
    Serial.println("POINT:1");
    break;

  case "2":
    Serial.println("POINT:2");
    break;

  case "3":
    Serial.println("UNDO");
    break;

  case "4":
    Serial.println("RESET");
    break;

  case "5":
    Serial.println("TEST");
    break;

  default:
    Serial.println("UNKNOWN");
    break;
  }
  */
   if (strcmp(datoRecibido.texto, "1") == 0) {
    Serial.println("POINT:1");
  } else if (strcmp(datoRecibido.texto, "2") == 0) {
    Serial.println("POINT:2");
  } else if (strcmp(datoRecibido.texto, "3") == 0) {
    Serial.println("UNDO");
  } else if (strcmp(datoRecibido.texto, "4") == 0) {
    Serial.println("RESET");
  } else if (strcmp(datoRecibido.texto, "5") == 0) {
    Serial.println("TEST");
  } else {
    Serial.println("UNKNOWN");
  } 
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
  Serial.println("RECEPTOR LISTO");
}

void loop() {
  // No necesita hacer nada aquí, todo pasa en onRecibir()
}