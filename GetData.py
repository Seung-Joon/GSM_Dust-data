from firebase import firebase
import json

url = "https://gsm-dustdata-2f7b8.firebaseio.com"
fbase = firebase.FirebaseApplication(url, None)
datas = fbase.get("/AccData", None)

with open('DustData.json', 'w') as json_file:
  json.dump(datas, json_file)
