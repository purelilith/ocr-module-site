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

TRIALS = [
    ("1 дёшево: сжатие листа", True, {"min_size": 5}),
    ("2 сжатие + мелкие кусочки", True, {"min_size": 1}),
    ("3 сжатие + увеличение x1.5", True, {"min_size": 1, "mag_ratio": 1.5}),
    ("4 дорого: без сжатия, увеличение x2", False, {"min_size": 1, "mag_ratio": 2}),
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
                wrong.append(doc_id + ":" + key)
    seconds = (time.time() - started) / len(ids)
    print(name, "-", good, "из", total, "верно;", round(seconds, 1), "сек на документ; ошибки:", wrong)