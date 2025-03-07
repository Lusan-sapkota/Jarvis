import cv2
import numpy as np
from PIL import Image #pillow package
import os

# Use os.path.join for cross-platform compatibility
path = os.path.join('backend', 'auth', 'samples')
cascade_path = os.path.join('backend', 'auth', 'haarcascade_frontalface_default.xml')
trainer_output_path = os.path.join('backend', 'auth', 'trainer', 'trainer.yml')

# Check if samples directory exists, create if it doesn't
if not os.path.exists(path):
    os.makedirs(path)
    print(f"Created samples directory at {path}")
    print("Please add sample images to this directory and run this script again.")
    print("Images should be named like: user.1.jpg, user.2.jpg, etc.")
    exit()

# Check if trainer directory exists, create if it doesn't
trainer_dir = os.path.join('backend', 'auth', 'trainer')
if not os.path.exists(trainer_dir):
    os.makedirs(trainer_dir)
    print(f"Created trainer directory at {trainer_dir}")

# Check if cascade file exists
if not os.path.exists(cascade_path):
    print(f"Error: Cascade file not found at {cascade_path}")
    print(f"Current working directory: {os.getcwd()}")
    exit()

recognizer = cv2.face.LBPHFaceRecognizer_create() # Local Binary Patterns Histograms
detector = cv2.CascadeClassifier(cascade_path)
#Haar Cascade classifier is an effective object detection approach


def Images_And_Labels(path): # function to fetch the images and labels
    # Check if directory is empty
    if not os.listdir(path):
        print(f"No images found in {path}")
        print("Please add sample images and run again.")
        exit()

    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []

    for imagePath in imagePaths: # to iterate particular image path
        # Skip non-image files
        if not (imagePath.lower().endswith('.jpg') or 
                imagePath.lower().endswith('.jpeg') or 
                imagePath.lower().endswith('.png')):
            continue

        try:
            gray_img = Image.open(imagePath).convert('L') # convert it to grayscale
            img_arr = np.array(gray_img,'uint8') #creating an array

            # Extract ID from filename (user.ID.jpg)
            id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = detector.detectMultiScale(img_arr)

            if len(faces) == 0:
                print(f"No face detected in {imagePath}, skipping...")
                continue

            for (x,y,w,h) in faces:
                faceSamples.append(img_arr[y:y+h,x:x+w])
                ids.append(id)
                print(f"Face detected in {imagePath} with ID: {id}")
        except Exception as e:
            print(f"Error processing {imagePath}: {e}")

    return faceSamples,ids

print ("Training faces. It will take a few seconds. Wait ...")

faces,ids = Images_And_Labels(path)

# Check if any faces were detected
if len(faces) == 0:
    print("No faces detected in any of the sample images.")
    print("Please check your sample images and try again.")
    exit()

recognizer.train(faces, np.array(ids))

# Save the trained model
recognizer.write(trainer_output_path)

print(f"Model trained, Now we can recognize your face.")
print(f"Trained {len(faces)} face images from {len(set(ids))} different people")
print(f"Trainer saved to: {trainer_output_path}")
