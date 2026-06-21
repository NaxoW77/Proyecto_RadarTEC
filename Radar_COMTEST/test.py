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

# Datos manuales y automáticos

# Puntos cruzandose
coordenadas_manuales = [
    # Primer punto en 45cm 20°
    [45, 20, 0], # [Distancia, Angulo, Barrido]
    
    [20, 180, 0],
    
    # Segundo punto en 40cm 60°
    [40, 60, 1],
    
    [25, 100, 1],
    
    # Tercer punto en 35cm 100°
    [35, 100, 2],
    
    [30, 20, 2],
    
    # Cuarto punto en 30cm 140°
    [20, 120, 3],
    [30, 140, 3],
    [40, 160, 3],
    
    # Quinto punto en 25cm 180°
    [25, 180, 4]
]

barridos = [0,coordenadas_manuales[-1][-1]]
barrido_actual = 0

def loop():
    
    global barrido_actual
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
            print("Barrido:", barrido_actual)
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

                distancia = 100 # Distancia nula
                
                for posiciones in coordenadas_manuales:
                    if posiciones[2] == barrido_actual:
                        if posiciones[1] == step:
                            distancia = posiciones[0]
                            break
                
                cadena_datos = f"Distance: {distancia} cm | Angle: {step}\n"
                
                # Mensaje por el puerto
                try:
                    ser.write(cadena_datos.encode('utf-8'))

                    print(f"Enviando: {cadena_datos.strip()}")
                except serial.SerialTimeoutException:
                    print(f"Buffer lleno: {step}°")

                # Delay antes de avanzar al siguiente paso
                time.sleep(0.25) 
                step += 20
                

            # Señal de fin de barrido
            print("Enviando: Time: 1s")
            try:
                ser.write(b"Time: 1s\n")
            except serial.SerialTimeoutException:
                pass
            
            barrido_actual+=1
            if barrido_actual > barridos[-1]:
                    barrido_actual = barridos[0]
            
            # Delay del reinicio
            time.sleep(3) 

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