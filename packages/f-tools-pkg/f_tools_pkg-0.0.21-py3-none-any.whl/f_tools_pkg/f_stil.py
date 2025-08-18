import re

class f_stil:
    def __init__(self):
        pass
    def get_pattern(self,path):
        f = open(path,"r");
        f_list = f.readlines();
        f.close()
        scanchain=[[],[]]
        pattern=[]
        multiclock_capture=[[],[],[],[]] # [special _pi, pattern NO., _pi Pattern(GPIO), special pattern]
        scan_pin={"CLK":-1,"COM":-1,"EN":-1,"SI":-1,"SO":-1}
        patternlength =0;
        p = 0
        flag=0
        p_flag=0
        s_flag=0
        l_flag=0
        m_flag=0 # multiclock_capture
        clk_flag=0
        com_flag=0
        pi_flag =0
        chainno=0
        scan_in=""
        scan_out=""
        tmp_pat=""
        for i in range(0,len(f_list)):
            # find scan clk
            if clk_flag < 2 and scan_pin["CLK"] == -1:
                obj = re.match("\s*Ann {\*\s*clock_name\s*.*",f_list[i])
                if(obj):
                    clk_flag +=1
                    continue
                obj = re.match("\s*Ann {\*\s*GPIO\[(\w+)\].*",f_list[i])
                if obj:
                    scan_pin["CLK"] = int(obj.group(1))
                    clk_flag +=1
                    continue
            # find scan compress
            if com_flag < 2 and scan_pin["COM"] == -1:
                if f_list[i].find("constraint_value"):
                        com_flag = 1
                obj = re.match("\s*Ann {\*\s*GPIO\[(\w+)\]\s*(\w+)\s*.*",f_list[i])
                if obj:
                    scan_pin["COM"]={int(obj.group(1)),obj.group(2)}
                    com_flag +=1
                    continue
            # find scan enable
            if scan_pin["EN"] == -1:
                obj = re.match("\s*\"ScanCompression_mode_pre_shift\".*\"GPIO\[(\w+)\]\".*",f_list[i])
                if obj:
                    scan_pin["EN"]=int(obj.group(1))
                    continue
            # find pi
            if pi_flag < 2:
                if f_list[i].find("\"_pi\"") != -1:
                    pi_flag = 1
                    tmp_pat += f_list[i]
                    continue
                if pi_flag ==1:
                    tmp_pat += f_list[i]
                    if f_list[i].find("\'") != -1 :
                        pi_flag =2    
                        for i in tmp_pat.split('\'')[1].strip().split("+"):
                            obj = re.match("\s*\"GPIO\[(\w+)\]\"",i.strip()) 
                            if obj : 
                                multiclock_capture[2].append(int(obj.group(1)))
                            if i.find("RSTN") != -1:
                                multiclock_capture[2].append("R")
                        continue
            # find scan IO
            if p_flag < 2:
                obj = re.match("\s*Scan(.+) \"GPIO\[(\w+)\]\"",f_list[i])
                if obj:
                    if obj.group(1).lower() == "in":
                        scan_in = obj.group(2)
                        p_flag +=1
                    if obj.group(1).lower() == "out":
                        scan_out = obj.group(2)
                        p_flag +=1
                    if p_flag == 2:
                        # print("si:%s so:%s" %(scan_in,scan_out))
                        scan_pin["SI"]=scan_in
                        scan_pin["SO"]=scan_out
            #find scanStructures
            if s_flag == 0:
                obj =re.match("\s*ScanChain \"(chain)*(sccompin)*(sccompout)*(\d+)\" {\s*",f_list[i])
                if obj:
                    s_flag =1
                    if(obj.group(2) or obj.group(3)):
                        l_flag = 1
                    chainno = int(obj.group(4))
                    continue
            else:
                obj = re.match("\s*ScanLength (\w+);\s*",f_list[i])
                chainlen = int(obj.group(1))
                if(l_flag):
                    l_flag = 0
                    patternlength = int(obj.group(1))
                else:
                    if chainlen not in scanchain[0]:
                        scanchain[0].append(chainlen)
                        scanchain[1].append([chainno])
                    else:
                        idx = scanchain[0].index(chainlen)
                        scanchain[1][idx].append(chainno)
                s_flag = 0
                
            # find scan pattern
            if flag==0:
                obj=re.match("\s*\"pattern (\w+)\": Call \"load_unload\" {\s*",f_list[i])
                if obj:
                    flag = 1
                    p = int(obj.group(1),10)
                    pattern.append(["",""])
                    tmp_pat = ""
                    # print(p)
                    continue
            if flag >=1:
                tmp_pat += f_list[i].strip()
                if f_list[i].find(";") != -1:
                    obj = re.match("\s*\"GPIO\[(\w+)\]\"=\s*(.*);\s*}?",tmp_pat)
                    if obj:
                        if obj.group(1) == scan_in:
                            flag = 2 #scan in
                        elif obj.group(1) == scan_out:
                            flag = 3 #scan out
                        pattern[p][flag-2] += obj.group(2).strip()
                        tmp_pat = ""
                if f_list[i].find("Call \"multiclock_capture\"")!=-1:
                    flag =0
                    m_flag = 1;
                    tmp_pat = "";
                    continue
            if m_flag >=1:
                tmp_pat += f_list[i].strip()
                if f_list[i].find("}") != -1:
                    m_flag = 0
                    obj = re.match("\s*\"_pi\"=(.+);\s*\"_po\"=(.+);\s*}",tmp_pat)
                    if obj:
                        tmp_pi = obj.group(1).strip()
                        tmp_po = obj.group(2).strip()
                        if(tmp_pi != tmp_po):
                            print("multiclock_capture: not same pi po %d",p)
                        if scan_pin["EN"] != -1 and scan_pin["CLK"] != -1:
                            if tmp_pi[multiclock_capture[2].index(scan_pin["EN"])] == '1' or \
                            tmp_pi[multiclock_capture[2].index(scan_pin["CLK"])] =='0':
                                tmp = tmp_pi
                                multiclock_capture[3].append(p)
                                if tmp not in multiclock_capture[0]:
                                    multiclock_capture[0].append(tmp)
                                    multiclock_capture[1].append([p])
                                else:
                                    idx = multiclock_capture[0].index(tmp)
                                    multiclock_capture[1][idx].append(p)
        print("scan pins",scan_pin)
        print("patternlength:",patternlength)
        totalbits = 0
        for l in scanchain[0]:
            plist = scanchain[1][scanchain[0].index(l)]
            slen = len(plist)
            print(l,slen,plist)
            totalbits += slen * l
        print("total %d pattern, %d bits" %(len(pattern),totalbits))    
        print("_pi :",multiclock_capture[2])    
        for l in multiclock_capture[0]:
            print(l,multiclock_capture[1][multiclock_capture[0].index(l)])
        print("special pattern :",multiclock_capture[3])  
        return [patternlength,pattern,multiclock_capture,scan_pin]

    def set_pattern(self,s,e,pattern):
        fi= open("pattern_i.h","w")
        fi.write("#include \"type.h\"\n")
        fo=open("pattern_o.h","w")
        fo.write("#include \"type.h\"\n")
        
        for i in range(s,e):
            fi.write(f"uint8_t pattern_i"+str(i)+"[]={\n")
            n = 0
            v = 0
            for c in pattern[i][0]:
                fi.write(c+",")
                if n %16==15:
                    fi.write("/*"+hex(n>>4)+"*/ \n")
                n+=1
            fi.write("};\n")
            
            fo.write("uint8_t pattern_o"+str(i)+"[]={\n")
            n = 0
            for c in pattern[i][1]:
                if(c=="H"):
                    t = 1;
                elif(c=="L"):
                    t = 0
                else:
                    t = 2

                fo.write(str(t)+",")
                if n %16==15:
                    fo.write("/*"+hex(n>>4)+"*/ \n")
                n+=1
            fo.write("};\n")
        fi.write("uint8_t *pattern_i[] = {")
        for i in range(0,e-s):
            fi.write(f"pattern_i{i},")
        fi.write("};\n")
        
        fo.write("uint8_t *pattern_o[] = {")
        for i in range(0,e-s):
            fo.write(f"pattern_o{i},")
        fo.write("};\n")
        
        fi.close()
        fo.close()   