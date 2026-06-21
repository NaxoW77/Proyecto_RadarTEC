import serial
import time
import random

PUERTO_SIMULADOR = 'COM11'  
BAUD_RATE = 9600

def loop():
    try:
        # Abrimos el puerto serial emulado
        ser = serial.Serial(PUERTO_SIMULADOR, BAUD_RATE, timeout=1)

        while True:
            # Señal de inicio de barrido
            print("Enviando: Time: 0s")
            ser.write(b"Time: 0s\n")
            ser.flush()
            
            step = 0
            # Bucle de barrido de 0 a 180 grados (de 20 en 20)
            while step <= 180:
                time.sleep(0.05) # delay(50) del movimiento del servo

                distancia = random.randint(10, 45) # Distancia aleatoria
                
                # Print de la distancia y el grados
                cadena_datos = f"Distance: {distancia} cm | Angle: {step}\n"
                
                # Mensaje por el puerto
                ser.write(cadena_datos.encode('utf-8'))
                ser.flush()
                print(f"Transmitido -> {cadena_datos.strip()}")

                # delay(250) antes de avanzar al siguiente paso
                time.sleep(0.25) 
                step += 20

            # Señal de fin de barrido
            print("Enviando: Time: 1s")
            ser.write(b"Time: 1s\n")
            ser.flush()
            
            # delay del reinicio del servo en el Arduino real
            time.sleep(0.30) 

    except serial.SerialException as e:
        print(f"\nError: {e}")
    except KeyboardInterrupt:
        print("")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Puerto serial cerrado.")

if __name__ == "__main__":
    loop()