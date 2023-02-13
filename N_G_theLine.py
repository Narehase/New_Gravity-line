#======================
import numpy as np
import cv2
import os

import math
import time

#각 모듈 불러오기
#====================== 

def IntToAlpabet(Wa):
    if Wa > 25:
        Wa = 25
        
    al = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return str(al[Wa])

def IntToAlpabet_s(Wa):
    if Wa > 25:
        Wa = 25
        
    al = "abcdefghijklmnopqrstuvwxyz"
    return str(al[Wa])

class Gravity:
    def __init__(self, reZeroset = [500,500], D_acc = [0.,0.],frame_time:float = 0.01, unit:float = 1., G:float = 1. , Util = "Y"): # 함수 초기 설정 및 초기화
        # pixel_size 단위는 미터\
        self.Util = Util
        self.G = G
        self.num_ = 0
        self.dt= 0
        self.Set_List = []
        self.Gra = []
        self.rx = reZeroset[0]
        self.ry = reZeroset[1]
        self.Dacc = D_acc
        self.frame_t = frame_time
        self.unit = unit
        self.V = 0

    def set_fild(self, size = [1000,1000]): # 화면 표시영역 크기 설정
        self.fild = np.zeros([size[0],size[1],3])
        self.fild_size = size
        self.cov = self.fild.copy()

    def sets(self, name:str, m:float, r:float, acc = [0.,0.], axis = [0,0], color = [0,255,100], Move = "Y"): # 각 객체 저장
        #acc = [0.,0.] || [가속도, 각도]
        ch = False
        for i in self.Set_List:
            if i[0] == name:
                for al in range(26):
                    plus_text = IntToAlpabet_s(al)
                    rename = name + "_{}".format(plus_text)
                    for i in self.Set_List:
                        if i[0] == rename:
                            ch = True
                            break
                    if(al == 25 and i[0] == rename):
                        print("같은 이름이 너무 많습니다! 객체별 이름을 다르게 설정해 주세요!")
                        raise
                    if ch:
                        ch = False
                        continue                    
                    if(i[0] != rename):
                        print("같은 이름의 객체가 존재합니다. 이에 {} 의 객체명을 {}로 변경 합니다.".format(name,rename))
                        name = rename
                        break
        past_po = []  
        self.Set_List.append([name, m, r, acc, axis, color, Move, 0, past_po])
        self.Pick(axis,r,color)
    
    def Pick(self, axis, r, color = [0,0,255]):
        for i in range(r):
            i += 1
            for ip in range(360):
                
                rad = math.radians(ip)

                x = int(i*math.cos(rad)) + self.rx
                y = int(i*math.sin(rad)) + self.ry
                
                y = int(axis[1])+y
                x = int(axis[0])+x
                try:
                    if x < 0 or x > self.fild_size[1]:
                        raise
                    if y < 0 or y > self.fild_size[0]:
                        raise
                    self.fild[y,x] = color
                except:
                    pass

    def Nuton(self):
        List_r = []
        for A in self.Set_List:
            L1 = []
            for B in self.Set_List:
                if A != B:
                    F, Seta = self.__A_to_B__(A,B)
                    L1.append([Seta,F])
                
            x = 0.
            y = 0.
            for L2 in L1: # 벡터 합성
                x += L2[1]*math.cos(math.radians(L2[0])) 
                y += L2[1]*math.sin(math.radians(L2[0]))
            
            #가속도 분해 합성
            x += self.Dacc[1]*A[1]*math.cos(math.radians(self.Dacc[0]))
            y += self.Dacc[1]*A[1]*math.sin(math.radians(self.Dacc[0]))

            #가속도 분해 합성
            x += A[3][1]*A[1]*math.cos(math.radians(A[3][0]))
            y += A[3][1]*A[1]*math.sin(math.radians(A[3][0]))

            
            #각도 구하기
            Seta = math.atan2(y,x)*(180/math.pi)
            All_Acc = math.sqrt((x**2)+(y**2)) / A[1] # F -> a (F=ma -> a = F/m)
            

            V = All_Acc * self.frame_t

            Displacement = V*self.frame_t
        

            Date = self._Draw_(A[4],Seta,Displacement,100,name=[A][0])
            DeV = self._Draws_(A[4],Seta,Displacement,A[0],A[8])
            if A[6] == "Y" or A[6] == "y":
                List_r.append([A[0],A[1],A[2],[Seta,Displacement],Date,A[5],A[6],V, DeV])
            elif A[6] == "N" or A[6] == "n":
                List_r.append([A[0],A[1],A[2],[Seta,All_Acc],A[4],A[5],A[6],V, A[8]])
            else:
                print("sets의 변수 Move 는 Y 또는 N이어야 합니다.")
                raise TypeError

        self.List_r = List_r
                        
    def Update(self):
        subfild = cv2.resize(self.fild, [900,900])
        cv2.imshow("G",subfild)
        cv2.waitKey(1)
        self.dt += self.frame_t
        self.fild = self.cov.copy()
        self.Set_List = self.List_r
        for A in self.Set_List:
            self.Pick(A[4],A[2],A[5])

    def Navi(self):
        os.system("cls")
        print("{}second ===============/\\".format(str(self.dt)[0:5]) )
        for A in self.Set_List:
            print("{} | V: {}".format(str(A[0])[0:6],str(A[7])[0:6]))

    def _Draws_(self, Axis,Seta,Acc,name = "", sapari:list = []):
        # return []
        # print(len(sapari))
        deV = sapari
        x_s = (Acc * math.sin(math.radians(Seta)) + Axis[0])
        y_s = (Acc * math.cos(math.radians(Seta)) + Axis[1])     
        # deV = sapari
        if len(deV) > 59:
            deV = deV[1:]
        deV.append([x_s,y_s])
        xo = self.rx
        yo = self.ry
        for pca in range(len(deV) - 1):
            # print(pca)
            cp = deV[pca]
            pos = deV[pca+1]
                
            xd = pos[0] - (cp[0])
            yd = pos[1] - (cp[1])
            
            Squid = math.sqrt((xd*xd)+(yd*yd))    
            Seta = math.atan2(xd,yd)*(180/math.pi) 
            # cv2.line(self.fild,(int(cp[0]+ xo),int(cp[1]+ yo)),(int(pos[0]+ xo),int(pos[1]+ yo)),(255,0,0),1)
            
            for ip in range((round(Squid))):
                xs = int(ip * math.sin(math.radians(Seta))) + int(cp[0] + xo)
                ys = int(ip * math.cos(math.radians(Seta))) + int(cp[1] + yo)
                # print(x,y)
                if xs >= 0 and xs < int(self.fild_size[0]) - 2:
                    if ys >= 0 and ys < int(self.fild_size[1]) - 2:
                        # print(x,y)
                        # print(self.fild_size)
                        # print( y< int(self.fild_size[1]) - 2)
                        
                        self.fild[ys,xs] = [0,100,0]
                        # self.cov[ys,xs] = [0,100,0]
            
        return deV

    def _Draw_(self,Axis,Seta,Acc,Lagrangu,J = 0, name = "") -> list:
        
        x_s = (Acc * math.sin(math.radians(Seta)) + Axis[0])
        y_s = (Acc * math.cos(math.radians(Seta)) + Axis[1])
        
        for i in range(round(Lagrangu)):
            x = int(i * math.sin(math.radians(Seta)) + self.rx + Axis[0])
            y = int(i * math.cos(math.radians(Seta)) + self.ry + Axis[1])
            
            try:                   
                if x < 0 or x > self.fild_size[0]-1:
                    # print("err60")
                    pass
                elif y < 0 or y > self.fild_size[1]-1:
                    pass
                else:
                    if J == 0:
                        self.fild[y,x] = [100,100,100]
                    elif J == 1:
                        
                        self.fild[y,x] = [0,0,10]
            except:
                pass

        xp = int(Axis[0])+self.rx
        yp = int(Axis[1])+self.ry

        if xp < 0 or xp > self.fild_size[0] -1:
            pass
        elif yp < 0 or yp > self.fild_size[1] -1:
            pass
        else:
            if self.Util == "Y" or self.Util == "y":
                self.fild[yp,xp] = [0,100,0]
                self.cov[yp,xp] = [0,100,0]
  
                for Ai in self.Set_List:
                    if Ai == name:
                        pos = Ai[4]
                        # print(f"{pos=}")
                        # print(xp,yp)
                        xd = pos[0] - (x_s)
                        yd = pos[1] - (y_s)

                        # print((int(xp),int(yp)),(int(pos[0]) + self.rx,int(pos[1])+self.ry) , "<--- err _d")
                        # cv2.line(self.cov,(int(xp),int(yp)),(int(pos[0]),int(pos[1])),(255,0,0),1)
                        # cv2.line(self.fild,(xp,yp),(pos[0],pos[1]),(255,0,0),1)

                        a = np.array([x_s,y_s])
                        b = np.array(pos)
                        
                        # print(f"{dist=}")
                        
                        
                        Squid = math.sqrt((xd*xd)+(yd*yd))
                        
                        for ip in range((round(Squid))):
                            xs = int(ip * math.sin(math.radians(Seta)) + self.rx + Axis[0])
                            ys = int(ip * math.cos(math.radians(Seta)) + self.ry + Axis[1])
                            # print(x,y)
                            if xs >= 0 and xs < int(self.fild_size[0]) - 2:
                                if ys >= 0 and ys < int(self.fild_size[1]) - 2:
                                    # print(x,y)
                                    # print(self.fild_size)
                                    # print( y< int(self.fild_size[1]) - 2)
                                    
                                    self.fild[ys,xs] = [0,100,0]
                                    self.cov[ys,xs] = [0,100,0]
                                    pass
                        break
                


        
                            
        return [x_s,y_s]
            

    def __A_to_B__(self,A,B):
        G = 1.

        y = B[4][0] - A[4][0]
        x = B[4][1] - A[4][1]
        Squid = math.sqrt((x*x)+(y*y)) * self.unit
        
        if Squid <= 20:
            F = 0.
        else:
            F = self.G*((A[1]*B[1]) / Squid**2)
        
        Seta = math.atan2(y,x)*(180/math.pi) 

        return F,Seta


def rand_ty():
    a = np.random.randint(0,1000)
    b = np.random.randint(0,1000)
    #print(a," :: ",b)
    return[a-500,b-500] 

def kusari():
    a = np.random.randint(0,360)
    b = np.random.randint(1,20)
    return[a,b]

a = Gravity([500,500],D_acc=[0,0],frame_time=1, G= 1.5, Util = "")
a.set_fild(size=[1000,1000])
# for i in range(5):
#     a.sets("aa",5,5,[0, 9.8],rand_ty())


a.sets("ABC2",5,5,[0.,18],[-100,-100],[0,0,255])
a.sets("ABC3",5,5,[90.,18],[-100,100],[0,0,255])
a.sets("ABC4",5,5,[-90.,18],[100,-100],[0,0,255])
a.sets("ABC4",5,5,[180.,18],[100,100],[0,0,255])
a.sets("ABC",25000,5,[180.,10.],[0,0],[0,0,255],"N")

# a.sets("ABC",50,5,[100.,14],[-500,-500],[0,0,255])

et = time.time()
# for i in range(100):
while True:
    a.Nuton()
    a.Navi()
    a.Update()

    # 속도 = 가속도
    # 해당 시뮬레이션은 각 물체에게 가해지는 힘이 동일 하지 않아
    # 등가속도 식을 이용해서는 안되지만 해당 식이 사용되었기에 비슷한 상황을 보기 위해서는
    # t = 1 로 설정을 하였습니다.
    # 이에 V = at + v0 라는 식에 의해 V == a 라는 식이 완성됩니다.
    # 이에 가속도는 곧 속도가 됩니다.
print(time.time() - et)
# a.sets("ABC1",50,5,[180.,14],[200,200],[0,0,255])
# a.sets("ABC2",50,5,[0.,14],[-200,-200],[0,0,255])
# a.sets("ABC",24000,5,[180.,10.],[0,0],[0,0,255],"N")
    
# a.sets("ABC1",50,5,[180.,14],[100,100],[0,0,255])
# a.sets("ABC2",50,5,[0.,14],[-100,-100],[0,0,255])
# a.sets("ABC3",50,5,[90.,14],[-100,100],[0,0,255])
# a.sets("ABC4",50,5,[-90.,14],[100,-100],[0,0,255])
# a.sets("ABC",25000,5,[180.,10.],[0,0],[0,0,255],"N")


#11.295356273651123
