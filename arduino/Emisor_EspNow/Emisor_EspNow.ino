#include <esp_now.h>
#include <WiFi.h>

// ==================== CONFIGURACIÓN ====================

#define LED_PIN    12
#define TIEMPO_DOBLE_CLIC  400

struct Boton {
  uint8_t pin;
  const char* comandoClic;
  const char* comandoDoble;
  const char* etiqueta;
};

Boton botones[] = {
  { 4,  "1", "3", "Punto J1 / Undo" },
  { 18, "2", "4", "Punto J2 / Reset" },
};

const int NUM_BOTONES = sizeof(botones) / sizeof(botones[0]);

struct EstadoBoton {
  bool anterior;
  unsigned long ultimoClic;
  bool esperandoDoble;
};

EstadoBoton estados[NUM_BOTONES];

// ==================== ESP-NOW ====================

uint8_t macReceptor[] = {0xA0, 0xDD, 0x6C, 0x10, 0x5B, 0xE4};

typedef struct {
  char texto[32];
} Mensaje;

Mensaje datoEnviar;

void alEnviar(const esp_now_send_info_t *info, esp_now_send_status_t status) {
  // Callback vacío
}

// ==================== FUNCIONES AUXILIARES ====================

void enviarComando(const char* comando, const char* descripcion) {
  strncpy(datoEnviar.texto, comando, sizeof(datoEnviar.texto) - 1);
  datoEnviar.texto[sizeof(datoEnviar.texto) - 1] = '\0';
  
  esp_now_send(macReceptor, (uint8_t*)&datoEnviar, sizeof(datoEnviar));
  
  Serial.print("📤 ");
  Serial.print(descripcion);
  Serial.print(" → '");
  Serial.print(comando);
  Serial.println("'");
  
  digitalWrite(LED_PIN, HIGH);
}

// ==================== SETUP ====================

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  for (int i = 0; i < NUM_BOTONES; i++) {
    pinMode(botones[i].pin, INPUT_PULLUP);
    estados[i].anterior = HIGH;
    estados[i].ultimoClic = 0;
    estados[i].esperandoDoble = false;
  }

  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    Serial.println("❌ Error iniciando ESP-NOW");
    return;
  }

  esp_now_register_send_cb(alEnviar);

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, macReceptor, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("❌ Error agregando peer");
    return;
  }

  Serial.println("✅ Transmisor listo");
}

// ==================== LOOP ====================

void loop() {
  unsigned long ahora = millis();

  // ===== DETECTAR PRESIONES =====
  for (int i = 0; i < NUM_BOTONES; i++) {
    bool actual = digitalRead(botones[i].pin);

    if (estados[i].anterior == HIGH && actual == LOW) {
      
      if (estados[i].esperandoDoble && 
          (ahora - estados[i].ultimoClic) <= TIEMPO_DOBLE_CLIC &&
          botones[i].comandoDoble != nullptr) {
        
        // DOBLE CLIC
        Serial.print("[DOBLE] ");
        enviarComando(botones[i].comandoDoble, botones[i].etiqueta);
        estados[i].esperandoDoble = false;
        
      } else {
        // PRIMER CLIC
        estados[i].ultimoClic = ahora;
        estados[i].esperandoDoble = true;
      }
      
      delayMicroseconds(500);
    }

    estados[i].anterior = actual;
  }

  // ===== PROCESAR CLICS SIMPLES PENDIENTES =====
  for (int i = 0; i < NUM_BOTONES; i++) {
    if (estados[i].esperandoDoble && 
        (ahora - estados[i].ultimoClic) > TIEMPO_DOBLE_CLIC) {
      
      Serial.print("[SIMPLE] ");
      enviarComando(botones[i].comandoClic, botones[i].etiqueta);
      estados[i].esperandoDoble = false;
    }
  }

  // Apagar LED
  static unsigned long ledApagado = 0;
  if (digitalRead(LED_PIN) == HIGH && ahora > ledApagado) {
    ledApagado = ahora + 80;
    digitalWrite(LED_PIN, LOW);
  }
}