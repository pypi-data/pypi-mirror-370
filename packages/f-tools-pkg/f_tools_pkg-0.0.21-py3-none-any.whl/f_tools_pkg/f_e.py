import os
import subprocess
import time
class yc_e:
    def __init__(self,times,timeout=None):
        self.timeout = timeout
        for num in range(0,times):
            ret = os.popen("e z").readlines()
            if ret[0].find("sync 0 = 02")!=-1:
                break
        if(num >=times-1):  
            print("can't e command")
            
    def cmdrun(self,command, timeout_duration=None):
        try:
            if(timeout_duration==None):
                timeout_duration = self.timeout
            command = command.strip().split(" ")
            print(command)
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout_duration,
            )
            return result.stdout.strip().split('\n')  # 返回正确执行时的输出
        except subprocess.TimeoutExpired:
            print(f"Calling {command}, timed out after {timeout_duration:02x} seconds.")
            raise 
            
    def e_k(self):
        self.cmdrun("e k")
        
    def e_p(self):
        while True:
            ret =  self.cmdrun("e p")[0]
            print(ret)
            if ret.find("Stopped") != -1:
                break
        return int(ret.split(" ")[3].replace(":",""),16)
    
    def e_pu(self):
        while True:
            ret = self.cmdrun("e pu")[0]
            print(ret)
            if ret.find("Stopped") != -1:
                break
        return int(ret.split(" ")[3].replace(":",""),16)

    def e_pr(self):
        while True:
            ret = self.cmdrun("e pr")[0]
            print(ret)
            if ret.find("Stopped") != -1:
                break
        return int(ret.split(" ")[3].replace(":",""),16)
    
    def e_tu(self):
        addr = -1
        ret = self.cmdrun("e tu")[0]
        print(ret)
        if ret.find("CPU") != -1:
            addr = int(ret.split(" ")[3].replace(":",""),16)
        return addr
    
    def e_nu(self):
        addr = -1
        ret = self.cmdrun("e nu")[0]
        print(ret)
        if ret.find("CPU") != -1:
            addr = int(ret.split(" ")[3].replace(":",""),16)
        return addr
    
    def e_cu(self):
        ret = self.cmdrun("e cu")[0]
        print(ret)
        return self.e_au()
        
    def e_bu(self,addr,type=0):
        ret = self.cmdrun("e bu " + self.tohex(addr) +" "+ self.tohex(type))[0]
        print(ret)
    
    def e_ru(self,reg,val=None):
        if(val!=None):
            ret = self.cmdrun("e ru "+reg+" "+self.tohex(val))[0]
        else:
            ret = self.cmdrun("e ru "+reg)[0]
            print(ret)
            return [int(ret.split(" ")[1],10),ret.split(" ")[3].strip()]
        
    
    def e_au(self):
        isstop = 0
        pc = 0
        ret = self.cmdrun("e au")[0]
        if ret.find("Stopped") != -1:
            isstop = 1
        else:
            isstop = 0
        pc = int(ret.split(" ")[3].replace(":",""),16)
        return [isstop,pc]
    
    def tohex(self,d):
        return hex(d).replace("0x","")
            
    def get_mem_data(self,addr,len):
        result = self.cmdrun("e "+self.tohex(addr)+"l"+self.tohex(len),self.timeout+int(len/500))
        odata=[]
        for line in result[1:]:
            for data in line.split(":")[1].strip().split(" "):
                odata.append(int(data,16))
        return odata
    
    def get_byte(self,addr):
        ret = self.get_mem_data(addr,1)
        return ret[0]

    def get_word(self,addr):
        ret = self.get_mem_data(addr,2)
        return ret[0] + (ret[1] << 8)

    def get_dword(self,addr):
        ret = self.get_mem_data(addr,4)
        return ret[0] + (ret[1] << 8) + (ret[2] << 16) + (ret[3] << 24)
    
    #addr:int 
    #data:str
    def set_data(self,addr,data):
        self.cmdrun("e "+self.tohex(addr)+" "+data)

    def set_byte(self,addr,data):
        self.set_data(addr,("%02x" %data))

    def set_word(self,addr,data):
        self.set_data(addr,("%04x" %data))

    def set_dword(self,addr,data):
        self.set_data(addr,("%08x" %data))

    def e_fu(self,ind):
        CPUB_ICE_REGSEL = 0x8209
        CPUB_ICE_STATUS = 0x8204
        self.set_byte(CPUB_ICE_REGSEL,ind)
        ret = self.get_byte(CPUB_ICE_STATUS)>>2 & 1
        return ret

# print(f'{5:08x}')
# os.environ["baud"]="80"       
# e = yc_e(10,20)
# try:
#     t=time.time()
#     print(e.get_mem_data(0x8000,10))
#     print(time.time()-t)
    
#     print(e.e_p())
#     print(e.e_k())
#     print(e.e_pu())
#     print(e.e_tu())
#     print(e.e_au())
#     print(e.e_ru("pdata"))
#     print(e.e_ru("pdata",0x55))
#     print(e.e_ru("pdata"))
    
#     print(e.get_byte(0x8000))
#     print(e.get_byte(0x8001))
#     print(e.get_word(0x8000))
#     print(e.get_dword(0x8000))
    
#     print(e.e_fu(0))
# except:
#     print("error")
