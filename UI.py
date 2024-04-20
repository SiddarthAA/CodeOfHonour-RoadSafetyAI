import cv2
import tkinter as tk
from tkinter import messagebox
import qrcode

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

def start_ride():
    # Add your logic for starting the ride here
    messagebox.showinfo("Ride Started", "Your ride has started!")

def open_driver_details_window():
    driver_details_window = tk.Toplevel()
    driver_details_window.title("Driver Details")
    driver_details_window.geometry("400x300")
    driver_details_window.configure(bg="white")

    # Driver details
    tk.Label(driver_details_window, text="Driver Name: John Doe", bg="white").pack()
    tk.Label(driver_details_window, text="Phone Number: 1234567890", bg="white").pack()
    tk.Label(driver_details_window, text="Trip Details:", bg="white").pack()
    tk.Label(driver_details_window, text="Start: Location A", bg="white").pack()
    tk.Label(driver_details_window, text="Stop: Location B", bg="white").pack()
    tk.Label(driver_details_window, text="Scheduled Stops: 2", bg="white").pack()

    # Start Ride button
    tk.Button(driver_details_window, text="Start Ride", command=start_ride).pack()

    # Set window position
    driver_details_window.transient(root)
    driver_details_window.grab_set()
    root.wait_window(driver_details_window)

root = tk.Tk()
root.title("Driver Login")
root.configure(bg="white")

# Background image
bg_image = tk.PhotoImage(file="background.gif")
bg_label = tk.Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)

verify_button = tk.Button(root, text="Verify Rider", command=scan_qr_code)
verify_button.pack()

login_label = tk.Label(root, text="")
login_label.pack()

root.bind("<space>", scan_qr_code)
root.mainloop()