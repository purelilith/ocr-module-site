import json
import os
import sys

import ocr_engine
from pipeline import process_document

base = sys.argv[1]
ids = sys.argv[2:]

with open(os.path.join(base, "documents.json"), encoding="utf-8") as f:
    documents = {d["document_id"]: d for d in json.load(f)}
with open(os.path.join(base, "reference_results.json"), encoding="utf-8") as f:
    reference = {d["document_id"]: d for d in json.load(f)["documents"]}

TRIALS = {
    "как сейчас": {"min_size": 5},
    "min_size=1": {"min_size": 1},
    "мельче порог": {"min_size": 1, "text_threshold": 0.5, "low_text": 0.3},
    "увеличение x2": {"min_size": 1, "mag_ratio": 2},
    "увеличение x2 + мельче порог": {"min_size": 1, "mag_ratio": 2,
                                    "text_threshold": 0.5, "low_text": 0.3},
}


def norm(value):
    return str(value).casefold().replace("ё", "е")


for name, options in TRIALS.items():
    ocr_engine.OCR_OPTIONS = options
    good = 0
    total = 0
    wrong = []
    for doc_id in ids:
        item = documents[doc_id]
        result = process_document(
            os.path.join(base, item["image"]),
            doc_type=item["document_type"],
            document_id=doc_id,
        )
        for key, expected in reference[doc_id]["fields"].items():
            if isinstance(expected, bool):
                continue
            total += 1
            if norm(result["fields"][key]) == norm(expected):
                good += 1
            else:
                wrong.append(doc_id + ":" + key)
    print(name, "-", good, "из", total, "верно; ошибки:", wrong)