import cv2
import os
import time

# Try multiple camera backends
cam = None
backends = [cv2.CAP_ANY, cv2.CAP_V4L, cv2.CAP_V4L2]

for backend in backends:
    try:
        print(f"Trying camera with backend {backend}")
        cam = cv2.VideoCapture(0, backend)
        if cam.isOpened():
            print(f"Camera opened successfully with backend {backend}")
            break
    except Exception as e:
        print(f"Failed with backend {backend}: {e}")

# Fallback to default
if cam is None or not cam.isOpened():
    cam = cv2.VideoCapture(0)
    
# Final check
if not cam.isOpened():
    print("Error: Could not open camera with any backend")
    exit()
    
cam.set(3, 640) # set video FrameWidth
cam.set(4, 480) # set video FrameHeight

# Use os.path for cross-platform compatibility
cascade_path = os.path.join('backend', 'auth', 'haarcascade_frontalface_default.xml')

# Check if cascade file exists
if not os.path.exists(cascade_path):
    print(f"Error: Cascade file not found at {cascade_path}")
    print(f"Current working directory: {os.getcwd()}")
    exit()

detector = cv2.CascadeClassifier(cascade_path)
#Haar Cascade classifier is an effective object detection approach

face_id = input("Enter a Numeric user ID here:  ")
#Use integer ID for every new face (0,1,2,3,4,5,6,7,8,9........)

# Ensure samples directory exists
samples_dir = os.path.join('backend', 'auth', 'samples')
if not os.path.exists(samples_dir):
    os.makedirs(samples_dir)
    print(f"Created samples directory at {samples_dir}")

print("Taking samples, look at camera ....... ")
count = 0 # Initializing sampling face count

while True:
    ret, img = cam.read() #read the frames using the above created object
    
    if not ret:
        print("Failed to capture image. Retrying...")
        time.sleep(0.5)
        continue
        
    try:
        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #The function converts an input image from one color space to another
        faces = detector.detectMultiScale(converted_image, 1.3, 5)

        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2) #used to draw a rectangle on any image
            count += 1
            
            # Use os.path.join for the file path with forward slashes
            sample_file = os.path.join(samples_dir, f"face.{face_id}.{count}.jpg")
            cv2.imwrite(sample_file, converted_image[y:y+h,x:x+w])
            # To capture & Save images into the datasets folder
            
            print(f"Saved sample {count}/100: {sample_file}")

            cv2.imshow('image', img) #Used to display an image in a window

        k = cv2.waitKey(100) & 0xff # Waits for a pressed key
        if k == 27: # Press 'ESC' to stop
            break
        elif count >= 100: # Take 100 samples
             break
    except Exception as e:
        print(f"Error processing frame: {e}")
        # Continue to the next frame

print("Samples taken now closing the program....")
cam.release()
cv2.destroyAllWindows()