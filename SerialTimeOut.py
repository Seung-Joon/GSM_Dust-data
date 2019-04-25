import signal
from contextlib import contextmanager
import serial
import datetime as d
from firebase import firebase
import time

ser = serial.Serial(port='/dev/ttyS0',baudrate=9600)

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

def raise_timeout(signum, frame):
    raise TimeoutError

def getDateValue():
    now = time.localtime()
    key = "%04d%02d%02d%02d%02d%02d" %(now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    return key

def dataRequest(request_code = ''):
    ser.write(request_code.encode('utf-16'))
    print("requesting data")
    with timeout(5):
        try:
            dataFrame = ser.readline().decode()
            if(len(dataFrame) < 30):
                raise NotImplementError
            else:
                dataFrame = dataFrame.split()
                for i in range(len(dataFrame)):
                    dataFrame[i] = str('0x') + dataFrame[i]
                    dataFrame[i] = int(dataFrame[i], 0)
                return dataFrame 
        except:
            print("Fail to request")
            err_li = [int(-1)]
            return err_li

def dataDecode(data_list):
    if len(data_list) > 1:
        DATA_FRAME = {'PM1.0': data_list[2], 'PM2.5' : data_list[3],
                      'PM10' : data_list[4], 'V_SYSTEM' : data_list[6] / data_list[7],
                      'V_SOLAR' : data_list[9] / data_list[10], 'TEMPURATURE' : data_list[11],
                      'HUMIDITY' : data_list[12], 'ERR' : 0}
    else:
        DATA_FRAME = {'ERR' : -1}
    return DATA_FRAME

url = 'https://gsm-dustdata.firebaseio.com'

def dataSynchronization(url, dataFrame): 
    fbase = firebase.FirebaseApplication(url, None)
    try:
        fbase.put('/','data', dataDecode(dataFrame))
        print("Synchronization Success")
    except Exception as e:
        print("ERROR: fail to update data")
        
def dataAccumulation(url, dateValue, dataFrame):
    fbase = firebase.FirebaseApplication(url, None)
    try:
        fbase.put('/', 'AccData', {dateValue:dataDecode(dataFrame)})
        print("Accumulation Success")
    except Exception as e:
        print("ERROR: fail to update data")
        
while 1:
    SYS_DATA_FRAME = dataRequest('^')
    print(SYS_DATA_FRAME)
    print('updating data')
    dataSynchronization(url, SYS_DATA_FRAME)
    dataAccumulation(url, str(getDateValue()), SYS_DATA_FRAME) 
    print('done..')
