import signal
from contextlib import contextmanager
import serial

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

def getDateValue(): # current date
  import datetime as d
  today = d.datetime.today()

  year = today.year
  month = today.month
  day = today.day
  hour = today.hour
  minute = today.minute
  second = today.second
  date_value =  str(year) + str(append0(month)) + str(append0(day)) + str(append0(hour)) + str(append0(minute)) + str(append0(second))
  return date_value

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

def dataUpdate(url):
    firebase.FirebaseApplication(url, None)
    fbase.put('PM1.0': data_list[2], 'PM2.5' : data_list[3],
                      'PM10' : data_list[4], 'V_SYSTEM' : data_list[6] / data_list[7],
                      'V_SOLAR' : data_list[9] / data_list[10], 'TEMPURATURE' : data_list[11],
                      'HUMIDITY' : data_list[12], 'ERR' : 0)
    
while 1:
    from firebase import firebase
    import urllib
    from urllib.request import urlopen, Request
    import bs4
    
    enc_location = urllib.parse.quote(location + '+날씨')
    url = "https://search.naver.com/search.naver?ie=utf8&query=" + enc_location
    
    SYS_DATA_FRAME = dataDecode(dataRequest('^'))
    dataUpdate(url)
    # print(SYS_DATA_FRAME)
