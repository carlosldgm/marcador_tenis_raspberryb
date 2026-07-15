#include <esp_now.h>
#include <WiFi.h>

// Definición de pines
const int PIN_BOTON = 2;
const int PIN_LED   = 13;

// Dirección MAC del ESP8266 Receptor (REEMPLAZA CON LA TUYA)
uint8_t direccionMacReceptor[] = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};

// Estructura simplificada para enviar datos
typedef struct struct_mensaje {
    bool estadoLed;
} struct_mensaje;

struct_mensaje miDatos;
esp_now_peer_info_t peerInfo;

// Variables de control del botón
int estadoBotonActual;
int ultimoEstadoBoton = LOW;
bool ledEncendido = false;

void setup() {
  Serial.begin(115200);

  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_BOTON, INPUT_PULLDOWN);/Users/carlosldgm/Desktop/ESP-NOW-0707/Receptor_ESPNOW_2Botones.ino

  // Modo Wi-Fi Estación (obligatorio para ESP-NOW)
  WiFi.mode(WIFI_STA);

  // Inicializar ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error inicializando ESP-NOW");
    return;
  }
  
  // Configurar los datos del receptor
  memcpy(peerInfo.peer_addr, direccionMacReceptor, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;
  
  // Registrar el receptor       
  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.println("Fallo al agregar el receptor");
    return;
  }
}

void loop() {
  estadoBotonActual = digitalRead(PIN_BOTON);

  // Detectar pulsación (Flanco de subida)
  if (estadoBotonActual == HIGH && ultimoEstadoBoton == LOW) {
    ledEncendido = !ledEncendido;
    
    // Indicador visual local
    digitalWrite(PIN_LED, ledEncendido);

    // Preparar el dato
    miDatos.estadoLed = ledEncendido;

    // Enviar por ESP-NOW
    esp_err_t resultado = esp_now_send(direccionMacReceptor, (uint8_t *) &miDatos, sizeof(miDatos));
     
    if (resultado == ESP_OK) {
      Serial.println("Enviado con éxito");
    } else {
      Serial.println("Error en el envío");
    }
    
    delay(50); // Anti-rebote
  }
  
  ultimoEstadoBoton = estadoBotonActual;
}
