import serial
import time
import random

# Archivo de configuración
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from Config import config
config = config.Config

SERIAL_PORT = config.test_port_write
BAUD_RATE = config.serial_baudrate

def loop():
    try:
        # Abrimos el puerto simulado
        ser = serial.Serial(
            port=SERIAL_PORT, 
            baudrate=BAUD_RATE, 
            timeout=1, 
            rtscts=False, 
            dsrdtr=False, 
            write_timeout=0
        )

        while True:
            # Señal de inicio de barrido
            print("Enviando: Time: 0s")
            try:
                ser.write(b"Time: 0s\n")
                
            except serial.SerialTimeoutException:
                pass
            
            step = 0
            # Bucle de barrido de 0 a 180 grados (de 20 en 20)
            while step <= 180:
                time.sleep(0.05) # delay(50) del movimiento del servo

                distancia = random.randint(10, 45) # Distancia aleatoria
                cadena_datos = f"Distance: {distancia} cm | Angle: {step}\n"
                
                # Mensaje por el puerto
                try:
                    ser.write(cadena_datos.encode('utf-8'))

                    print(f"Enviando: {cadena_datos.strip()}")
                except serial.SerialTimeoutException:
                    print(f"Buffer lleno en paso {step}° (¿Está la GUI abierta?)")

                # Delay antes de avanzar al siguiente paso
                time.sleep(0.25) 
                step += 20

            # Señal de fin de barrido
            print("Enviando: Time: 1s")
            try:
                ser.write(b"Time: 1s\n")
            except serial.SerialTimeoutException:
                pass
            
            # Delay del reinicio del servo en el Arduino real
            time.sleep(0.30) 

    except serial.SerialException as e:
        print(f"\nError de comunicación: {e}")
    except KeyboardInterrupt:
        print("\nCerrando.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Puerto serial cerrado.")

if __name__ == "__main__":
    loop()