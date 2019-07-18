import json

date_array = []
obj = dict()
input()

with open('DustData.json') as json_file:
  json_data = json.load(json_file)

for _ in range(2):
  date = int(input("Input Date Value : "))
  date_array.append(date)

for data_id in json_data['AccData']:
  gen_date = int(json_data['AccData'][data_id]['data_generated_date'][:8])

  if gen_date - date_array[0] >= 0 and date_array[1] - gen_date >= 0:
    try:
      obj['AccData'][data_id] = json_data['AccData'][data_id]
    except KeyError:
      obj['AccData'] = {data_id : json_data['AccData'][data_id]}

obj['data'] = json_data['data']

with open('DustDataDate.json', 'w') as new_file:
  try:
    json.dump(obj, new_file)
  except:
    print("Save Failed..")
  else:
    print("Save Successed.")