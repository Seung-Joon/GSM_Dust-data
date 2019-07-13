from firebase import firebase
import json

url = "https://gsm-dustdata-2f7b8.firebaseio.com"
fbase = firebase.FirebaseApplication(url, None)
datas = fbase.get("/AccData", None)

for data in datas:
  print(datas[data])

  
