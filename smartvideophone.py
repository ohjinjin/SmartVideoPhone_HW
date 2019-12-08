#!/usr/bin/env python
#-*-coding:utf-8-*-
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO Library
import time
import socket
import threading
import pygame
import sys
from PIL import Image
import requests
from io import BytesIO
import pymysql.cursors
#https://raspberrypihq.com/getting-started-with-python-programming-and-the-raspberry-pi/
#https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/
#https://www.instructables.com/id/Raspberry-Pi-Tutorial-How-to-Use-a-Buzzer/
#https://github.com/gumslone/raspi_buzzer_player/blob/master/buzzer_player.py
#https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/
# 클라이언트 별 스레드
class ClientThread(threading.Thread):

    def __init__(self,ip,port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        print ("[+] New thread started for "+ip+":"+str(port))


    def run(self):    
        print ("Connection from : "+ip+":"+str(port))
        while True:
            tmp = clientSock.recv(1024)#.decode()
            if (tmp != ""):
                run_quickstart(tmp)
                pygame.mixer.init()
                #time.sleep(3)
                pygame.mixer.music.load('output.mp3')
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy()==True:
                    continue
            time.sleep(3)
notes = {
    'B0' : 31,
    'C1' : 33, 'CS1' : 35,
    'D1' : 37, 'DS1' : 39,
    'EB1' : 39,
    'E1' : 41,
    'F1' : 44, 'FS1' : 46,
    'G1' : 49, 'GS1' : 52,
    'A1' : 55, 'AS1' : 58,
    'BB1' : 58,
    'B1' : 62,
    'C2' : 65, 'CS2' : 69,
    'D2' : 73, 'DS2' : 78,
    'EB2' : 78,
    'E2' : 82,
    'F2' : 87, 'FS2' : 93,
    'G2' : 98, 'GS2' : 104,
    'A2' : 110, 'AS2' : 117,
    'BB2' : 123,
    'B2' : 123,
    'C3' : 131, 'CS3' : 139,
    'D3' : 147, 'DS3' : 156,
    'EB3' : 156,
    'E3' : 165,
    'F3' : 175, 'FS3' : 185,
    'G3' : 196, 'GS3' : 208,
    'A3' : 220, 'AS3' : 233,
    'BB3' : 233,
    'B3' : 247,
    'C4' : 262, 'CS4' : 277,
    'D4' : 294, 'DS4' : 311,
    'EB4' : 311,
    'E4' : 330,
    'F4' : 349, 'FS4' : 370,
    'G4' : 392, 'GS4' : 415,
    'A4' : 440, 'AS4' : 466,
    'BB4' : 466,
    'B4' : 494,
    'C5' : 523, 'CS5' : 554,
    'D5' : 587, 'DS5' : 622,
    'EB5' : 622,
    'E5' : 659,
    'F5' : 698, 'FS5' : 740,
    'G5' : 784, 'GS5' : 831,
    'A5' : 880, 'AS5' : 932,
    'BB5' : 932,
    'B5' : 988,
    'C6' : 1047, 'CS6' : 1109,
    'D6' : 1175, 'DS6' : 1245,
    'EB6' : 1245,
    'E6' : 1319,
    'F6' : 1397, 'FS6' : 1480,
    'G6' : 1568, 'GS6' : 1661,
    'A6' : 1760, 'AS6' : 1865,
    'BB6' : 1865,
    'B6' : 1976,
    'C7' : 2093, 'CS7' : 2217,
    'D7' : 2349, 'DS7' : 2489,
    'EB7' : 2489,
    'E7' : 2637,
    'F7' : 2794, 'FS7' : 2960,
    'G7' : 3136, 'GS7' : 3322,
    'A7' : 3520, 'AS7' : 3729,
    'BB7' : 3729,
    'B7' : 3951,
    'C8' : 4186, 'CS8' : 4435,
    'D8' : 4699, 'DS8' : 4978
}
deck_the_halls_melody = [
    notes['G5'], notes['F5'], notes['E5'], notes['D5'],
    notes['C5'], notes['D5'], notes['E5'], notes['C5'],
    notes['D5'], notes['E5'], notes['F5'], notes['D5'], notes['E5'], notes['D5'],
    notes['C5'], notes['B4'], notes['C5'], 0,
]


deck_the_halls_tempo = [
    2, 4, 2, 2,
    2, 2, 2, 2,
    4, 4, 4, 4, 2, 4,
    2, 2, 2, 2,
    
    2, 4, 2, 2,
    2, 2, 2, 2,
    4, 4, 4, 4, 2, 4,
    2, 2, 2, 2,
    
    2,4,2,2,
    2,4,2,2,
    4,4,2,4,4,2,
    2,2,2,2,
    
    2, 4, 2, 2,
    2, 2, 2, 2,
    4, 4, 4, 4, 2, 4,
    2, 2, 2, 2,
]

## tcp/ip 소켓 생성
# 접속할 서버 주소
#HOST ='192.168.0.110' # or loopback addr
HOST ='192.168.219.104' # or loopback addr

# 클라이언트 접속을 대기하는 포트 번호
PORT = 8000

# 주소 체계로 IPv4, 소켓 타입으로 TCP 사용
serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 포트 사용중이라 연결할 수 없다는 winError 10048 에러 해결을 위해 필요
serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 네트워크 인터페이스와 포트 번호에 소켓을 바인딩
serverSock.bind((HOST, PORT))


# 안드로이드 스레드들 관리
threads = []

# tcp_client..server와 networking
clientSock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#clientSock_server.connect(("192.168.0.111",8000))
clientSock_server.connect(("192.168.219.107",8000))
buttonClicked = False

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low(off)
GPIO.setup(29,GPIO.OUT)
GPIO.setup(31,GPIO.IN)
GPIO.output(29,GPIO.LOW)
buzzer=16
GPIO.setup(buzzer,GPIO.OUT)

def run_quickstart(str):
    # [START tts_quickstart]
    """Synthesizes speech from the input string of text or ssml.

    Note: ssml must be well-formed according to:
        https://www.w3.org/TR/speech-synthesis/
    """
    from google.cloud import texttospeech

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.types.SynthesisInput(text=str)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='ko-KR',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.MALE)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    # The response's audio_content is binary.
    with open('output.mp3', 'wb') as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
    # [END tts_quickstart]
def getdistance():
    pulse_start = pulse_end = None
    
    GPIO.output(29,False)         
    time.sleep(0.5)
    GPIO.output(29,True)
    time.sleep(0.00001)
    
    GPIO.output(29,False)
    
    while GPIO.input(31)==0:
        pulse_start=time.time()
        
        
    while GPIO.input(31)==1:
        pulse_end=time.time()

    pulse_duration=pulse_end-pulse_start
    distance=pulse_duration*17000
    distance=round(distance,2)
    
    return distance
    
def insertDB():
    conn = pymysql.connect(host='192.168.219.107',
        user='%',#'raspberrypi',
        password='',#'1234',
        db='smartvideophone',
        charset='utf8mb4')
    response = requests.get("http://192.168.219.104:8090/?action=snapshot")
    img = Image.open(BytesIO(response.content))
    #image = Image.open("C:\\Users\\Oh\\Desktop\\images.jpg")
    blob_value = BytesIO(response.content).getvalue()
    try:
        with conn.cursor() as cursor:
            sql = 'INSERT INTO visit_log (image) VALUES (%s)'
            cursor.execute(sql, (blob_value,))
        conn.commit()
        print(cursor.lastrowid)
        # 1 (last insert id)
    finally:
        conn.close()
        
def requestInsert():
    global clientSock_server
    try:
        msg = "triggered"
        clientSock_server.sendall(msg.encode("utf-8"))
    except socket.error, e:
        print("checkkk")
        if isinstance(e.args, tuple):
            print("error no is %d"%e[0])
        else:
            print("socket error", e)
        clientSock_server.close()
        clientSock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #clientSock_server.connect(("192.168.0.111",8000))
        clientSock_server.connect(("192.168.219.107",8000))
        
    #clientSock_server.close()
    
def button_callback(channel):
    print("Button was pushed!")
    # buzerRR
    #play(deck_the_halls_melody, deck_the_halls_tempo, 0.30, 0.800)
    #th = threading.Thread(target=insertDB)
    #th.start()
    #th.join()
    #th = threading.Thread(target=requestInsert)
    #th.start()
    #th.join()
    #clientSock_server.send("triggered".encode("utf-8"))
    global buttonClicked
    buttonClicked = True
    #time.sleep(5)
    #destroy()
    
    # tts "who is this?"
    # Select allfaces from db
    # Get snapshot about stranger's face from raspi-ip:8090 via opencv
    # Recognize the face via opencv

def buzz(frequency, length):     #create the function "buzz" and feed it the pitch and duration)

    if(frequency==0):
        time.sleep(length)
        return
    period = 1.0 / frequency         #in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
    delayValue = period / 2      #calcuate the time for half of the wave
    numCycles = int(length * frequency)  #the number of waves to produce is the duration times the frequency
    
    for i in range(numCycles):      #start a loop from 0 to the variable "cycles" calculated above
        GPIO.output(buzzer, True)    #set pin 27 to high
        time.sleep(delayValue)      #wait with pin 27 high
        GPIO.output(buzzer, False)      #set pin 27 to low
        time.sleep(delayValue)      #wait with pin 27 low

def destroy():
    GPIO.cleanup()              # Release resource
    

def play(melody,tempo,pause,pace=0.800):
    
    for i in range(0, len(melody)):     # Play song
        
        noteDuration = pace/tempo[i]
        buzz(melody[i],noteDuration)    # Change the frequency along the song note
        
        pauseBetweenNotes = noteDuration * pause
        time.sleep(pauseBetweenNotes)
        
def trigger():
    global buttonClicked
    GPIO.add_event_detect(10,GPIO.RISING,callback=button_callback) # Setup event on pin 10 rising edge
    while True:
        result = getdistance()
        print("distance: ",result,"cm")
        print(buttonClicked)
        if (buttonClicked or result<30):
            print("trigger!")
            if buttonClicked or result>=30:
                play(deck_the_halls_melody, deck_the_halls_tempo, 0.30, 0.800)
            #clientSock_server.send("triggered".encode("utf-8"))
            th = threading.Thread(target=requestInsert)
            th.start()
            th.join()
            
            buttonClicked = False
        time.sleep(3)
        

def detectSensor():
    
    while True:
        
        result=getdistance()
        print("distance: ",result,"cm")

        if result<30 and result >=3:     #4.지정한 범위 내의 물체가 들어오면 multi-thread메소드를 통해 영상스트리밍함수,메시지 전달 함수를 실행한다.
            print("distance: ",result,"cm")
            clientSock_server.send("triggered".encode("utf-8"))
            #th = threading.Thread(target=requestInsert)
            #th.start()
            #th.join()
            
            time.sleep(10)
th = threading.Thread(target=trigger)
th.start()
#th2 = threading.Thread(target=detectSensor)
#th2.start()

while True:
    # 서버가 클라이언트의 접속을 허용하도록_최대 4명까지
    serverSock.listen(4)

    # accept 함수에서 대기하다가 클라이언트가 접속하면 새로운 소켓을 리턴
    (clientSock, (ip, port)) = serverSock.accept()
    newthread = ClientThread(ip, port)
    newthread.start()
    threads.append(newthread)
    #print("\n클라이언트 수: "+str(len(threads)))


#msg = input("Press Enter to Quit")

GPIO.cleanup()
clientSock_server.close()
