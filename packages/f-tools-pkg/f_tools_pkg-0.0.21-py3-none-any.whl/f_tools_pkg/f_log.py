import time
import datetime

class file_log:
    def __init__(self,filepath):
        self.filepath = filepath
        self.f = open(self.filepath,"a")
        self.f.close()
        self.last_timepoint = 0
        self.now_timepoint = 0
        print("open " + filepath + " OK")

    def log_write(self,strdata):
        self.f = open(self.filepath,"a")
        self.f.write(strdata + "\n")
        self.f.close()

    def list_to_str(self,listdata):
        strdata=""
        for i in listdata:
            if str == type(i):
                strdata = strdata + i
            elif int == type(i):
                strdata = strdata + chr(i)

        return strdata

    def filelog(self,str_data,isecho=True):
        wbuf = ''
        if  list == type(str_data):
            wbuf = self.list_to_str(str_data)
        else:
            wbuf = str_data

        self.log_write(wbuf)

        if True == isecho:
            print(wbuf)

    def filetimelog(self,strdata,isecho=True,isprintgap=False):
        self.now_timepoint = time.time()
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        if True == isprintgap:
            gap = int(self.now_timepoint*1000 - self.last_timepoint*1000)
            w_data = timestamp + " " + strdata + " gap= " + str(gap) +("timeover" if gap > 1000 else "")
        else:
            w_data = timestamp + " " + strdata

        self.log_write(w_data)

        if True == isecho:
            print(w_data)

        self.last_timepoint = self.now_timepoint



