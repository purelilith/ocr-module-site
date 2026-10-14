import os
import uuid
from flask import Flask, render_template, request, jsonify

from pipeline import process_document
from dean_rag import DeanRAG  # Импортируем Модуль 3

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

UPLOAD_DIR = "uploads"
ALLOWED = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".pdf"}
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Инициализируем RAG-модуль один раз при старте сервера[span_6](start_span)[span_6](end_span)[span_7](start_span)[span_7](end_span)
rag = DeanRAG()

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
        # Шаг 1 (Модуль 2): Распознавание и парсинг полей в JSON-карточку
        doc_result = process_document(path, document_id=file.filename)
        
        # Шаг 2 (Модуль 3): Валидация и проверка комплектности по Положению
        # Получаем стандартную проверку комплектности (эквивалент вопросов о комплектности)
        validation_info = rag.validation_record(doc_result)
        doc_result["validation"] = validation_info

        # Если пользователь передал текстовый вопрос (например, через дополнительное поле на сайте),
        # мы можем обработать его через Модуль 3:
        question = request.form.get("question", "").strip()
        if question:
            answer_record, trace = rag.answer_with_trace(doc_result, question, "web-Q1")
            doc_result["answers"] = [answer_record]
        else:
            # Или генерируем стандартные ответы для всех привязанных вопросов (если требуется)
            doc_result["answers"] = []

    except ValueError as error:
        return jsonify({"error": str(error)}), 422
    except Exception as e:
        return jsonify({"error": "Не получилось распознать документ: " + str(e)}), 500
    finally:
        if os.path.exists(path):
            os.remove(path)

    return jsonify(doc_result)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)