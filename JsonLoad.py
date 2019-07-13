import json

with open('gsm-dustdata-2f7b8-export.json') as json_file:  
  obj = dict()
  datas = json.load(json_file)
  for data_id in datas['AccData']:
    if not datas['AccData'][data_id]['system_data']['ERR']:
      try:
        obj['AccData'][data_id] = datas['AccData'][data_id]
      except KeyError:
        obj['AccData'] = {data_id : datas['AccData'][data_id]}
  obj['data'] = datas['data']
  
with open('NonErrorData.json', 'w') as new_file:
  json.dump(obj, new_file)
  print("JSON Dumped.")

