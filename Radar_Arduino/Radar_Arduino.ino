#include <Servo.h>

const int trigPin = 2;
const int echoPin = A0;
const int servoPin = 7;
const int ledPin = 4;
const int buzzerPin = 11;

int step = 0;

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
  Serial.println("Time: 0s");
  while(step <= 180){
    myServo.write(step);
    delay(50);
    readDistance();

    if(step < 45){
      analogWrite(ledPin, 255);
    }
    else if(step < 90){
      analogWrite(ledPin, 0);
    }
    else if(step < 135){
      analogWrite(ledPin, 255);
    }
    else if(step < 180){
      analogWrite(ledPin, 0);
    }

    delay(250);
    step+=20;

  }
  step = 0;
  Serial.println("Time: 1s");
  delay(50);
  myServo.write(step);
  analogWrite(ledPin, 255);
  delay(250);
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
    tone(buzzerPin, step*75);
    delay(5);
  }
  noTone(buzzerPin);
  Serial.print(" cm | Angle: ");
  Serial.println(step);
}
