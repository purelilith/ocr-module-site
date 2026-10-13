import json
import os
import sys
import ocr_engine
from pipeline import process_document

base = sys.argv[1]

source = sys.argv[2] if len(sys.argv) > 2 else "image"
profile = sys.argv[3] if len(sys.argv) > 3 else "fast"
ocr_engine.OCR_OPTIONS = ocr_engine.PROFILES[profile]


def load(name):
    with open(os.path.join(base, name), encoding="utf-8") as f:
        return json.load(f)


documents = load("documents.json")
questions = load("questions.json")

results = []
for item in documents:
    document_id = item["document_id"]
    try:
        doc = process_document(
            os.path.join(base, item[source]),
            doc_type=item["document_type"],
            document_id=document_id,
            debug_dir="debug",
        )
    except Exception as error:
        print("ОШИБКА", document_id, error)
        continue

    doc["answers"] = [
        {"question_id": q["question_id"], "answerable": False, "value": None,
         "answer": "Ответ даст модуль 3.", "sources": []}
        for q in questions if q["document_id"] == document_id
    ]
    results.append(doc)
    print("готово:", document_id)

with open("results.json", "w", encoding="utf-8") as f:
    json.dump({"version": "1.0", "documents": results}, f, ensure_ascii=False, indent=2)

ocr_output = [
    {"document_id": d["document_id"], "document_type": d["document_type"], "fields": d["fields"]}
    for d in results
]
with open("ocr_output.json", "w", encoding="utf-8") as f:
    json.dump(ocr_output, f, ensure_ascii=False, indent=2)