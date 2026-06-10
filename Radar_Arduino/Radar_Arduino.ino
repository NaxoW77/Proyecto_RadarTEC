


//
//   Código para la función del Arduino
//
//   Se sube al Arduino para leer los datos
//   y moverse cada ciertos tiempos,
//   además de avisar inicio y  fin de barridos.
//



// Imports necesarios
#include <Servo.h>

// Definiciones de pines
const int trigPin = 2;
const int echoPin = A0;
const int servoPin = 7;
const int ledPin = 4;
const int buzzerPin = 11;

// Variable para los pasos
int step = 0;

// Variable para el servo
Servo myServo;
int servoPos = 0;

// Función setup para configurar el Arduino
void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(echoPin, INPUT);

  myServo.attach(servoPin);
}

// Función loop para el proceso
void loop() {

  // Señal de inicio del barrido
  Serial.println("Time: 0s");

  // Movimiento del servo
  while(step <= 180){
    myServo.write(step);
    delay(50);

    // Lectura de la distancia
    readDistance();

    // Función del LED
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

    // Espera al servo y continúa cada 20 grados
    delay(250);
    step+=20;
  }

  // Se reinicia el barrido
  step = 0;

  // Señal de fin del barrido
  Serial.println("Time: 1s");
  delay(50);

  // Se reinicia la posición del servo
  myServo.write(step);
  analogWrite(ledPin, 255);

  delay(250);
}

// Función para la lectura de la distancia
void readDistance() {

  // Envío del pulso
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Lectura de la distancia
  long duration = pulseIn(echoPin, HIGH);
  int distance = duration * 0.034 / 2;

  // Se muestra la distancia
  Serial.print("Distance: ");
  Serial.print(distance);

  // Señal auditiva
  if(distance < 50 && distance > 0){
    tone(buzzerPin, step*75);
    delay(5);
  }
  noTone(buzzerPin);

  // Se muestra el ángulo
  Serial.print(" cm | Angle: ");
  Serial.println(step);
}
