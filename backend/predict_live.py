import cv2
import mediapipe as mp
import numpy as np
import joblib

mp_face_mesh = mp.solutions.face_mesh

model = joblib.load("model.pkl")

LIP_INDICES = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291]

cap = cv2.VideoCapture(0)

predictions = []
features = []

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
                    landmark = face_landmarks.landmark[idx]
                    lip_points.append([landmark.x, landmark.y])

                features.append(np.array(lip_points).flatten())

        if len(features) > 5:
            features_np = np.array(features[-5:])

            diff = np.diff(features_np, axis=0)

            final_feature = np.concatenate([
                np.mean(features_np, axis=0),
                np.mean(diff, axis=0)
            ])

            prediction = model.predict([final_feature])[0]
            proba = model.predict_proba([final_feature])[0]
            confidence = max(proba)

            lip_size = np.mean(np.abs(features_np))
            movement = np.mean(np.abs(diff)) / (lip_size + 1e-6)

            if prediction == 1 and confidence > 0.5 and movement > 0.0015:
                pred = 1
            elif movement > 0.003:
                pred = 1
            else:
                pred = 0

            predictions.append(pred)

            if len(predictions) > 15:
                predictions.pop(0)

            final = round(sum(predictions) / len(predictions))

            text = "Speech" if final == 1 else "No Speech"

            cv2.putText(frame, text, (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)

        cv2.imshow("Lip Reader", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()