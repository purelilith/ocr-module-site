import json
import sys
from pipeline import process_document

result = process_document(sys.argv[1])
print(json.dumps(result, ensure_ascii=False, indent=2))