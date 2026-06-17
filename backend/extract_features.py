import cv2
import mediapipe as mp
import os
import numpy as np

mp_face_mesh = mp.solutions.face_mesh

LIP_INDICES = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291]


def extract_lip_features(video_path):
    cap = cv2.VideoCapture(video_path)
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

    cap.release()

    if len(features) < 2:
        return None

    features = np.array(features)

    # Motion features
    diff = np.diff(features, axis=0)

    final_feature = np.concatenate([
        np.mean(features, axis=0),
        np.mean(diff, axis=0)
    ])

    return final_feature


def process_dataset(dataset_path):
    X = []
    y = []

    for label in ["speech", "nonspeech"]:
        folder = os.path.join(dataset_path, label)

        for file in os.listdir(folder):
            video_path = os.path.join(folder, file)

            print("Processing:", video_path)

            feat = extract_lip_features(video_path)

            if feat is not None:
                X.append(feat)
                y.append(1 if label == "speech" else 0)

    return np.array(X), np.array(y)


if __name__ == "__main__":
    X, y = process_dataset("dataset")

    np.save("X.npy", X)
    np.save("y.npy", y)

    print("Saved features ✅")
    print("Features shape:", X.shape)
    print("Labels shape:", y.shape)