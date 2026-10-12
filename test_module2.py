import json
import sys
from pipeline import process_document

doc_type = sys.argv[2] if len(sys.argv) > 2 else None
result = process_document(sys.argv[1], doc_type=doc_type, debug_dir="debug")
print(json.dumps(result, ensure_ascii=False, indent=2))