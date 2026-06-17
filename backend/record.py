import cv2
import os

label = input("Enter label (speech / nonspeech): ")

save_path = f"dataset/{label}"
os.makedirs(save_path, exist_ok=True)

cap = cv2.VideoCapture(0)

count = len(os.listdir(save_path))

print("Press 's' to start recording, 'e' to stop, 'q' to quit")

recording = False
frames = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Camera", frame)

    key = cv2.waitKey(1)

    if key == ord('s'):
        print("Recording...")
        recording = True
        frames = []

    elif key == ord('e'):
        print("Stopped recording")
        recording = False

        filename = f"{save_path}/video_{count}.avi"
        out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))

        for f in frames:
            out.write(f)
        out.release()

        print(f"Saved: {filename}")
        count += 1

    elif key == ord('q'):
        break

    if recording:
        frames.append(frame)

cap.release()
cv2.destroyAllWindows()