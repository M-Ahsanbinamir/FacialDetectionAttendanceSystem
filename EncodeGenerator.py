import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate("ServiceAccountsKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendacerealtime-bac37-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendacerealtime-bac37.appspot.com"
})

# Importing the Students images
folderPath = 'Images'
pathList = os.listdir(folderPath)
imgList = []
studentIds = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])

    fileName = os.path.basename(path)  # Get only the file name without the folder path
    bucket = storage.bucket()
    blob = bucket.blob(f'Images/{fileName}')  # Upload the file directly into the 'Images' folder
    blob.upload_from_filename(os.path.join(folderPath, path))  # Upload the file from the folder path
    print(f"Uploaded {fileName} to Firebase Storage in the 'Images' folder")

# Encoding the images
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding Started")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

# Save the encoding data to a file
file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")