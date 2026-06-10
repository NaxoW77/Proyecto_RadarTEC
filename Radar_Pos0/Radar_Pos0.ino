//
//   Código simple para ubicar el servo
//
//   Se utiliza para colocar el servo en
//   una posición específica durante
//   el ensamblado de las piezas.
//

// Imports necesarios
#include <Servo.h>

// Definiciones de pines
const int servoPin = 7;

// Inicialización del servo
Servo myServo;

// Función setup
void setup() {
  Serial.begin(9600);
  myServo.attach(servoPin);
}

// Función loop
void loop() {

  // Ubicación del servo
  myServo.write(0);
}
