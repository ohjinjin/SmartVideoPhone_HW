#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import socket
import threading
import os
import sys


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
trig=[2,5,7]
echo=[3,6,8]
result=[500,500,500]
DT=17
SCK=27
sample=0
pre_gram=0
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       

s.connect(('192.168.0.17', 8080))       #TCP/IP 통신 소켓을 생성하고 서버와의 연결을 시도한다.

def get_weight():                       #무게센서를 통해서 물체의 무게 측정하여 send_weight()함수로 전달한다.
    i=0
    Count=0
    GPIO.setup(DT,GPIO.OUT)
    GPIO.output(DT,1)
    GPIO.output(SCK,0)
    GPIO.setup(DT,GPIO.IN)
    while GPIO.input(DT)==1:
        i=0
    for i in range(24):
        GPIO.output(SCK,1)
        Count=Count<<1
        GPIO.output(SCK,0)
        if GPIO.input(DT)==0:
            Count=Count+1
    GPIO.output(SCK,1)
    Count=Count^0x800000
    GPIO.output(SCK,0)
    
    return Count

def send_weight():                      #쇼핑카트에 물체가 들어왔는지 나갔는지를 판단해주기 위해서             
    global pre_gram                     #쇼핑카트의 무게센서를 이용하여 측정된 이전의 무게와 현재의 무게를 비교해서
    w=0                                 #무게의 증가,감소,그대로인지를 판단하여 전달한다.
    result_gram=0
    count=[]
    plus=[]
    minus=[]
    equal=[]
    for each in range(3):               #무게센서가 튀는 값을 생각하여 get_weight()함수를 통해서 
        count.append(get_weight())      #무게를 3번 측정하여 저장한다.
        time.sleep(0.5)
    
    cntArr={"+":0, "-":0, "=":0}
    
    for i in range(len(count)):         
        w=((sample-count[i])/106)       
    
        gram=max(0,round(w))
        count[i] = gram
        result_gram=gram-pre_gram
        if result_gram>80:
            cntArr['+'] += 1
            plus.append(count[i])
        elif result_gram<-80:
            cntArr['-'] += 1
            minus.append(count[i])
        else:
            cntArr['='] += 1
            equal.append(count[i])
    
    Max = cntArr["+"]
    MaxK = "+"
    for (eachK,eachV) in cntArr.items():
        if eachV > Max:
            Max = eachV
            MaxK = eachK
            

    if MaxK=="+": #plus min
        pre_gram = min(plus)
    elif MaxK =="-":# minus max
        pre_gram = max(minus)
    else:#equal min
        pre_gram = min(equal)
    print(MaxK)
    return MaxK

def setup():                            #라즈베리파이에 연결된 모든 GPIO포트를 설정 및 초기화 해준다.
    GPIO.setup(SCK,GPIO.OUT)
    for i in range(0,3):
        GPIO.setup(trig[i],GPIO.OUT)
        GPIO.setup(echo[i],GPIO.IN)
        GPIO.output(trig[i],GPIO.LOW)
        
        
def get_ip_address():                   #와이파이 연결에 따라 라즈베리파이 자신의IP주소를 가져온다.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('8.8.8.8',80))
    get_ip=sock.getsockname()[0]
    
    return get_ip

def runStream():                        #라즈베리파이 terminal 창의 shell프로세스 명령어를 이용하여 웹을 통한
    print("runStream called")           #파이카메라의 영상스트리밍을 실행한다.
    os.system('sh mjpg.sh')
    
def killStream():                       #몇초간 웹을 통한 영상스트리밍을 실행한 후에 killall명령어를 통해
    time.sleep(7)                       #실행중인 웹 영상스트리밍 shell프로세스를 종료시키고
    os.system('killall -9 mjpg_streamer')#무게측정을 통해 판단한 값을 서버로 전송한다.
    os.system('killall -9 sh')
    s.send(send_weight().encode())

def send_server():                      #웹을 통한 영상스트리밍이 시작이 되면 서버에 영상스트리밍을 시작했다는 문자열과
    print('send_start')                 #자신의 IP번호와 지정된 PORT번호로 생성된 웹주소를 서버에 전달한다.
    tmpStr = 'darknet.exe detector demo data/obj.data data/yolo-obj.cfg yolo-obj_last.weights http://'+my_ip+':8091/?action=stream'
    s.send(tmpStr.encode())             
    print('send_end')    
    
def dis(num):                           #초음파 거리 센서를 이용하여 물체의 거리를 측정한다.   
    GPIO.output(trig[num],False)         
    time.sleep(0.01)
    
    GPIO.output(trig[num],True)
    time.sleep(0.00001)
    
    GPIO.output(trig[num],False)
    
    while GPIO.input(echo[num])==0:
        pulse_start=time.time()
        
        
    while GPIO.input(echo[num])==1:
        pulse_end=time.time()

    pulse_duration=pulse_end-pulse_start
    distance=pulse_duration*17000
    distance=round(distance,2)
    
    return distance


try:                                    #프로그램을 실행하면 서버소켓이 먼저 연결이 된 후 처음시작되는 부분이다.
    my_ip=get_ip_address()              #동작순서   1.자신의 IP주소를 불러온다.
    print(my_ip)

    setup()                             #           2.모든 GPIO(초음파,무게센서)설정한다.
    sample=get_weight()
    while True:
        for i in range(0,3):
            result[i]=dis(i)            #           3.3개의 초음파 센서로 거리를 측정한다.
                        
            if result[i]<50 and result[i] >=3:     #4.지정한 범위 내의 물체가 들어오면 multi-thread메소드를 통해 영상스트리밍함수,메시지 전달 함수를 실행한다.
                print("distance",i+1 ,": ",result[i],"cm")
                t = threading.Thread(target=runStream)
                t2 = threading.Thread(target=send_server)
                t.start()
                t2.start()
                killStream()            #           5.multi-thread메소드가 실행 된 후 웹 영상 스트리밍을 종료시키는 함수를 실행한다.
                                        #           6.무한 루프문을 통해 1-5과정이 반복된다.
            
except :
        GPIO.cleanup()
        


