#include <IRremote.hpp>
#include <BluetoothSerial.h>

#define IR_RECEIVE_PIN 25  // GPIO 25 para o sensor IR
#define BUTTON_PIN 14      // GPIO14 para o botão
#define LED_PIN 26         // GPIO26 para o LED

BluetoothSerial SerialBT;
bool connected = false;     // Variável para controlar o estado da conexão
bool lastButtonState = HIGH; // Estado anterior do botão (HIGH por padrão com pull-up)

void setup() {
  Serial.begin(115200);     // Monitor Serial
  while (!Serial) {         // Aguarda a conexão serial
    ; // Faz nada até o Serial estar pronto
  }
  IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK); // Inicia o receptor IR
  SerialBT.begin("Board32 Control Bluetooth"); // Nome do dispositivo Bluetooth
  Serial.println("Bluetooth ativado!"); // Aviso de que o Bluetooth está ativado
  Serial.println("Sensor IR e Bluetooth prontos! Pareie via Bluetooth e pressione um botao no controle remoto...");
  delay(1000); // Atraso para garantir que a mensagem seja exibida

  // Configuração dos pinos do botão e LED
  pinMode(BUTTON_PIN, INPUT_PULLUP); // Botão com pull-up interno
  pinMode(LED_PIN, OUTPUT);          // LED como saída
  digitalWrite(LED_PIN, LOW);        // LED inicia desligado
}

void loop() {
  // Lê o estado atual do botão
  bool currentButtonState = digitalRead(BUTTON_PIN);
  
  // Controla o LED conforme o estado do botão (acende só enquanto pressionado)
  if (currentButtonState == LOW) {
    digitalWrite(LED_PIN, HIGH); // Liga o LED enquanto pressionado
  } else {
    digitalWrite(LED_PIN, LOW);  // Desliga o LED quando solto
  }

  // Só processa o IR se o botão NÃO estiver pressionado (LED apagado)
  if (currentButtonState == HIGH && IrReceiver.decode()) { 
    String hexCode = "0x" + String(IrReceiver.decodedIRData.command, HEX);
    Serial.println("Código Hexadecimal: " + hexCode); 
    SerialBT.println(hexCode); 
    delay(1000);  // Delay de 1 segundo na resposta do LED IR
    IrReceiver.resume(); 
  }
  
  // Verifica se há uma conexão Bluetooth estabelecida
  if (SerialBT.hasClient() && !connected) {
    Serial.println("Conexão Bluetooth estabelecida!"); 
    connected = true;
  } else if (!SerialBT.hasClient() && connected) {
    connected = false; 
  }
  
  delay(10); // Pequeno delay para melhorar a estabilidade
}