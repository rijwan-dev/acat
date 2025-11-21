exfrom flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return send_from_directory("fake-degree", "index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "document" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["document"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    return jsonify({
        "message": "File uploaded successfully",
        "filename": filename,
        "stored_at": save_path
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
