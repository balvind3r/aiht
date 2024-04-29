import cv2
from cvzone.FaceDetectionModule import FaceDetector
import serial
import urllib.request
import numpy as np

url = 'http://192.168.216.90/cam-hi.jpg'
ws, hs = 1280, 720
# cap.set(3, ws)
# cap.set(4, hs)

# if not cap.isOpened():
#     print("Camera couldn't Access!!!")
#     exit()

port = "/dev/cu.usbserial-0001"
ser = serial.Serial(port, 9600)  # Change the port to match your Arduino's port

detector = FaceDetector()
servoPos = [90, 90]  # initial servo position

while True:
    img_resp = urllib.request.urlopen(url)
    imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
    img = cv2.imdecode(imgnp, -1)
    img, bboxs = detector.findFaces(img, draw=False)

    if bboxs:
        # get the coordinate
        fx, fy = bboxs[0]["center"][0], bboxs[0]["center"][1]
        pos = [fx, fy]
        # convert coordinate to servo degree
        servoX = np.interp(fx, [0, ws], [180, 0])
        servoY = np.interp(fy, [0, hs], [180, 0])
        if servoX < 0:
            servoX = 0
        elif servoX > 180:
            servoX = 180
        if servoY < 0:
            servoY = 0
        elif servoY > 180:
            servoY = 180

        servoPos[0] = servoX
        servoPos[1] = servoY

        cv2.circle(img, (int(fx), int(fy)), 80, (0, 0, 255), 2)
        cv2.putText(img, str(pos), (int(fx) + 15, int(fy) - 15), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        cv2.line(img, (0, int(fy)), (ws, int(fy)), (0, 0, 0), 2)  # x line
        cv2.line(img, (int(fx), hs), (int(fx), 0), (0, 0, 0), 2)  # y line
        cv2.circle(img, (int(fx), int(fy)), 15, (0, 0, 255), cv2.FILLED)
        cv2.putText(img, "TARGET LOCKED", (850, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    else:
        cv2.putText(img, "NO TARGET", (880, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
        cv2.circle(img, (640, 360), 80, (0, 0, 255), 2)
        cv2.circle(img, (640, 360), 15, (0, 0, 255), cv2.FILLED)
        cv2.line(img, (0, 360), (ws, 360), (0, 0, 0), 2)  # x line
        cv2.line(img, (640, hs), (640, 0), (0, 0, 0), 2)  # y line

    cv2.putText(img, f'Servo X: {int(servoPos[0])} deg', (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    cv2.putText(img, f'Servo Y: {int(servoPos[1])} deg', (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    # Send servo positions to Arduino
    ser.write(f"{int(servoPos[0])},{int(servoPos[1])}\n".encode())

    cv2.imshow("Image", img)
    cv2.waitKey(1)
