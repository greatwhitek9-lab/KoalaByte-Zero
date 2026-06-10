#include <Arduino.h>

static const uint32_t BAUD_RATE = 921600;

void setup() {
  Serial.begin(BAUD_RATE);
  delay(250);
  Serial.println("KOALABYTE_EYE_CONTROLLER_READY");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "PING") {
      Serial.println("PONG");
    } else if (command == "STATUS") {
      Serial.println("OK:REV_0_5_EYES");
    } else {
      Serial.print("UNKNOWN:");
      Serial.println(command);
    }
  }
  delay(10);
}
