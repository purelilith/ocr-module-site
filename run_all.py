import json
import os
import sys
import traceback

import ocr_engine
from doc_types import DOC_TYPES, NOT_FOUND
from extract import validate
from pipeline import process_document, for_module3

base = sys.argv[1]
source = sys.argv[2] if len(sys.argv) > 2 else "image"
profile = sys.argv[3] if len(sys.argv) > 3 else "fast"
ocr_engine.OCR_OPTIONS = ocr_engine.PROFILES[profile]

if os.path.exists("errors.txt"):
    os.remove("errors.txt")


def load(name):
    with open(os.path.join(base, name), encoding="utf-8") as f:
        return json.load(f)


documents = load("documents.json")
questions = load("questions.json")

results = []
for item in documents:
    document_id = item["document_id"]
    doc_type = item["document_type"]
    try:
        doc = process_document(
            os.path.join(base, item[source]),
            doc_type=doc_type,
            document_id=document_id,
            debug_dir="debug",
        )
    except Exception:
        print("ОШИБКА", document_id, "(подробности в errors.txt)")
        with open("errors.txt", "a", encoding="utf-8") as f:
            f.write(document_id + "\n" + traceback.format_exc() + "\n")
        fields = {
            key: (False if cfg["kind"] == "mark" else NOT_FOUND)
            for key, cfg in DOC_TYPES[doc_type]["fields"].items()
        }
        doc = {
            "document_id": document_id,
            "document_type": doc_type,
            "fields": fields,
            "validation": validate(doc_type, fields),
            "answers": [],
        }

    doc["answers"] = [
        {"question_id": q["question_id"], "answerable": False, "value": None,
         "answer": "Ответ даст модуль 3.", "sources": []}
        for q in questions if q["document_id"] == document_id
    ]
    results.append(doc)
    print("готово:", document_id)

with open("results.json", "w", encoding="utf-8") as f:
    json.dump({"version": "1.0", "documents": results}, f, ensure_ascii=False, indent=2)

with open("ocr_output.json", "w", encoding="utf-8") as f:
    json.dump([for_module3(d) for d in results], f, ensure_ascii=False, indent=2)