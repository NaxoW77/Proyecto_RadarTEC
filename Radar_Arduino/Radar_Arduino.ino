#include <Servo.h>

const int trigPin = 2;
const int echoPin = A0;
const int servoPin = 7;
const int ledPin = 4;
const int buzzerPin = 11;

unsigned long prevServoMillis = 0;
unsigned long prevSensorMillis = 0;
unsigned long prevLedOnMillis = 0;
unsigned long prevLedOffMillis = 0;

const int servoInterval = 3;
const int sensorInterval = 40;
const int ledOnInterval = 500;
const int ledOffInterval = 1000;

Servo myServo;
int servoPos = 0;
int servoDirection = 1;

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  myServo.attach(servoPin);
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - prevServoMillis >= servoInterval) {
    prevServoMillis = currentMillis;
    
    servoPos += servoDirection;
    myServo.write(servoPos);

    if (servoPos <= 0 || servoPos >= 180) {
      servoDirection *= -1;
    }
  }

  if (currentMillis - prevSensorMillis >= sensorInterval) {
    prevSensorMillis = currentMillis;
    readDistance();
  }

  if (currentMillis - prevLedOnMillis >= ledOnInterval) {
    prevLedOnMillis = currentMillis;
    analogWrite(ledPin, 255);
  }

  if (currentMillis - prevLedOffMillis >= ledOffInterval) {
    prevLedOffMillis = currentMillis;
    analogWrite(ledPin, 0);
  }

  if (currentMillis > 10000){
    currentMillis = 0;
  }
}

void readDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  int distance = duration * 0.034 / 2;

  Serial.print("Distance: ");
  Serial.print(distance);
  if(distance < 50 && distance > 0){
    tone(buzzerPin, servoPos*75);
    delay(5);
  }
  noTone(buzzerPin);
  Serial.print(" cm | Angle: ");
  Serial.println(servoPos);
}
