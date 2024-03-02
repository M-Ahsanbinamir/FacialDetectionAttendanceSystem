import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("ServiceAccountsKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://faceattendacerealtime-bac37-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "1234":
        {
            "name": "Elon Musk",
            "major": "Technology",
            "starting_year": 1995,
            "standing": "P",
            "year": 28,
            "last_attendance_time": "2024-01-11 00:54:34",
            "total_attendance": 17
        },
    "5678":
        {
            "name": "Warren Duffet",
            "major": "Economics",
            "starting_year": 1951,
            "standing": "F",
            "year": 72,
            "last_attendance_time": "2024-02-22 10:30:21",
            "total_attendance": 59
        },
    "9012":
        {
            "name": "Ahsan",
            "major": "Computer Science",
            "starting_year": 2021,
            "standing": "X",
            "year": 3,
            "last_attendance_time": "2024-02-18 08:30:59",
            "total_attendance": 2
        }
}

for key, value in data.items():
    ref.child(key).set(value)