import signal
from contextlib import contextmanager
import serial
from firebase import firebase
import time

class DataManager():
    def __init__(self):
        self.ser = serial.Serial(port='/dev/ttyS0',baudrate=9600)
        self.url = 'https://gsm-dustdata.firebaseio.com'
        self.fbase = firebase.FirebaseApplication(self.url, None)
        self.now = time.localtime()
        self.key = "%04d%02d%02d%02d%02d%02d" % tuple(tm for tm in self.now[:6])

    @contextmanager
    def timeout(self, time):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(time)
        try:
            yield
        except TimeoutError:
            pass
        finally:
            signal.signal(signal.SIGALRM, signal.SIG_IGN)

    def raise_timeout(self, signum, frame):
        raise TimeoutError

    def getDateValue(self):
        return self.key

    def dataRequest(self, request_code = ''):
        self.ser.write(request_code.encode('utf-16'))
        print("requesting data")
        with self.timeout(5):
            try:
                dataFrame = self.ser.readline().decode()
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
                return [int(-1)]

    def dataDecode(self, data_list):
        if len(data_list) < 2:
            return {'ERR' : -1}
        return {'PM1.0': data_list[2], 'PM2.5' : data_list[3],
                'PM10' : data_list[4], 'V_SYSTEM' : data_list[6] / data_list[7],
                'V_SOLAR' : data_list[9] / data_list[10], 'TEMPURATURE' : data_list[11],
                'HUMIDITY' : data_list[12], 'ERR' : 0}
        
    def dataSynchronization(self, dataFrame): 
        try:
            self.fbase.put('/','data', self.dataDecode(dataFrame))
            print("Synchronization Success")
        except:
            print("ERROR: fail to update data")
            
    def dataAccumulation(self, dateValue, dataFrame):
        try:
            self.fbase.put('/', 'AccData', {dateValue:self.dataDecode(dataFrame)})
            print("Accumulation Success")
        except:
            print("ERROR: fail to update data")
        
if __name__ == "__main__":
    DM = DataManager()
    while 1:
        SYS_DATA_FRAME = DM.dataRequest('^')
        print(SYS_DATA_FRAME)
        print('updating data')
        DM.dataSynchronization(SYS_DATA_FRAME)
        DM.dataAccumulation(str(DM.getDateValue()), SYS_DATA_FRAME)
        print('done..')
