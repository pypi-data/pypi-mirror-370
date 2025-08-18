import array
import struct

class bmp_gray:
    def __init__(self, w=1080, h=1920):
        self.w = w
        self.h = h
        self.location = 0
        
    def calc_data_size (self):
        if((self.w)%4 == 0):
            self.dataSize = self.w * self.h
        else:
            self.dataSize = (((self.w) // 4 + 1) * 4) * self.h

        self.fileSize = self.dataSize + 54 + 1024 
    
    def _conv2byte(self, l, num, len):
        tmp = num
        for i in range(len):
            l.append(tmp & 0x000000ff)
            tmp >>= 8    
    
    def gen_bmp_header (self):
        self.calc_data_size();
        self.bmp_header = [0x42, 0x4d]
        self._conv2byte(self.bmp_header, self.fileSize, 4) #file size
        self._conv2byte(self.bmp_header, 0, 2)
        self._conv2byte(self.bmp_header, 0, 2)
        self._conv2byte(self.bmp_header, 54 + 1024, 4) #rgb data offset

        self._conv2byte(self.bmp_header, 40, 4) #info block size
        self._conv2byte(self.bmp_header, self.w, 4)
        self._conv2byte(self.bmp_header, self.h, 4)
        self._conv2byte(self.bmp_header, 1, 2)
        self._conv2byte(self.bmp_header, 8, 2) #888
        self._conv2byte(self.bmp_header, 0, 4)  #no compression
        self._conv2byte(self.bmp_header, self.dataSize, 4) #rgb data size
        self._conv2byte(self.bmp_header, 0, 4)
        self._conv2byte(self.bmp_header, 0, 4)
        self._conv2byte(self.bmp_header, 0, 4)
        self._conv2byte(self.bmp_header, 0, 4)
        
    def print_bmp_header (self):
        length = len(self.bmp_header)
        for i in range(length):
            print("{:0>2x}".format(self.bmp_header[i]), end=' ')
            if i%16 == 15:
                print('')
        print('')
        
    def paint_bgcolor(self, color=0xff):
        self.rgbData = []
        for r in range(self.h):
            self.rgbDataRow = []
            for c in range(self.w):
                self.rgbDataRow.append(color)
            self.rgbData.append(self.rgbDataRow)
    
    def paint_point(self, x, y, color=0xff):
        self.rgbData[y][x] = color
    
    def add_point_init(self,loc):
        self.location = loc

    def add_point(self,color):
        x = self.location % self.w
        y = self.location // self.w
        self.rgbData[y][x] = color
        self.location = self.location + 1

    def paint_line(self, x1, y1, x2, y2, color):
        k = (y2 - y1) / (x2 - x1)
        for x in range(x1, x2+1):
            y = int(k * (x - x1) + y1)
            self.rgbData[y][x] = color

    def paint_rect(self, x1, y1, w, h, color):
        for x in range(x1, x1+w):
            for y in range(y1, y1+h):
                self.rgbData[y][x] = color

    def save_image(self, name="save.bmp"):
            f = open(name, 'wb')

            #write bmp header
            f.write(array.array('B', self.bmp_header).tobytes())

            #write bmp color table
            for i in range(256):
                f.write(struct.pack("B",i))
                f.write(struct.pack("B",i))
                f.write(struct.pack("B",i))
                f.write(struct.pack("B",0))

            #write rgb data
            zeroBytes = self.dataSize // self.h - self.w

            for r in range(self.h):
                l = []
                for i in range(len(self.rgbData[r])):
                    p = self.rgbData[r][i]
                    l.append(p & 0xff)

                f.write(array.array('B', l).tobytes())

                for i in range(zeroBytes):
                    f.write(bytes(0x00))

            #close file
            f.close()
            
    # get bmp width and height
    def read_image(self,name="read.bmp"):
        self.f = open(name,'rb')
        self.list_rdbmp = self.f.read()
        self.f.close() 

        self.w = 0
        self.h = 0
        for i in range(0,4):
            self.w = self.w + (self.list_rdbmp[18 + i] << (i * 8))
            self.h = self.h + (self.list_rdbmp[22 + i] << (i * 8))
    
    def read_point(self,x,y):
        if x > self.w - 1 or y > self.h:
            print("point out size")
            return 0
        else:
            return self.list_rdbmp[0x436 + y * self.w + x]
    
    def scale_image(self,scale,iname,oname="scale.bmp"):
        if scale >= 0:
            self.read_image(iname)
            i_h = self.h
            i_w = self.w
            self.w *= scale
            self.h *= scale
            self.gen_bmp_header()
            self.paint_bgcolor(0x00)
            for y in range(0,i_h):
                for n_y in range(0,scale):
                    for x in range(0,i_w):
                        for n_x in range(0,scale):
                            self.paint_point(x*scale+n_x, y*scale+n_y,self.list_rdbmp[0x436 + y * i_w + x])
            self.save_image(oname)
        else:
            scale = abs(scale)
            self.read_image(iname)
            i_h = self.h
            i_w = self.w
            self.w = int(self.w / scale)
            self.h = int(self.h / scale)
            self.gen_bmp_header()
            self.paint_bgcolor(0x00)
            avg=[0]*int(self.w * self.h)
            for y in range(0,i_h):
                    for x in range(0,i_w):
                            avg[int(int(y/scale) * i_w /scale) + int(x/scale)] += self.list_rdbmp[0x436 +y * i_w + x]
                                
            for y in range(0,self.h):
                for x in range(0,self.w):        
                        self.paint_point(x, y,int(avg[y*self.w+x]/(scale*scale)))

            self.save_image(oname)