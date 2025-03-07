import os
import cv2
import numpy as np
from PIL import Image

def create_trainer():
    print("Training face recognizer...")
    
    # Path to the directory with face images
    training_path = os.path.join('backend', 'auth', 'trainer')
    
    # Check if directory exists
    if not os.path.exists(training_path):
        os.makedirs(training_path)
        print(f"Created training directory at {training_path}")
        print("Please add training images to this directory and run this script again.")
        return
    
    # Check for training images
    image_files = [f for f in os.listdir(training_path) if f.endswith('.jpg') or f.endswith('.png')]
    if not image_files:
        print("No training images found. Please add images to the training_data directory.")
        print("Images should be named like: user.1.jpg, user.2.jpg, etc.")
        return
    
    # Create face detector
    detector = cv2.CascadeClassifier(os.path.join('backend', 'auth', 'haarcascade_frontalface_default.xml'))
    
    # Create lists for face samples and IDs
    faces = []
    ids = []
    
    # Process each image
    for image_file in image_files:
        # Get the ID from filename (assuming format: user.ID.jpg)
        try:
            id = int(os.path.split(image_file)[0].split(".")[1])
        except:
            print(f"Skipping {image_file} - could not parse ID from filename")
            continue
            
        path = os.path.join(training_path, image_file)
        pil_img = Image.open(path).convert('L')  # convert to grayscale
        img_numpy = np.array(pil_img, 'uint8')
        
        face = detector.detectMultiScale(img_numpy)
        
        for (x, y, w, h) in face:
            faces.append(img_numpy[y:y+h, x:x+w])
            ids.append(id)
            
    # Check if faces were detected
    if not faces:
        print("No faces detected in training images. Please check your images.")
        return
            
    # Create and train LBPH Face Recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(ids))
    
    # Save the trained model
    trainer_dir = os.path.join('backend', 'auth', 'trainer')
    if not os.path.exists(trainer_dir):
        os.makedirs(trainer_dir)
        
    trainer_path = os.path.join(trainer_dir, 'trainer.yml')
    recognizer.write(trainer_path)
    
    print(f"Training complete! Model saved to {trainer_path}")
    print(f"{len(faces)} faces trained from {len(set(ids))} people")

if __name__ == "__main__":
    create_trainer()