from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import sys
import websocket
import json
import time
import threading
import time
import pygame
import secrets
import string
from Alert import SOS
from geopy.geocoders import Nominatim

background_color = "#fafafa"

def get_current_coordinates():
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode("India")
    return (location.latitude, location.longitude)

latitude, longitude = get_current_coordinates()

class Sensor:
    def __init__(self, address, sensor_type):
        self.address = address
        self.sensor_type = sensor_type
        self.x_data = []
        self.y_data = []
        self.z_data = []
        self.time_data = []
        self.gyro_x_data = []
        self.gyro_y_data = []
        self.gyro_z_data = []
        self.z_threshold = 18.0
        self.y_gyro_threshold = 14.0
        self.acc_z = False
        self.gyro_y = False

    def on_message(self, ws, message):
        values = json.loads(message)['values']
        timestamp = json.loads(message)['timestamp']

        if self.sensor_type == "android.sensor.accelerometer":
            self.x_data.append(values[0])
            self.y_data.append(values[1])
            self.z_data.append(values[2])
        elif self.sensor_type == "android.sensor.gyroscope":
            self.gyro_x_data.append(values[0])
            self.gyro_y_data.append(values[1])
            self.gyro_z_data.append(values[2])

        self.time_data.append(float(timestamp / 1000000))

    def on_error(self, ws, error):
        print("\n")
        print("\033[1;31;40mConnection closed\033[m")

    def on_close(self, ws):
        print("\n")
        print("\033[1;31;40mConnection closed\033[m")


    def on_open(self, ws):
        print("\n")
        print(f"\033[1;32;40mConnected to {self.sensor_type}\033[m")

    def make_websocket_connection(self):
        ws = websocket.WebSocketApp(f"ws://{self.address}/sensor/connect?type={self.sensor_type}",
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        ws.run_forever()

    def connect(self):
        thread = threading.Thread(target=self.make_websocket_connection)
        thread.start()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, sensor_type, x_data, y_data, z_data, time_data):
        super(MainWindow, self).__init__()

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.graphWidget.setBackground(background_color)
        self.graphWidget.setTitle(f"{sensor_type} Data Plot", color="#8d6e63", size="20pt")

        styles = {"color": "#f00", "font-size": "15px"}
        self.graphWidget.setLabel("left", "m/s^2", **styles)
        self.graphWidget.setLabel("bottom", "Time (milliseconds)", **styles)
        self.graphWidget.addLegend()

        self.x_data_line = self.graphWidget.plot([], [], name="x", pen=pg.mkPen(color="#d32f2f"))  # Red
        self.y_data_line = self.graphWidget.plot([], [], name="y", pen=pg.mkPen(color="#7cb342"))  # Green
        self.z_data_line = self.graphWidget.plot([], [], name="z", pen=pg.mkPen(color="#0288d1"))  # Blue

        self.x_data = x_data
        self.y_data = y_data
        self.z_data = z_data
        self.time_data = time_data

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        limit = -1000

        self.x_data_line.setData(self.time_data[limit:], self.x_data[limit:])
        self.y_data_line.setData(self.time_data[limit:], self.y_data[limit:])
        self.z_data_line.setData(self.time_data[limit:], self.z_data[limit:])

        accel_change = False
        gyro_change = False

        if len(sensor1.x_data) > 1 and len(sensor1.y_data) > 1 and len(sensor1.z_data) > 1:
            x_diff = abs(sensor1.x_data[-1] - sensor1.x_data[-2])
            y_diff = abs(sensor1.y_data[-1] - sensor1.y_data[-2])
            z_diff = abs(sensor1.z_data[-1] - sensor1.z_data[-2])

            if x_diff > 10 or y_diff > 10 or z_diff > 10:
                accel_change = True

        if len(sensor2.gyro_x_data) > 1 and len(sensor2.gyro_y_data) > 1 and len(sensor2.gyro_z_data) > 1:
            gyro_x_diff = abs(sensor2.gyro_x_data[-1] - sensor2.gyro_x_data[-2])
            gyro_y_diff = abs(sensor2.gyro_y_data[-1] - sensor2.gyro_y_data[-2])
            gyro_z_diff = abs(sensor2.gyro_z_data[-1] - sensor2.gyro_z_data[-2])

            if gyro_x_diff > 10 or gyro_y_diff > 10 or gyro_z_diff > 10:
                gyro_change = True

        if accel_change and gyro_change:
            x,y = get_current_coordinates()
            time.sleep(5)
            w,z = get_current_coordinates()
            if x==w and y==z:
                return True
            else:
                pass
            print("\n")
            print("\033[1;33;40m-------------------------------------------\033[0m")
            print("\033[1;33;40m|           Co-Ordinates Verified          |\033[0m")
            print("\033[1;33;40m|              Potential Crash             |\033[0m")
            print("\033[1;33;40m-------------------------------------------\033[0m")
            handle_crash_detection()


def handle_crash_detection():
    try:
        alarm_sound.play()

        def countdown_animation(seconds):
            for i in range(seconds, 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write(f"{i} Seconds Remaining For Emergency Call |{'=' * i}{' ' * (seconds - i)}|")
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write("\n")

        countdown_animation(10)

        while pygame.mixer.get_busy():
            pygame.time.wait(100)

        id = SOS()
        x = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(4))
        tmpz = x.upper()
        print("\n")
        print("\033[1;31;40m-------------------------------------------\033[0m")
        print("\033[1;31;40m|          Initiating Emergency Call      |\033[0m")
        print("\033[1;31;40m-------------------------------------------\033[0m")        
        time.sleep(100)
    except KeyboardInterrupt:
        print("\n")
        print("\033[1;34;40mCancelled Emergency Call!\033[0m")
        pygame.mixer.music.stop()

if __name__ == "__main__":
    pygame.display.set_mode((1, 1))
    pygame.init()
    alarm_sound = pygame.mixer.Sound('C:\\Users\\siddu\\Desktop\\x\\Module-y\\Alarm.mp3')

    sensor1 = Sensor(address="172.16.128.69:8080", sensor_type="android.sensor.accelerometer")
    sensor2 = Sensor(address="172.16.128.69:8080", sensor_type="android.sensor.gyroscope")

    sensor1.connect()
    sensor2.connect()

    app = QtWidgets.QApplication(sys.argv)
    window1 = MainWindow(sensor_type="Accelerometer", x_data=sensor1.x_data, y_data=sensor1.y_data, z_data=sensor1.z_data, time_data=sensor1.time_data)
    window2 = MainWindow(sensor_type="Gyroscope", x_data=sensor2.gyro_x_data, y_data=sensor2.gyro_y_data, z_data=sensor2.gyro_z_data, time_data=sensor2.time_data)
    window1.show()
    window2.show()

    sys.exit(app.exec_())