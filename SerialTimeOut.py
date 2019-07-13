import signal
from contextlib import contextmanager
import serial
from firebase import firebase
from pymongo import MongoClient
import json, csv
import time

ser = serial.Serial(port='/dev/ttyS0',baudrate=9600)
url = 'https://gsm-dustdata-2f7b8.firebaseio.com'
client = MongoClient('localhost', 27017)

database = client.dustData
collection = database.accData

fbase = firebase.FirebaseApplication(url, None)

now = time.localtime()
key = "%04d%02d%02d%02d%02d%02d" % tuple(tm for tm in now[:6])

@contextmanager
def timeout(time):
    signal.signal(signal.SIGALRM, raise_timeout)
    signal.alarm(time)
    try:
        yield
    except TimeoutError:
        pass
    finally:
        signal.signal(signal.SIGALRM, signal.SIG_IGN)

def raise_timeout(selsignum, frame):
    raise TimeoutError

def getDateValue():
    return key

def dataRequest(request_code = ''):
    ser.write(request_code.encode('utf-16'))
    print("requesting data")
    with timeout(5):
        try:
            dataFrame = ser.readline().decode()
            if len(dataFrame) < 30:
                raise NotImplementedError
            else:
                dataFrame = dataFrame.split()
                for i in range(len(dataFrame)):
                    dataFrame[i] = str('0x') + dataFrame[i]
                    dataFrame[i] = int(dataFrame[i], 0)
                return dataFrame
            
        except Exception as e:
            print(e)
            print("Fail to request")
            return [int(-1)]

def dataDecode(data_list):
    if len(data_list) < 2:
        return {'ERR' : -1}
    else:
        temp = {'PM1': data_list[2],
            'PM2_5' : data_list[3],
            'PM10' : data_list[4],
            'V_SYSTEM' : data_list[6] / data_list[7],
            'V_SOLAR' : data_list[9] / data_list[10],
            'TEMPURATURE' : data_list[11],
            'HUMIDITY' : data_list[12],
            'ERR' : 0}
        return temp
    
def dataSynchronization(dataFrame):
    with timeout(5):
        try:
            fbase.put('/','data', dataDecode(dataFrame))
            print("Success")
        except Exception as e:
            print("ERR MESSAGE\n")
            print(e)
            print("ERROR: fail to update data")
        
def dataAccumulation(dateValue, dataFrame):
    with timeout(5):
        try:
            fbase.post('/AccData', {'system_data':dataDecode(dataFrame), 'data_generated_date': dateValue})
            #fbase.post('/', 'AccData', {dateValue:self.dataDecode(dataFrame)})
            #collection.insert({dateValue:dict(self.dataDecode(dataFrame))})
            print("Accumulation Success")
        except Exception as e:
            print(e)
            print("ERROR: fail to update acc data")
                

if __name__ == "__main__":
    SYS_DATA_FRAME = dataRequest('^')
    print(SYS_DATA_FRAME)
    print('updating data')
    dataSynchronization(SYS_DATA_FRAME)
    dataAccumulation(getDateValue(), SYS_DATA_FRAME)
    print('done..')
