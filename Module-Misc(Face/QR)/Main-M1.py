import cv2
import tkinter as tk
from tkinter import messagebox
import qrcode

def generate_qr_code(text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qr_code.png")


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

        cv2.imshow("Scan QR Code", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            cv2.imwrite("login.jpg", frame)
            qr_code_data = decode_qr_code(frame)
            if qr_code_data == "KiwiBeansXY01":
                messagebox.showinfo("Login Successful", "You are logged in!")
                #login_label.config(text="Logged In")
                cap.release()
                cv2.destroyAllWindows()
                return
    cap.release()
    cv2.destroyAllWindows()