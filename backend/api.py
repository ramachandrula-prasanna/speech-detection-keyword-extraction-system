from flask import Flask, request, jsonify, Response
import whisper
import os
import cv2
import numpy as np
import sounddevice as sd

app = Flask(__name__)
model = whisper.load_model("base")

# 🔥 CHANGE THIS if camera index different
CAM_INDEX = 0  

# ---------- KEYWORDS ----------
def extract_keywords(text):
    fillers = ["um","uh","hmm","like","you","know","ok","okay"]

    words = text.lower().split()
    clean = []

    for w in words:
        w = w.strip(".,!?")
        if w not in fillers and len(w) > 2 and w not in clean:
            clean.append(w)

    return clean[:10]

# ---------- CAMERA INIT ----------
camera = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
print("Camera opened:", camera.isOpened())

# ---------- SINGLE FRAME ROUTE ----------
@app.route('/frame')
def frame():
    global camera

    success, frame = camera.read()

    if not success:
        return "No frame", 500

    # 🔥 FIXED ALIGNMENT
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (640, 480))

    ret, buffer = cv2.imencode(
        '.jpg',
        frame,
        [int(cv2.IMWRITE_JPEG_QUALITY), 70]
    )

    frame_bytes = buffer.tobytes()

    return Response(frame_bytes, mimetype='image/jpeg')
# ---------- MIC ----------
def listen_live():
    try:
        duration = 3
        samplerate = 16000

        print("🎤 Listening...")

        audio = sd.rec(
    int(duration * samplerate),
    samplerate=samplerate,
    channels=1,
    dtype='float32'
)
        sd.wait()

        audio = np.squeeze(audio)

        result = model.transcribe(audio)
        text = result["text"].strip()

        print("Text:", text)
        return text

    except Exception as e:
        print("Mic error:", e)
        return ""

# ---------- LIVE ----------
@app.route('/live', methods=['GET'])
def live():
    text = listen_live()

    if not text:
        return jsonify({"keywords": ["No speech detected"]})

    keywords = extract_keywords(text)

    return jsonify({"keywords": keywords})

# ---------- UPLOAD ----------
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files['file']
    filename = "temp.mp4"
    file.save(filename)

    try:
        result = model.transcribe(filename)
        text = result["text"].strip()

        if not text:
            return jsonify({"keywords": ["No speech detected"]})

        keywords = extract_keywords(text)

        return jsonify({"keywords": keywords})

    except Exception as e:
        print(e)
        return jsonify({"keywords": ["No speech detected"]})

    finally:
        if os.path.exists(filename):
            os.remove(filename)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)