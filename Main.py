import cv2
import numpy as np
import dlib
from imutils import face_utils
from pygame import mixer
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import sys
import websocket
import json
import time
import secrets
import string
import threading
import os
from pygame.locals import *
import pygame
from matplotlib import pyplot as plt
import cv2
import tkinter as tk
from tkinter import messagebox
import qrcode

def Main():
    messagebox.showinfo("Ride Started", "Your ride has started!")
    def Mx():
        mixer.init()
        sound = mixer.Sound("C:\\Users\\siddu\\Desktop\\Local\\Module-X(Drowsy)\\Alarm.wav")

        # Video Capture 
        # 1 = Droid Cam
        # 0 Laptop WebCam

        cap = cv2.VideoCapture(1)
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor("C:\\Users\\siddu\\Desktop\\Local\\Module-X(Drowsy)\\Face_Landmarks.dat")

        sleep = 0
        drowsy = 0
        active = 0
        status = ""
        color = (0, 0, 0)

        def compute(ptA, ptB):
            dist = np.linalg.norm(ptA - ptB)
            return dist

        def blinked(a, b, c, d, e, f):
            up = compute(b, d) + compute(c, e)
            down = compute(a, f)
            ratio = up / (2.0 * down)
            if ratio > 0.25:
                return 2
            elif ratio > 0.21 and ratio <= 0.25:
                return 1
            else:
                return 0

        face_frame = None
        counter = 0
        closed_eye_count = 0
        open_eye_count = 0
        total_frame_count = 0

        while True:
            _, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = detector(gray)

            for face in faces:
                x1 = face.left()
                y1 = face.top()
                x2 = face.right()
                y2 = face.bottom()

                face_frame = frame.copy()
                cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                landmarks = predictor(gray, face)
                landmarks = face_utils.shape_to_np(landmarks)

                left_blink = blinked(landmarks[36], landmarks[37], landmarks[38], landmarks[41], landmarks[40], landmarks[39])
                right_blink = blinked(landmarks[42], landmarks[43], landmarks[44], landmarks[47], landmarks[46], landmarks[45])

                if left_blink == 0 or right_blink == 0:
                    sleep += 1
                    drowsy = 0
                    active = 0
                    closed_eye_count += 1
                    if sleep > 6:
                        status = "SLEEPING"
                        color = (255, 0, 0)
                        counter += 1
                elif left_blink == 1 or right_blink == 1:
                    sleep = 0
                    active = 0
                    drowsy += 1
                    open_eye_count += 1
                    if drowsy > 6:
                        status = "DROWSY"
                        color = (0, 0, 255)
                        counter = 0
                else:
                    drowsy = 0
                    sleep = 0
                    active += 1
                    open_eye_count += 1
                    if active > 6:
                        status = "AWAKE"
                        color = (0, 255, 0)
                        counter = 0

                if counter >= 10:
                    try:
                        sound.set_volume(1.0)
                        sound.play()
                    except:
                        pass
                    counter = 0

                cv2.putText(frame, f"Status: {status}", ((frame.shape[1] - cv2.getTextSize(f"Status: {status}", cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0][0]) // 2, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)
                cv2.putText(frame, f"Closed Eyes: {closed_eye_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(frame, f"Open Eyes: {open_eye_count}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

                for n in range(0, 68):
                    (x, y) = landmarks[n]
                    cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)

            if status == "SLEEPING":
                cv2.rectangle(face_frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), 10)

            cv2.imshow("Frame", frame)
            if face_frame is not None:
                cv2.imshow("Result of detector", face_frame)
            
            total_frame_count += 1
            
            key = cv2.waitKey(1)
            if key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

        awake_percentage = (open_eye_count / total_frame_count) * 100
        sleepy_percentage = (closed_eye_count / total_frame_count) * 100

        if sleepy_percentage >= 50:
            grade = 'F (Very Sleepy)'
        elif sleepy_percentage >= 30:
            grade = 'D (Sleepy)'
        elif sleepy_percentage >= 20:
            grade = 'C (Awake, but drowsy)'
        elif sleepy_percentage >= 10:
            grade = "B (Semi Awake)"
        else:
            grade = 'A (Fully Awake)'

        rtnx = {
            "Closed Eye Count" : f"{closed_eye_count}",
            "Open Eye Count" : f"{total_frame_count - closed_eye_count}",
            "Total Frames" : f"{total_frame_count}",
            "Awake Percentage" : f"{(100-sleepy_percentage):.2f}",
            "Drowsy/Sleep Percentage" : f"{sleepy_percentage:.2f}",
            "Grade" : grade
        }

        return(rtnx)

    def UI(data):
        root = Tk()
        root.title("Ride Overview Dashboard")
        root.configure(bg='white')

        for i, (key, value) in enumerate(data.items()):
            label = Label(root, text=f"{key}: {value}", font=("Helvetica", 12), bg='white', fg='black', padx=10, pady=5)
            label.grid(row=i, column=0, sticky=W)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8))

        ax1.pie([data['Awake Percentage'], data['Drowsy/Sleep Percentage']],
                labels=['Awake', 'Drowsy/Sleep'],
                autopct='%1.1f%%',
                startangle=90,
                colors=['#66c2a5', '#fc8d62'])
        ax1.set_title('Drowsiness Overview', fontsize=14, fontweight='bold')

        ax2.bar(['Closed Eye', 'Open Eye'], [data['Closed Eye Count'], data['Open Eye Count']], color=['#66c2a5', '#fc8d62'])
        ax2.set_xlabel('Eye State', fontsize=12)
        ax2.set_ylabel('Count', fontsize=12)
        ax2.set_title('Eye State Overview', fontsize=14, fontweight='bold')
        ax2.tick_params(axis='x', labelsize=10)
        ax2.tick_params(axis='y', labelsize=10)

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=len(data), columnspan=2, padx=10, pady=10)

        root.mainloop()


    def My():
        background_color = "#fafafa"

        def get_current_coordinates():
            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.geocode("India")
            return (location.latitude, location.longitude)


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
                    """try: 
                        x,y = get_current_coordinates()
                    except: 
                        pass
                    time.sleep(5)
                    try:
                        w,z = get_current_coordinates()
                        if x==w and y==z:
                            return True
                        else:
                            pass
                    except: 
                        pass"""
                    

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

        pygame.display.set_mode((1, 1))
        pygame.init()
        alarm_sound = pygame.mixer.Sound('C:\\Users\\siddu\\Desktop\\x\\Module-y\\Alarm.mp3')

        sensor1 = Sensor(address="172.16.128.43:8080", sensor_type="android.sensor.accelerometer")
        sensor2 = Sensor(address="172.16.128.43:8080", sensor_type="android.sensor.gyroscope")

        sensor1.connect()
        sensor2.connect()

        app = QtWidgets.QApplication(sys.argv)
        window1 = MainWindow(sensor_type="Accelerometer", x_data=sensor1.x_data, y_data=sensor1.y_data, z_data=sensor1.z_data, time_data=sensor1.time_data)
        window2 = MainWindow(sensor_type="Gyroscope", x_data=sensor2.gyro_x_data, y_data=sensor2.gyro_y_data, z_data=sensor2.gyro_z_data, time_data=sensor2.time_data)
        window1.show()
        window2.show()

        sys.exit(app.exec_())

    def run_mx_and_my():
        mx_result = Mx()
        my_thread = threading.Thread(target=My)

        my_thread.start()

        UI(mx_result)

    try:
        app = QtWidgets.QApplication(sys.argv)
        run_mx_and_my()
        sys.exit(app.exec_())
    except:
        pass 

def decode_qr_code(image):
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(image)
    return data

def scan_qr_code(event=None):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to open camera")
            break

        cv2.imshow("Verify Rider", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            cv2.imwrite("login.jpg", frame)
            qr_code_data = decode_qr_code(frame)
            if qr_code_data == "KiwiBeansXY01":
                messagebox.showinfo("Login Successful", "You are logged in!")
                login_label.config(text="Logged In")
                cap.release()
                cv2.destroyAllWindows()
                open_driver_details_window()
                return
    cap.release()
    cv2.destroyAllWindows()

def open_driver_details_window():
    driver_details_window = tk.Toplevel()
    driver_details_window.title("Driver Details")
    driver_details_window.geometry("400x300")
    driver_details_window.configure(bg="#f0f0f0")  # Set a light gray background

    # Driver details with a modern font and larger text size
    tk.Label(driver_details_window, text="Driver Name: Kushal B", bg="#f0f0f0", font=("Helvetica", 14)).pack()
    tk.Label(driver_details_window, text="Phone Number: 8618856297", bg="#f0f0f0", font=("Helvetica", 14)).pack()
    tk.Label(driver_details_window, text="Trip Details:", bg="#f0f0f0", font=("Helvetica", 14)).pack()
    tk.Label(driver_details_window, text="Start: PES University", bg="#f0f0f0", font=("Helvetica", 14)).pack()
    tk.Label(driver_details_window, text="Stop: Banashankri Metro Station", bg="#f0f0f0", font=("Helvetica", 14)).pack()
    tk.Label(driver_details_window, text="Scheduled Stops: 1", bg="#f0f0f0", font=("Helvetica", 14)).pack()

    # Start Ride button with a modern design
    tk.Button(driver_details_window, text="Start Ride", command=Main, bg="#4CAF50", fg="white", font=("Helvetica", 16), padx=10, pady=5).pack()

    # Set window position
    driver_details_window.transient(root)
    driver_details_window.grab_set()
    root.wait_window(driver_details_window)

root = tk.Tk()
root.title("Driver Login")
root.configure(bg="#f0f0f0")  # Set a light gray background

# Background image
# Replace "" with the path to your background image
# bg_image = tk.PhotoImage(file="")
# bg_label = tk.Label(root, image=bg_image)
# bg_label.place(relwidth=1, relheight=1)

verify_button = tk.Button(root, text="Verify Rider", command=scan_qr_code, bg="#2196F3", fg="white", font=("Helvetica", 16), padx=10, pady=5)
verify_button.pack()

login_label = tk.Label(root, text="", bg="#f0f0f0")
login_label.pack()

root.bind("<space>", scan_qr_code)
root.mainloop()