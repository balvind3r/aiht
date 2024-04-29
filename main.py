import cv2
import numpy as np
import urllib.request
import serial  # Import serial library for communication with ESP32

# Initialize serial communication with ESP32
ser = serial.Serial('COM6', 9600)  # Change port and baud rate as per your ESP32 configuration

url = 'http://192.168.29.24/cam-hi.jpg'
confThreshold = 0.5
nmsThreshold = 0.5
whT = 320

classesFile = 'coco.names'
classNames = []

with open(classesFile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

modelConfiguration = 'yolov3.cfg'
modelWeights = 'yolov3.weights'

net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

def find_person(output_list, img):
    hT, wT, cT = img.shape
    bbox = []
    classIds = []
    confs = []

    for output in output_list:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > confThreshold and classID == 0:  # Class ID 0 represents 'person' in COCO dataset
                w, h = int(detection[2] * wT), int(detection[3] * hT)
                x, y = int((detection[0] * wT) - w / 2), int((detection[1] * hT) - h / 2)
                bbox.append([x, y, w, h])
                classIds.append(classID)
                confs.append(float(confidence))

    indices = cv2.dnn.NMSBoxes(bbox, confs, confThreshold, nmsThreshold)

    if len(indices) > 0:  # If a person is detected
        i = indices[0]  # Take the first person detected
        box = bbox[i]
        x, y, w, h = box[0], box[1], box[2], box[3]
        # Calculate center of the person
        center_x = x + w // 2
        center_y = y + h // 2
        print("Person detected at:", center_x, center_y)
        # Map the center coordinates to the servo range (0-180)
        mapped_x = np.interp(center_x, [0, wT], [180, 0])
        mapped_y = np.interp(center_y, [0, hT], [180, 0])
        # Send mapped coordinates to ESP32
        ser.write(f"{int(mapped_x)},{int(mapped_y)}\n".encode())

while True:
    img_resp = urllib.request.urlopen(url)
    imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
    img = cv2.imdecode(imgnp, -1)

    blob = cv2.dnn.blobFromImage(img, 1 / 255, (whT, whT), [0, 0, 0], 1, crop=False)
    net.setInput(blob)

    layerNames = net.getLayerNames()
    net.getUnconnectedOutLayers()
    outputNames = [layerNames[i - 1] for i in net.getUnconnectedOutLayers()]
    outputs = net.forward(outputNames)
    output_list = list(outputs)

    find_person(output_list, img)

    cv2.imshow('Image', img)
    key = cv2.waitKey(1)
    if key == 27:
        break

cv2.destroyAllWindows()
