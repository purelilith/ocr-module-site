import json
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)

words = set()
for doc in data["documents"]:
    for key in ("student_name", "supervisor_name"):
        value = doc["fields"].get(key)
        if value and value != "не найдено":
            words.update(word.lower() for word in value.split())

with open("known_words.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(words)) + "\n")