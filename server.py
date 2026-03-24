import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from process_video import process_video
from evaluate_model import evaluate_model

app = Flask(__name__)

@app.route('/')
def hello():
    return 'LSP Translate'


@app.route('/upload_video', methods=['POST'])
def upload_video():
    tmp_file = None  # Para poder eliminarlo incluso si falla algo

    try:
        if 'video' not in request.files:
            return jsonify({"error": "No video provided"}), 400

        video_file = request.files['video']

        if video_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        file_name = secure_filename(video_file.filename)

        root_path = os.path.dirname(os.path.abspath(__file__))
        tmp_dir = os.path.join(root_path, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        tmp_file = os.path.join(tmp_dir, file_name)
        video_file.save(tmp_file)

        # Procesamiento
        video_processed = process_video(tmp_file)
        resp = evaluate_model(video_processed)

        resp = [r.upper() for r in resp][::-1]
        final_text = " ".join(resp)

        print(f"Final translation: {final_text}")

        return jsonify({"translation": final_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if tmp_file and os.path.exists(tmp_file):
            os.remove(tmp_file)


# Para Railway
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)