from datetime import datetime
import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("ServiceAccountsKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendacerealtime-bac37-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendacerealtime-bac37.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBg = cv2.imread("Resources/background.png")

# Importing the mode images into a list
folderModePath = 'Resources/modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# load the encoding file
print("Loading Encoded File")
file = open('EncodeFile.p', 'rb')
encodeKnownListwithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeKnownListwithIds
# print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1

imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrentFrame = face_recognition.face_locations(imgS)
    encodeCurrentFrame = face_recognition.face_encodings(imgS, faceCurrentFrame)

    imgBg[151:151+480, 517:517+640] = img
    imgBg[154:154+473, 120:120+371] = imgModeList[modeType]

    if faceCurrentFrame:
        for encodeFace, faceLoc in zip(encodeCurrentFrame, faceCurrentFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            print("Match Index", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 513 + x1, 157 + y1, x2 - x1, y2 - y1
                imgBg = cvzone.cornerRect(imgBg, bbox, rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBg, "Loading", (730,620))
                    cv2.imshow("Face Attendance", imgBg)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                # Get the data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                # Get the Image from the Storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # Update data of Attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secondElapse = (datetime.now() - datetimeObject).total_seconds()
                print(secondElapse)
                if secondElapse > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBg[154:154 + 473, 120:120 + 371] = imgModeList[modeType]

            if modeType != 3:
                if 10<counter<20:
                    modeType=2

                imgBg[154:154 + 473, 120:120 + 371] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBg, str(studentInfo['total_attendance']), (340, 229), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,0,0), 1)
                    cv2.putText(imgBg, str(studentInfo['major']), (275, 528), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 0.50, (0,0,0), 1)
                    cv2.putText(imgBg, str(id), (325, 483), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 0.75, (0,0,0), 1)
                    cv2.putText(imgBg, str(studentInfo['standing']), (222,580), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 0.50, (255,255,255), 1)
                    cv2.putText(imgBg, str(studentInfo['starting_year']), (310, 580), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 0.50, (255,255,255), 1)
                    cv2.putText(imgBg, str(studentInfo['year']), (420, 580), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 0.50, (255,255,255), 1)

                    imgBg[253:253+155,183:183+246] = imgStudent

                    (w, h) = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, 2)
                    offset = (371 - w[0]) // 2
                    cv2.putText(imgBg, str(studentInfo['name']), (120+offset, 445), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (255,255,255), 2)

                counter += 1

                if counter>=20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBg[154:154+473, 120:120+371] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0


    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBg)
    cv2.waitKey(1)

