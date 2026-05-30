#include <Servo.h>

const int servoPin = 7;

Servo myServo;

void setup() {
  Serial.begin(9600);
  myServo.attach(servoPin);
}

void loop() {
  myServo.write(0);
}
