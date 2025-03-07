from sys import flags
import time
import cv2
import os

def AuthenticateFace():
    try:
        flag = ""
        # Check if face module is available
        if not hasattr(cv2, 'face'):
            print("Error: OpenCV face module not found")
            print("Please install opencv-contrib-python package")
            return 0

        # Local Binary Patterns Histograms
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        # Use os.path for cross-platform compatibility
        trainer_path = os.path.join('backend', 'auth', 'trainer', 'trainer.yml')
        cascade_path = os.path.join('backend', 'auth', 'haarcascade_frontalface_default.xml')

        # Check if files exist
        if not os.path.exists(trainer_path):
            print(f"Error: Trainer file not found at {trainer_path}")
            print(f"Current working directory: {os.getcwd()}")
            return 0

        if not os.path.exists(cascade_path):
            print(f"Error: Cascade file not found at {cascade_path}")
            print(f"Current working directory: {os.getcwd()}")
            return 0

        recognizer.read(trainer_path)  # load trained model
        faceCascade = cv2.CascadeClassifier(cascade_path)

        font = cv2.FONT_HERSHEY_SIMPLEX  # denotes the font type

        id = 2  # number of persons you want to Recognize
        names = ['','', 'Lusan']  # names, leave first empty bcz counter starts from 0

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
            return 0
            
        cam.set(3, 640)  # set video FrameWidth
        cam.set(4, 480)  # set video FrameHeight

        # Define min window size to be recognized as a face
        minW = 0.1*cam.get(3)
        minH = 0.1*cam.get(4)

        # Add a counter for initial frames that might be invalid
        frame_count = 0
        max_init_frames = 10  # Increased to give more chances

        while True:
            ret, img = cam.read()  # read the frames
            
            if not ret or img is None:
                frame_count += 1
                print(f"Failed to capture image from camera (attempt {frame_count})")
                if frame_count > max_init_frames:
                    print("Maximum attempts reached. Aborting face recognition.")
                    break
                time.sleep(1)  # Wait longer before retrying
                continue
                
            try:
                # Convert to grayscale
                converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                faces = faceCascade.detectMultiScale(
                    converted_image,
                    scaleFactor=1.2,
                    minNeighbors=5,
                    minSize=(int(minW), int(minH)),
                )

                for(x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    id, accuracy = recognizer.predict(converted_image[y:y+h, x:x+w])

                    if (accuracy < 100):
                        id = names[id]
                        accuracy = "  {0}%".format(round(100 - accuracy))
                        flag = 1
                    else:
                        id = "unknown"
                        accuracy = "  {0}%".format(round(100 - accuracy))
                        flag = 0

                    cv2.putText(img, str(id), (x+5, y-5), font, 1, (255, 255, 255), 2)
                    cv2.putText(img, str(accuracy), (x+5, y+h-5), font, 1, (255, 255, 0), 1)

                cv2.imshow('camera', img)

                k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
                if k == 27:
                    break
                if flag == 1:
                    break

            except Exception as e:
                print(f"Error during face detection: {e}")
                break

        # Do a bit of cleanup
        cam.release()
        cv2.destroyAllWindows()
        return flag
    
    except Exception as e:
        print(f"Authentication error: {e}")
        return 0
