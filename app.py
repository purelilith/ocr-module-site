import os
import uuid

from flask import Flask, render_template, request, jsonify

from pipeline import process_document

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

UPLOAD_DIR = "uploads"
ALLOWED = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".pdf"}
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("photo")
    if file is None or file.filename == "":
        return jsonify({"error": "Файл не выбран"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED:
        return jsonify({"error": "Нужна картинка или PDF"}), 400

    path = os.path.join(UPLOAD_DIR, uuid.uuid4().hex + ext)
    file.save(path)

    try:
        result = process_document(path, document_id=file.filename)
    except ValueError as error:
        return jsonify({"error": str(error)}), 422
    except Exception:
        return jsonify({"error": "Не получилось распознать документ"}), 500
    finally:
        os.remove(path)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)