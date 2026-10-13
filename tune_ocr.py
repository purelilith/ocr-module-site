import json
import os
import sys
import time

import ocr_engine
from pipeline import process_document

base = sys.argv[1]
ids = sys.argv[2:]

with open(os.path.join(base, "documents.json"), encoding="utf-8") as f:
    documents = {d["document_id"]: d for d in json.load(f)}
with open(os.path.join(base, "reference_results.json"), encoding="utf-8") as f:
    reference = {d["document_id"]: d for d in json.load(f)["documents"]}

if ids == ["all"]:
    ids = list(documents)

TRIALS = [
    ("1 порог 0.4/0.25", True, {"min_size": 5, "text_threshold": 0.4, "low_text": 0.25}),
    ("2 сосед: порог 0.35/0.2", True, {"min_size": 5, "text_threshold": 0.35, "low_text": 0.2}),
    ("3 порог 0.5/0.3 + x1.25", True, {"min_size": 5, "text_threshold": 0.5, "low_text": 0.3, "mag_ratio": 1.25}),
    ("4 точный: x1.75", True, {"min_size": 5, "mag_ratio": 1.75}),
]


def norm(value):
    return str(value).casefold().replace("ё", "е")


for name, shrink, options in TRIALS:
    ocr_engine.SHRINK_PAGE = shrink
    ocr_engine.OCR_OPTIONS = options
    started = time.time()
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
            total += 1
            if norm(result["fields"][key]) == norm(expected):
                good += 1
            else:
                wrong.append(f"{doc_id}:{key} ждали {expected!r}, получили {result['fields'][key]!r}")
    seconds = (time.time() - started) / len(ids)
    print(name, "-", good, "из", total, "верно;", round(seconds, 1), "сек на документ; ошибки:", wrong)