import joblib
import numpy as np
from extract_features import extract_lip_features

# Load trained model safely
try:
    model = joblib.load("model.pkl")
except:
    model = None


def predict_from_video(video_path):
    try:
        features = extract_lip_features(video_path)

        if features is None:
            print("No features extracted")
            return False

        # Convert to numpy array
        features = np.array(features)

        # 🔥 Better metrics
        variation = np.std(features)     # pattern change
        mean_val = np.mean(features)     # overall movement

        print("Variation:", variation)
        print("Mean:", mean_val)

        # 🔥 Filter out non-speech (low variation)
        if variation < 0.02:
            return False

        # 🔥 Use ML model if available
        if model is not None:
            prediction = model.predict([features])[0]
            print("Prediction:", prediction)

            return True if prediction == 1 else False

        # fallback
        return True

    except Exception as e:
        print("Lip inference error:", e)
        return False