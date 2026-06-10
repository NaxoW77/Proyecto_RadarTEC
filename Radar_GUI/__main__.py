import serial
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from threading import Thread
import numpy as np
from math import sin, cos
import time

SERIAL_PORT = 'COM7' 
BAUD_RATE = 9600

class Radar:
    def __init__(self, root):

        #Crear gráfico circular del radar
        self.root = root
        self.root.title("Radar")
        
        self.figRad, self.axRad = plt.subplots(subplot_kw={'projection': 'polar'})
        self.axRad.set_title('Detección del radar', color='green')
        self.axRad.grid(color='green')
        self.axRad.set_facecolor('black')
        self.axRad.set_ylim(0, 50)
        
        self.axRad.set_xlim(0, np.pi)
        
        # Se cambiaron las etiquetas para que ahora vayan de 20 en 20 grados
        ticks_deg = np.arange(0, 181, 20)
        ticks = np.pi - np.deg2rad(ticks_deg)
        self.axRad.set_xticks(ticks)
        self.axRad.set_xticklabels([f"{d}°" for d in ticks_deg], color='green')
        
        self.axRad.set_yticklabels([]) 
        self.axRad.set_yticks([10, 20, 30, 40, 50])
        
        offset = 0.0
        
        for r in [10, 20, 30, 40, 50]:
            self.axRad.text(-offset, r, str(r), ha='center', va='top', color='green', fontsize=9)
            
        for r in [10, 20, 30, 40, 50]:
            self.axRad.text(np.pi + offset, r, str(r), ha='center', va='top', color='green', fontsize=9)
            
        self.axRad.text(-np.pi/2, 2, '0', ha='center', va='top', color='green', fontsize=9)
        
        self.line, = self.axRad.plot([], [], 'ro', markersize=5)
        
        # Tiempo por cada barrido
        self.time = 0
        self.time_counter = 0
        self.time_start = time.time()
        self.counting = False
        self.time_exceeded = False
        
        # Puntos actuales
        self.points_x = []
        self.points_y = []
        
        # Puntos para las posiciones anteriores
        self.prevPoints_x = []
        self.prevPoints_y = []
        
        # Posiciones de los objetos (Original y trasladado)
        self.objects_pos0 = []
        self.objects_pos1 = []
        
        # Predicciones
        self.objects_predict = []
        
        # Texto para mostrar el tiempo
        self.time_text = self.figRad.text(0.02, 0.98, '', transform=self.figRad.transFigure, color='green', fontsize=12, fontweight='bold', verticalalignment='top', horizontalalignment='left')

        self.canvasRad = FigureCanvasTkAgg(self.figRad, master=root)
        self.canvasRad.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.figRad.set_facecolor("black")

        #Crear gráfico del plano cartesiano

        self.figCart, self.axCart = plt.subplots()
        self.axCart.plot(color="green")
        self.axCart.grid(color="green")
        self.axCart.set_facecolor('black')
        self.axCart.set_xlabel('Tiempo (x)', color='green')
        self.axCart.set_ylabel('Profundidad (y)', color='green')
        self.axCart.tick_params('both', colors='green')
        self.axCart.set_title('Predicción Parabólica', color='green')
        self.axCart.spines['top'].set_color('green')
        self.axCart.spines['bottom'].set_color('green')
        self.axCart.spines['right'].set_color('green')
        self.axCart.spines['left'].set_color('green')


        self.canvasCart = FigureCanvasTkAgg(self.figCart, master=root)
        self.canvasCart.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.figCart.set_facecolor("black")

        self.running = True
        self.thread = Thread(target=self.read_serial, daemon=True)
        self.thread.start()
        
        # Inicia el intervalo del contador
        self.update_time_display()

    def read_serial(self):
        while self.running:
            try:
                ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
                while self.running:
                    
                    # Revisar si se ha excedido el tiempo
                    if self.time_exceeded:
                        self.reset_connection()
                        break
                    
                    raw_data = ser.readline()
                    if not raw_data:
                        continue
                    
                    line = raw_data.decode('utf-8', errors='ignore').strip()
                    match = re.search(r"Distance:\s*(\d+)\s*cm\s*\|\s*Angle:\s*(\d+)", line)
                    match2 = re.search(r"Time:\s*(\d+)\s*s", line)
                    
                    if match2:
                        self.time = int(match2.group(1))
                        
                        if self.time == 0:
                            # Empezar a contar
                            self.counting = True
                            self.time_start = time.time()
                        elif self.time == 1:
                            # Detener el contador
                            self.counting = False
                            self.points_x = []
                            self.points_y = []
                            self.update_plot()
                    
                    if match:
                        
                        if self.counting == False:
                            self.time_exceeded = True
                        
                        dist = int(match.group(1))
                        angle = int(match.group(2))

                        if 0 <= dist <= 50:
                            rad = np.pi - np.deg2rad(angle)
                            self.points_x.append(rad)
                            self.points_y.append(dist)
                            self.update_plot()
                
                ser.close()
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)

    def reset_connection(self):
        print("Error: Tiempo agotado")
        self.time_exceeded = False
        self.counting = False
        self.points_x = []
        self.points_y = []
        self.prevPoints_x = []
        self.prevPoints_y = []
        self.time_text.set_text("Error: Tiempo agotado")
        self.update_plot()

    def update_plot(self):
        try:
            self.line.set_data(self.points_x, self.points_y)
            self.canvasRad.draw_idle()
        except:
            pass
    
    def update_time_display(self):
        try:
            if self.counting:
                elapsed = time.time() - self.time_start
                self.time_text.set_text(f"t = {elapsed:.3f}s")
                self.canvasRad.draw_idle()
                
                # Revisar si se ha excedido el tiempo
                if elapsed > 3.150:
                    self.time_exceeded = True
                
        except:
            pass
        
        self.root.after(50, self.update_time_display)
    
    def parable(self, pol1, pol2, time, const=9.8):

        """Grafica una parábola según dos coordenadas polares dadas,
        el tiempo de deteccion entre una y otra, y una constante
            - pol1: Coordenada polar #1. Tupla en forma (x, y). siendo 'x' la distancia y 'y' el ángulo
            - pol2: Coordenada polar #2. Mismas condiciones que pol1.
            - time: Tiempo de detección entre una coordenada y otra
            - const: Constante para la parábola, por defecto es la constante gravitatoria: 9.8"""

        #Transformar las coordenadas polares en cartesianas, y asignar cada valor 'x' y 'y'
        #por separado

        x1 = pol1[0]*cos(pol1[1])
        x2 = pol2[0]*cos(pol2[1])

        y1 = pol1[0]*sin(pol1[1])
        y2 = pol2[0]*sin(pol2[1])
        
        #Calcular coeficientes de la variable independiente

        a = - (const * (time**2)) / (2 * ((x2 - x1)**2))
        b = (y2 - y1 + 0.5 * const * (time**2)) / (x2 - x1) - 2*a*x1
        c = y1 - a * (x1**2) - b * x1



        

    def on_close(self):
        self.running = False
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Radar(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()