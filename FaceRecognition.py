import face_recognition
import smtplib
import os
from picamera import PiCamera
from time import sleep
from gpiozero import MotionSensor,LED
from signal import pause

pir = MotionSensor(23)
red = LED(22)
red.on()
camera= PiCamera()
 
 
def FaceRecognition():
    ayaz_image = face_recognition.load_image_file("/home/pi/Desktop/work/Ayaz.jpg")
    unknown_image = face_recognition.load_image_file("/home/pi/Desktop/work/Face.jpg")

    try:
        ayaz_face_encoding = face_recognition.face_encodings(ayaz_image)[0]
        unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
    
    except IndexError:
        print("No face detected...Aborting process...")
        return

    known_faces = [ayaz_face_encoding]
    results = face_recognition.compare_faces(known_faces,unknown_face_encoding)

    if False in results:
        os.system('echo "Am sorry, your face does not match, please contact MR AYAAZ for access" |festival --tts')
        print("Face does not match!")
        smtpUser = 'raspberrypi7786@gmail.com'
        smtpPass = '820925***'

        toAdd = 'ayazrom14@gmail.com'
        fromAdd = smtpUser

        subject = 'IMPORTANT MAIL FROM RASPBERRYPI4'
        header = 'To:' + toAdd + '\n' + 'From:' + fromAdd + '\n' + 'Subject:' + subject
        body = 'Unrecognised face detected at front door.'
        print (header + '\n' + body)

        s = smtplib.SMTP('smtp.gmail.com',587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(smtpUser,smtpPass)
        print("Login Successfull")
        s.sendmail(fromAdd,toAdd,header + '\n\n' + body)
        s.quit()
    else:
        os.system('echo "Welcome home MR AYAAZ, your door is now open" |festival --tts')
        print("Face Recognized is: Ayaaz!")
        print("Door opened!")
        red.off()
        sleep(5)
        os.system('echo "Attention! door is now closing" |festival --tts')
        red.on()
        print("Door closed!")
def take_photo():
    os.system('echo "Hello, please look at the camera while i take a photo of your face" |festival --tts')
    camera.start_preview()
    sleep(3)
    camera.capture('/home/pi/Desktop/work/Face.jpg')
    camera.stop_preview()
    FaceRecognition()
    sleep(5)
#function that runs when motion is detected!
pir.when_motion = take_photo
pause() 
