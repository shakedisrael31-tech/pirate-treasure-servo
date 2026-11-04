"""
look_detector.py
מזהה בעזרת MediaPipe אם מישהו מסתכל למצלמה, ושולח לארדואינו:
  '1' כשמתחילים להסתכל, '0' כשמפסיקים.

התקנה:
  pip install mediapipe==0.10.14 opencv-python pyserial

הרצה:
  python look_detector.py --port COM5        (Windows)
  python look_detector.py --port /dev/tty.usbmodem1101   (Mac)
  python look_detector.py --no-serial        (בדיקה בלי ארדואינו)
יציאה: מקש q
"""

import argparse
import time

import cv2
import mediapipe as mp

try:
    import serial
except ImportError:
    serial = None

# ---------- הגדרות שאפשר לכוונן ----------
HEAD_TOLERANCE = 0.15   # כמה הראש יכול להיות מסובב (0.5 = ישר בדיוק)
EYE_TOLERANCE = 0.15    # כמה האישון יכול לזוז מהמרכז
FRAMES_TO_ON = 5        # כמה פריימים רצופים של מבט כדי להפעיל
FRAMES_TO_OFF = 10      # כמה פריימים רצופים בלי מבט כדי לכבות
# -----------------------------------------


def ratio(value, a, b):
    """מיקום יחסי של value בין a ל-b (0 עד 1)."""
    if b == a:
        return 0.5
    return (value - a) / (b - a)


def is_looking(lm):
    """מקבל landmarks של Face Mesh ומחזיר True אם הפנים והעיניים מכוונות למצלמה."""
    # כיוון הראש שמאלה/ימינה: האף ביחס לצדי הפנים
    yaw = ratio(lm[1].x, lm[234].x, lm[454].x)
    # כיוון הראש למעלה/למטה: האף ביחס למצח ולסנטר
    pitch = ratio(lm[1].y, lm[10].y, lm[152].y)

    # מיקום האישונים בתוך העיניים
    eye1 = ratio(lm[468].x, lm[33].x, lm[133].x)
    eye2 = ratio(lm[473].x, lm[362].x, lm[263].x)

    head_ok = abs(yaw - 0.5) < HEAD_TOLERANCE and 0.35 < pitch < 0.75
    eyes_ok = abs(eye1 - 0.5) < EYE_TOLERANCE and abs(eye2 - 0.5) < EYE_TOLERANCE
    return head_ok and eyes_ok, (yaw, pitch, eye1, eye2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="COM5", help="פורט הארדואינו")
    parser.add_argument("--camera", type=int, default=0, help="מספר המצלמה")
    parser.add_argument("--no-serial", action="store_true", help="בלי ארדואינו")
    args = parser.parse_args()

    # חיבור לארדואינו
    ser = None
    if not args.no_serial:
        if serial is None:
            print("pyserial לא מותקן: pip install pyserial")
        else:
            try:
                ser = serial.Serial(args.port, 9600, timeout=1)
                time.sleep(2)  # זמן לארדואינו להתאפס
                print(f"מחובר לארדואינו ב-{args.port}")
            except Exception as e:
                print(f"לא הצלחתי להתחבר ל-{args.port}: {e}")
                print("ממשיך בלי ארדואינו.")

    cap = cv2.VideoCapture(args.camera)
    face_mesh = mp.solutions.face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,  # נדרש בשביל האישונים
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    looking_state = False
    on_count = 0
    off_count = 0

    def send(cmd):
        if ser:
            ser.write(cmd.encode())

    send("0")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("אין תמונה מהמצלמה")
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb)

        looking_now = False
        info = ""
        if result.multi_face_landmarks:
            lm = result.multi_face_landmarks[0].landmark
            looking_now, vals = is_looking(lm)
            info = "yaw %.2f  pitch %.2f  eyes %.2f / %.2f" % vals

        # סינון רעשים: צריך כמה פריימים רצופים כדי לשנות מצב
        if looking_now:
            on_count += 1
            off_count = 0
        else:
            off_count += 1
            on_count = 0

        if not looking_state and on_count >= FRAMES_TO_ON:
            looking_state = True
            send("1")
            print("מסתכלים! -> סרבו זז")
        elif looking_state and off_count >= FRAMES_TO_OFF:
            looking_state = False
            send("0")
            print("הפסיקו להסתכל -> סרבו חוזר")

        # תצוגה
        color = (0, 200, 0) if looking_state else (0, 0, 255)
        text = "LOOKING" if looking_state else "NOT LOOKING"
        cv2.putText(frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        cv2.putText(frame, info, (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.imshow("Look Detector  (q = exit)", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    send("0")
    cap.release()
    cv2.destroyAllWindows()
    if ser:
        ser.close()


if __name__ == "__main__":
    main()
