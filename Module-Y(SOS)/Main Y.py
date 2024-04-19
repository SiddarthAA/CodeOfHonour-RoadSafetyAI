from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import sys  
import websocket
import json
import threading
from twilio.rest import Client

background_color = "#fafafa"

class Sensor:
    def __init__(self, address, sensor_type):
        self.address = address
        self.sensor_type = sensor_type
        self.x_data = []
        self.y_data = []
        self.z_data = []
        self.time_data = []
        self.z_threshold = 18.0
        self.y_gyro_threshold = 14.0
        self.acc_z= False
        self.gyro_y = False

    def on_message(self, ws, message):
        values = json.loads(message)['values']
        timestamp = json.loads(message)['timestamp']

        self.x_data.append(values[0])
        self.y_data.append(values[1])
        self.z_data.append(values[2])
        self.time_data.append(float(timestamp/1000000))

        if len(self.z_data) >= 2:
            z_diff = abs(self.z_data[-1] - self.z_data[-2])
        if z_diff >= self.z_threshold:  
            self.acc_z = True
        else:
            self.acc_z = False
        
        if self.acc_z:
            if len(self.y_data) >= 2:
                y_diff = abs(self.y_data[-1] - self.y_data[-2])
                if y_diff >= self.y_gyro_threshold:
                    self.gyro_y_change = True
                    account_sid = 'ACda9cd0e8d4118ee035d9bf174c3fad8b'
                    auth_token = '2953016cee2a101c0057b13f277b4066'
                    client = Client(account_sid, auth_token)
                    message = client.messages.create(
                    from_='+12513125896',
                    body='HELP',
                    to='+918088232862'
                    )
                    print("sent")
                else:
                    self.gyro_y_change = False

    def on_error(self, ws, error):
        print("Error occurred")
        print(error)

    def on_close(self, ws):
        print("Connection closed")

    def on_open(self, ws):
        print(f"Connected to: {self.address}")

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


sensor1 = Sensor(address="172.16.128.17:8080", sensor_type="android.sensor.accelerometer")
sensor2 = Sensor(address="172.16.128.17:8080", sensor_type="android.sensor.gyroscope")


sensor1.connect()
sensor2.connect()


app = QtWidgets.QApplication(sys.argv)
window1 = MainWindow(sensor_type="Accelerometer", x_data=sensor1.x_data, y_data=sensor1.y_data, z_data=sensor1.z_data, time_data=sensor1.time_data)
window2 = MainWindow(sensor_type="Gyroscope", x_data=sensor2.x_data, y_data=sensor2.y_data, z_data=sensor2.z_data, time_data=sensor2.time_data)
window1.show()
window2.show()




sys.exit(app.exec_())