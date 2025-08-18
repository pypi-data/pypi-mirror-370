import serial
import struct
import time
from time import sleep

class serialx:
    def __init__(self,COMX_i,baund,stopbits):
        COMX=COMX_i
        self.serial = serial.Serial(COMX,baund,stopbits=2)
        if self.serial.is_open:
            print(COMX,"open success")
        else:
            print(COMX,"open failed")
        print(self.serial.stopbits)
        

    def pinfo1(self,m):
        if m==ord('\n'):
            print("\n       ",end="")
        elif m == ord("\r"):
            pass
        else:
            print(chr(m),end="")
            
    def recv(self):
        while True:
            data = self.serial.read(1)
            if data == "":
                continue
            else:
                break
            sleep(0.00001)
        return int.from_bytes(data,byteorder='little',signed=False)

    #接受串口数据，以二进制写入
    def write(self,data):
        self.serial.write(data)

    def wait_head(self):
        while True:
            is_a5 = self.recv()
            self.pinfo1(is_a5)
            if is_a5 == 0xA5:
                if 0x5A !=self.recv():
                    continue
                else:
                    break
        return 1

    def wait_headpara(self,buf):
        #serial number
        buf[2] = (self.recv())
        buf[3] = (self.recv())

        #test type
        buf[4] = (self.recv())

        #return para num
        buf[5] = (self.recv())
        buf[6] = (self.recv())
        return ((buf[6]<<8) + buf[5])

    def wait_result(self,buf,len):
        for i in range(0,len):
            buf.append(self.recv())
        

    def wait_receive(self,recvdata):
        recvdata.clear()
        recvdatahead = [0xA5,0x5A,0x00,0x00,0x00,0x00,0x00]
        recvdata.extend(recvdatahead)
        self.wait_head()
        r_len = self.wait_headpara(recvdata)
        self.wait_result(recvdata,r_len)
        #return recvdata

    def wait_receive_headpara(self,recvdata):
        recvdata.clear()
        recvdatahead = [0xA5,0x5A,0x00,0x00,0x00,0x00,0x00]
        recvdata.extend(recvdatahead)
        self.wait_head()
        r_len = self.wait_headpara(recvdata)
        return r_len

    def send_cmd(self,type,seq,sendbuf):
        buflen = len(sendbuf)
        sendhead=[0xA5,0x5A,seq&0xff,(seq >> 8) & 0xff,type,buflen&0xff,(buflen >> 8) & 0xff]
        self.write(sendhead+sendbuf)

    def recv_cmd(self,recvbuf):
        r_len = self.wait_receive_headpara(recvbuf)
        for i in range(0,r_len):
            recvbuf.append(self.recv())
        return recvbuf
    
    def send_and_recv_cmd(self,type,seq,sendbuf,recvbuf):
        self.send_cmd(type,seq,sendbuf)
        return  self.recv_cmd(recvbuf)
    