import serial
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from threading import Thread
import numpy as np

SERIAL_PORT = 'COM7' 
BAUD_RATE = 9600

class Radar:
    def __init__(self, root):
        self.root = root
        self.root.title("Radar")
        
        self.fig, self.ax = plt.subplots(subplot_kw={'projection': 'polar'})
        self.ax.set_ylim(0, 50)
        
        self.ax.set_xlim(0, np.pi)
        self.ax.set_xticks(np.linspace(0, np.pi, 7))
        self.ax.set_xticklabels(['0°', '30°', '60°', '90°', '120°', '150°', '180°'])
        
        self.ax.set_yticklabels([]) 
        self.ax.set_yticks([10, 20, 30, 40, 50])
        
        offset = 0.0 
        
        for r in [10, 20, 30, 40, 50]:
            self.ax.text(-offset, r, str(r), ha='center', va='top', color='black', fontsize=9)
            
        for r in [10, 20, 30, 40, 50]:
            self.ax.text(np.pi + offset, r, str(r), ha='center', va='top', color='black', fontsize=9)
            
        self.ax.text(-np.pi/2, 2, '0', ha='center', va='top', color='black', fontsize=9)
        
        self.line, = self.ax.plot([], [], 'ro', markersize=5)
        self.points_x = []
        self.points_y = []

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.running = True
        self.thread = Thread(target=self.read_serial, daemon=True)
        self.thread.start()

    def read_serial(self):
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
            while self.running:
                raw_data = ser.readline()
                if not raw_data:
                    continue
                
                line = raw_data.decode('utf-8', errors='ignore').strip()
                match = re.search(r"Distance:\s*(\d+)\s*cm\s*\|\s*Angle:\s*(\d+)", line)
                
                if match:
                    dist = int(match.group(1))
                    angle = int(match.group(2))

                    if angle <= 10 or angle >= 170:
                        self.points_x = []
                        self.points_y = []

                    if 0 <= dist <= 50:
                        rad = np.deg2rad(angle)
                        self.points_x.append(rad)
                        self.points_y.append(dist)
                        self.update_plot()
            
            ser.close()
        except Exception as e:
            print(f"Error: {e}")

    def update_plot(self):
        try:
            self.line.set_data(self.points_x, self.points_y)
            self.canvas.draw_idle()
        except:
            pass

    def on_close(self):
        self.running = False
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Radar(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()