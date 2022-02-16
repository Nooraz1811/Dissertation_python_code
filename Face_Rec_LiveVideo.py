from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import RPi.GPIO as GPIO

RELAY = 16
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY, GPIO.OUT)
GPIO.output(RELAY,GPIO.LOW)

#Initialize 'currentname' to trigger only when a new person is identified.
currentname = "unknown"
encodingsP = "/home/pi/Desktop/work/encodings.pickle"
cascade = "/home/pi/Desktop/work/haarcascade_frontalface_default.xml"
# cascade for face detection
data = pickle.loads(open(encodingsP, "rb").read())
detector = cv2.CascadeClassifier(cascade)

print("Starting live video stream …")
#vs = VideoStream(src=0).start()
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# start the FPS counter
fps = FPS().start()

prevTime = 0
doorUnlock = False

# loop over frames from the video file stream
while True:
	frame = vs.read()
	frame = imutils.resize(frame, width=600)

	# convert the input frame from (1) BGR to grayscale (for face
	# detection) and (2) from BGR to RGB (for face recognition)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

	# detect faces in the grayscale frame
	rects = detector.detectMultiScale(gray, scaleFactor=1.1,minNeighbors=5, minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)

	boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

	# compute the facial embeddings for each face bounding box
	encodings = face_recognition.face_encodings(rgb, boxes)
	names = []

	# loop over the facial embeddings
	for encoding in encodings:
		matches = face_recognition.compare_faces(data["encodings"],encoding)
		name = "Unknown" #if face is not recognized, then print Unknown
		# check to see if we have found a match
		if True in matches:
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}
			# to unlock the door
			GPIO.output(RELAY,GPIO.HIGH)
			prevTime = time.time()
			doorUnlock = True
			print("Door unlock")
			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1
				
			name = max(counts, key=counts.get)
			#If someone in your dataset is identified, print their name on the screen
			if currentname != name:
				currentname = name
				print(currentname)
		# update the list of names
		names.append(name)

        
        #lock the door after 5 seconds
	if doorUnlock == True and time.time() - prevTime > 5:
		doorUnlock = False
		GPIO.output(RELAY,GPIO.LOW)
		print("Door lock")
	
	# loop over the recognized faces
	for ((top, right, bottom, left), name) in zip(boxes, names):
		# draw the predicted face name on the image – color is in BGR
		cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2)
		y = top - 15 if top - 15 > 15 else top + 15
		cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,.8, (255, 0, 255), 2)
		
	# display the image to our screen
	cv2.imshow("Facial Recognition is Running", frame)
	
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break
	# update the FPS counter
	fps.update()
fps.stop()
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()