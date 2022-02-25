from gpiozero import MotionSensor,LED
from picamera import PiCamera
from time import sleep
from signal import pause
import boto3
import smtplib
import os

pir = MotionSensor(24)
blue = LED(22)
blue.on()
camera = PiCamera()

def PlateRecognition():
    access_key_id = 'AKIARD2ZDU2CVNGZU***'
    secret_access_key = 'A26yFHfvehxm08SPkZI42xPFoxXbfYE25wev****'

    photo = ('/home/pi/Desktop/work/plateNum1.jpg')
    client = boto3.client('rekognition', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key,region_name='us-west-2')

    with open (photo, 'rb') as source_image:
        source_bytes = source_image.read()       
        response = client.detect_text(Image ={'Bytes': source_bytes})

    textDetections=response['TextDetections']
    z=0
    x=""
    for text in textDetections:
        y = (" " + text['DetectedText'])
        x += y
        z += 1
        if z == 2:
            break
    l = x.split()
    k = []
    for i in l:
        if (x.count(i)>1 and (i not in k)or x.count(i)==1):
            k.append(i)
    PlateNumber = (' '.join(k))
    print("License Plate Detected is: " + PlateNumber)
    if PlateNumber == "2935 CZ 15":
        os.system('echo "Welcome home MR AYAAZ, your gate is now opening." |festival --tts')
        print("Gate Opening...!")
        blue.off()
        sleep(5)
        os.system('echo "Attention! gate is now closing." |festival --tts')
        blue.on()
        print("Gate Closed...!")
    elif len(PlateNumber) < 1:
        print("No plate number detected...!")
    else:
        os.system('echo "Am sorry, your plate number does not match, please contact MR AYAAZ for access." |festival --tts')
        smtpUser = 'raspberrypi7786@gmail.com'
        smtpPass = '8209257**'
        toAdd = 'ayazrom14@gmail.com'
        fromAdd = smtpUser
        subject = 'IMPORTANT MESSAGE FROM RASPBERRYPI4'
        header = 'To:' + toAdd + '\n' + 'From:' + fromAdd + '\n' + 'Subject:' + subject
        body = ('UNRECOGNISED VEHICLE DETECTED AT GATE: '+ PlateNumber)
        print (header + '\n' + body)
        s = smtplib.SMTP('smtp.gmail.com',587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(smtpUser,smtpPass)
        print("Login Successfull")
        s.sendmail(fromAdd,toAdd,header + '\n\n' + body)
        s.quit()

def take_photo():
    os.system('echo "Hello, please wait while i take a photo of your license plate." |festival --tts')
    camera.start_preview()
    sleep(3)
    camera.capture('/home/pi/Desktop/work/plateNum1.jpg')
    camera.stop_preview()
    PlateRecognition()
    sleep(5)
#function that runs when motion is detected!
pir.when_motion = take_photo
pause()
