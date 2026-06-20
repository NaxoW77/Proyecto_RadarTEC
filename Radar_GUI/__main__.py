


#
#   Código de la interfaz para el radar
#
#   Se utiliza para mostrar una gráfica polar
#   y una cartesiana. Se muestran las posiciones
#   y predicciones según los movimientos
#



# Librerías para conectar con el arduino
import serial
import re

# Librerías para la gráfica
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Librerías para la interfaz
import tkinter as tk

# Librerías para el flujo del programa
from threading import Thread

# Librerías para cálculos
from math import sin, cos, sqrt, degrees, atan2
import numpy as np
import time

# Configuración de la comunicación serial
SERIAL_PORT = 'COM5' 
BAUD_RATE = 9600

# Clase principal
class Radar:
    def __init__(self, root):
        self.test = 1

        # Se crea la interfaz
        self.root = root
        self.root.title("Radar")
        
        # Se crea el gráfico polar
        self.figRad, self.axRad = plt.subplots(subplot_kw={'projection': 'polar'})
        self.axRad.set_title('Detección del radar', color='green')
        self.axRad.grid(color='green')
        self.axRad.set_facecolor('black')
        self.axRad.set_ylim(0, 50)
        self.axRad.set_xlim(0, np.pi)
        self.axRad.spines['polar'].set_color('green')
        
        self.canvasRad = FigureCanvasTkAgg(self.figRad, master=root)
        self.canvasRad.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.figRad.set_facecolor("black")
        
        # Etiquetas de cada 20 grados
        ticks_deg = np.arange(0, 181, 20)
        ticks = np.pi - np.deg2rad(ticks_deg)
        self.axRad.set_xticks(ticks)
        self.axRad.set_xticklabels([f"{d}°" for d in ticks_deg], color='green')
        
        # Etiquetas de cada 10 centímetros
        self.axRad.set_yticklabels([]) 
        self.axRad.set_yticks([10, 20, 30, 40, 50])
        
        # Simetría de las etiquetas
        offset = 0.0
        
        for r in [10, 20, 30, 40, 50]:
            self.axRad.text(-offset, r, str(r), ha='center', va='top', color='green', fontsize=9)
            
        for r in [10, 20, 30, 40, 50]:
            self.axRad.text(np.pi + offset, r, str(r), ha='center', va='top', color='green', fontsize=9)
            
        self.axRad.text(-np.pi/2, 2, '0', ha='center', va='top', color='green', fontsize=9)
        
        self.line, = self.axRad.plot([], [], 'ro', markersize=5)
        
        # Variables de tiempo
        self.time = 0
        self.time_start = time.time()
        self.points_time = []
        self.prevPoints_time = []
        
        # Estados de tiempo
        self.counting = False
        self.timeout = False
        
        # Puntos actuales
        self.points_x = []
        self.points_y = []

        # Puntos actuales, sin formato.
        self.points_angle = []
        self.points_dist = []
        
        # Puntos para las posiciones anteriores
        self.prevPoints_angle = []
        self.prevPoints_dist = []

        # Puntos de prediccion (Con formato polar)
        self.predictPoints_x = []
        self.predictPoints_y = []
        
        # Posiciones de los objetos (Original y trasladado)
        self.objects_pos0 = []
        self.objects_pos1 = []
        
        # Predicciones
        self.objects_predict = []
        
        # Texto para mostrar el tiempo
        self.time_text = self.figRad.text(0.02, 0.98, '', transform=self.figRad.transFigure, color='green', fontsize=12, fontweight='bold', verticalalignment='top', horizontalalignment='left')
        
        # Texto para mostrar errores
        self.error_text = self.figRad.text(0.02, 0.09, '', transform=self.figRad.transFigure, color='red', fontsize=12, fontweight='bold', verticalalignment='top', horizontalalignment='left')

        # Se crea el gráfico cartesiano
        self.figCart, self.axCart = plt.subplots()
        self.axCart.plot(color="green")
        self.axCart.grid(color="green")
        self.axCart.set_facecolor('black')
        self.axCart.set_xlabel('Posición (x)', color='green')
        self.axCart.set_ylabel('Posición (y)', color='green')
        self.axCart.tick_params('both', colors='green')
        self.axCart.set_title('Predicción Parabólica', color='green')
        self.axCart.spines['top'].set_color('green')
        self.axCart.spines['bottom'].set_color('green')
        self.axCart.spines['right'].set_color('green')
        self.axCart.spines['left'].set_color('green')

        #Variables para el gráfico cartesiano

        self.axCartPos1 = (0, 0)
        self.axCartPos2 = (0, 0)
        self.axCartX = np.arange(1, 50, 0.01)
        self.axCartY = (1*self.axCartX**2) + (1*self.axCartX) +1 #Forma cuadrática

        self.canvasCart = FigureCanvasTkAgg(self.figCart, master=root)
        self.canvasCart.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.figCart.set_facecolor("black")
        self.axCart.plot(self.axCartX, self.axCartY, color='green')
        self.axCart.set_ylim(0,20)
        self.axCart.scatter(self.axCartPos1, self.axCartPos2, color='red', zorder=5)

        # Hilo para la comunicación serial
        self.running = True
        self.thread = Thread(target=self.read_serial, daemon=True)
        self.thread.start()
        
        # Inicia el intervalo del contador
        self.update_time_display()


    def METODOPRUEBA(self):
        while self.running:

            

            time.sleep(1)

    # Función para la comunicación serial
    def read_serial(self):
        
        while self.running:
            try:
                
                # Puerto serial
                ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
                while self.running:
                    
                    # Revisar si se ha excedido el tiempo
                    if self.timeout:
                        self.reset_connection()
                        break
                    
                    # Leer el puerto serial
                    raw_data = ser.readline()
                    if not raw_data:
                        continue
                    
                    # Procesar los datos y buscar coincidencias
                    line = raw_data.decode('utf-8', errors='ignore').strip()
                    match = re.search(r"Distance:\s*(\d+)\s*cm\s*\|\s*Angle:\s*(\d+)", line)
                    match2 = re.search(r"Time:\s*(\d+)\s*s", line)
                    

                    # Coincidencia del tiempo
                    if match2:
                        self.time = int(match2.group(1))
                

                        if self.time == 0:
                            # Empezar a contar
                            self.counting = True
                            self.time_start = time.time()

                        
                            
                        elif self.time == 1:
                            # Detener el contador

                            print(self.objects_pos1)
                            print(self.objects_pos0)
                        
                            self.counting = False
                            self.points_x = []
                            self.points_y = []
                            
                            self.prevPoints_angle = self.points_angle
                            self.prevPoints_dist = self.points_dist
                            self.prevPoints_time = self.points_time
                            self.points_angle = []
                            self.points_dist = []
                            self.points_time = []

                            self.objects_pos0 = self.objects_pos1
                            self.objects_pos1 = []

                            self.update_plot()
                    
                    # Coincidencia de los datos
                    if match:
                        
                        # Revisar si se ha excedido el tiempo
                        if self.counting == False:
                            self.timeout = True
                        
                        # Guardar los datos
                        dist = int(match.group(1))
                        angle = int(match.group(2))
                        

                        # Límites de distancia
                        if 0 <= dist <= 50:
                            rad = np.pi - np.deg2rad(angle)
                            self.points_x.append(rad)
                            self.points_y.append(dist)

                            self.points_angle.append(angle)
                            self.points_dist.append(dist)
                            self.points_time.append(time.time() - self.time_start)

                            self.objects_pos1 = self.calcObject()

                            if len(self.objects_pos1) > 1:
                                # Llamar a la funciion parabola
                                objDist0 = self.objects_pos1[-2][1]
                                objAng0 = self.objects_pos1[-2][0]
                                objDist1 = self.objects_pos1[-1][1]
                                objAng1 = self.objects_pos1[-1][0]

                                objTime = self.objects_pos1[-2][2] - self.objects_pos1[-1][2]

                                self.parable((objDist0, objAng0), (objDist1, objAng1), objTime)

                            self.update_plot()
                            
                
                ser.close()
                
            # En caso de error
            except Exception as e:
                print(f"Error: {e}")
                self.error_text.set_text(f"Error: El puerto serial dejó de responder.")
                self.canvasRad.draw_idle()
                
                # Detener los hilos
                self.counting = False
                self.running = False

    # Intentos de reconexión
    def reset_connection(self):
        print("Error: Tiempo agotado")
        
        # Reinicialización de las variables
        self.timeout = False
        self.counting = False
        self.points_x = []
        self.points_y = []
        self.points_angle = []
        self.points_dist = []
        self.prevPoints_angle = []
        self.prevPoints_dist = []
        self.points_time = []
        self.prevPoints_time = []
        self.time_text.set_text("Error: Tiempo agotado")
        self.update_plot()

    # Actualizar los gráficos
    def update_plot(self):
        try:
            #Gráfico polar
            self.line.set_data(self.points_x, self.points_y)
            self.canvasRad.draw_idle()

            #Gráfico cartesiano

            #Borrar datos del grafico cartesiano antes de actualizarlo
            self.axCart.cla()
            #Reconfigurar el gráfico después de limpiarlo
            self.axCart.grid(color="green")
            self.axCart.set_facecolor('black')
            self.axCart.set_xlabel('Posición (x)', color='green')
            self.axCart.set_ylabel('Posición (y)', color='green')
            self.axCart.tick_params('both', colors='green')
            self.axCart.set_title('Predicción Parabólica', color='green')

            #Graficar la parábola y los puntos de detección
            self.axCart.plot(self.axCartX, self.axCartY, color='green')
            self.axCart.scatter(self.axCartPos1, self.axCartPos2, color='red', zorder=5)
            #Visualizar el gráfico con límites dinámicos según los puntos detectados
            self.axCart.set_ylim(0, max(self.axCartPos1[1], self.axCartPos2[1]) + 5)
            self.axCart.set_xlim(0, max(self.axCartPos1[0], self.axCartPos2[0]) + 5)
            
            self.canvasCart.draw_idle()

            # self.axCart.plot(self.axCartX, self.axCartY, color='green')
            # self.axCart.scatter(self.axCartPos1, self.axCartPos2, color='red', zorder=5)
            # self.canvasCart.draw_idle()
            
        except:
            pass
    
    # Actualizar el contador
    def update_time_display(self):
        if not self.running:
            return
        
        try:
            if self.counting:
                elapsed = time.time() - self.time_start
                self.time_text.set_text(f"t = {elapsed:.3f}s")
                self.canvasRad.draw_idle()
                
                # Revisar si se ha excedido el tiempo
                if elapsed > 3.150:
                    self.timeout = True
                
        except:
            pass
        
        # Llamada recursiva
        self.root.after(50, self.update_time_display)
    
    # Función para graficar una parábola
    def parable(self, pol1, pol2, time, const=9.8):

        """Grafica una parábola según dos coordenadas polares dadas,
        el tiempo de deteccion entre una y otra, y una constante
            - pol1: Coordenada polar #1. Tupla en forma (x, y). siendo 'x' la distancia y 'y' el ángulo
            - pol2: Coordenada polar #2. Mismas condiciones que pol1.
            - time: Tiempo de detección entre una coordenada y otra
            - const: Constante para la parábola, por defecto es la constante gravitatoria: 9.8"""

        #Transformar las coordenadas polares en cartesianas, y asignar cada valor 'x' y 'y'
        #por separado

        x1 = pol1[0]*cos(180-pol1[1])
        x2 = pol2[0]*cos(180-pol2[1])

        y1 = pol1[0]*sin(180-pol1[1])
        y2 = pol2[0]*sin(180-pol2[1])
        
        #Calcular coeficientes de la variable independiente

        a = - (const * (time**2)) / (2 * ((x2 - x1)**2))
        b = (y2 - y1 + 0.5 * const * (time**2)) / (x2 - x1) - 2*a*x1
        c = y1 - a * (x1**2) - b * x1

        #rangeX representa el intérvalo con el que se trabaja, el rango de x1 a x2.
        #Resto y sumo 1 para mejor visualización del gráfico
        x_min = min(x1, x2) - 1
        x_max = max(x1, x2) + 1

        rangeX = np.arange(x_min, x_max, 0.01)

        #Cambiar variables del gráfico
        self.axCartX = rangeX
        self.axCartY = (a*rangeX**2) + (b*rangeX) + c

        self.axCartPos1 = (x1, y1)
        self.axCartPos2 = (x2, y2)

    def calcObject(self):
        # Lista para almacenar los objetos detectados
        pointData = []

        # Enlistar los datos

        for i in range(len(self.points_angle)):
            angle = self.points_angle[i]
            dist = self.points_dist[i]
            tim = self.points_time[i]
            pointData.append([angle, dist, tim])

        #Agrupar los puntos por diferencia de angulo de 20 grados
        objects = []
        current_object = []
        for i in range(len(pointData)):
            if not current_object:
                current_object.append(pointData[i])
            else:
                if abs(pointData[i][0] - current_object[-1][0]) <= 20:
                    current_object.append(pointData[i])

                    if i == len(pointData) - 1:
                        objects.append(current_object)

                else:
                    objects.append(current_object)
                    current_object = [pointData[i]]

        #Calcular promedio para cada punto previamente agrupado

        promObject = []

        for object in objects:
            sum_ang = 0
            sum_dist = 0
            sum_tim = 0
            for i in range(len(object)):
                sum_ang += object[i][0]
                sum_dist += object[i][1]
                sum_tim += object[i][2]
            prom_ang = sum_ang/len(object)
            prom_dist = sum_dist/len(object)
            prom_tim = sum_tim/len(object)

            promObject.append([prom_ang, prom_dist, prom_tim])

        return promObject

        
        # print(promObject)
        # print(self.points_angle)
        # print(self.points_dist)
        # print(self.points_time)
    
    def prediction(self):
        """Prepara los puntos de dos barridos para predecir mediante MRU, los almacena en self.predictPoints"""

        if self.objects_pos0 == []:
            return
        
        for i in len(self.objects_pos0):
            if len(self.objects_pos1) < i:
                continue
            #Objetos en uso
            pos0 = self.objects_pos0[i]
            pos1 = self.objects_pos1[i]

            # Definición y corrección de cartesianas
            x1 = pos0[1]*cos(180-pos0[0])
            x2 = pos1[1]*cos(180-pos1[0])

            y1 = pos0[1]*sin(180-pos0[0])
            y2 = pos1[1]*sin(180-pos1[0])

            # Predicción de coordenada cartesiana
            # Busca un punto en la misma cantidad de tiempo entre pos0 y pos1, por lo que se cancelan los tiempos

            x3 = 2*x2 - x1
            y3 = 2*y2 - y1

            # Conversión de x3 y y3 a coordenadas polares

            dist = sqrt(x3**2 + y3**2)
            angle = degrees(atan2(y3, x3))

            # Mantener una distancia maxima de 50
            if dist > 50:
                dist = 50
            
            # Conversión al formato polar de la GUI

            rad = np.pi - np.deg2rad(angle)
            self.predictPoints_x.append(rad)
            self.predictPoints_y.append(dist)

        



        
        
        
    # Función para cerrar adecuadamente
    def on_close(self):
        self.running = False
        self.root.quit()
        self.root.destroy()

# Clase principal
if __name__ == "__main__":

    root = tk.Tk()
    app = Radar(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()