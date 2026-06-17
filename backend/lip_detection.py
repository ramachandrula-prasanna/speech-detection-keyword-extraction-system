import cv2
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh

LIP_INDICES = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291]

cap = cv2.VideoCapture(0)

features = []
predictions = []

with mp_face_mesh.FaceMesh(static_image_mode=False) as face_mesh:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb)

        if result.multi_face_landmarks:
            for face_landmarks in result.multi_face_landmarks:
                lip_points = []

                for idx in LIP_INDICES:
                    lm = face_landmarks.landmark[idx]
                    lip_points.append([lm.x, lm.y])

                features.append(np.array(lip_points).flatten())

        # Process last 5 frames
        if len(features) > 5:
            features_np = np.array(features[-5:])
            diff = np.diff(features_np, axis=0)

            movement = np.mean(np.abs(diff))

            print("Movement:", movement)

            # 🔥 SIMPLE THRESHOLD (tune if needed)
            if movement > 0.002:
                pred = 1
            else:
                pred = 0

            # 🔥 SMOOTHING
            predictions.append(pred)

            if len(predictions) > 10:
                predictions.pop(0)

            final = 1 if sum(predictions) > 6 else 0

            text = "Speech" if final == 1 else "No Speech"

            cv2.putText(frame, text, (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)

        cv2.imshow("Lip Detection Test", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()