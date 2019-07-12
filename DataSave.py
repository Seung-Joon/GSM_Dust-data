from firebase import firebase

url = "https://gsm-dustdata-2f7b8.firebaseio.com"
fbase = firebase.FirebaseApplication(url, None)

values = fbase.get("/AccData", None)

for id in values:
  result = fbase.get("/AccData/" + str(id), None)
  if result['system_data']['ERR'] == 0:
    print(result)
  
