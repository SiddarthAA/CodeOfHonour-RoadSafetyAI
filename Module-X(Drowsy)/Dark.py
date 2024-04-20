import cv2
import numpy as np
import dlib
from imutils import face_utils
from pygame import mixer

def Modx(video_path):
    mixer.init()
    sound = mixer.Sound("C:\\Users\\siddu\\Desktop\\Local\\Module-X(Drowsy)\\Alarm.wav")

    cap = cv2.VideoCapture(video_path)
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
        ret, frame = cap.read()
        frame = cv2.add(frame, np.array([75]))
        if not ret:
            break
        
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
                    # Increase the volume of the sound
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
            # Add a red frame around the face_frame to indicate sleeping
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
        "Closed Eye Count " : f"{closed_eye_count}",
        "Open Eye Count" : f"{total_frame_count - closed_eye_count}",
        "Total Frames" : f"{total_frame_count}",
        "Awake Percentage" : f"{(100-sleepy_percentage):.2f}%",
        "Drowsy/Sleep Percentage" : f"{sleepy_percentage:.2f}%",
        "Grade" : grade
    }

    return(rtnx)

video_path = "C:\\Users\\siddu\\Desktop\\Local\\Module-X(Drowsy)\\Video1.mp4"
Modx(video_path)
