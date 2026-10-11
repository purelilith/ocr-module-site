import os
import easyocr
import fitz  # так называется PyMuPDF при подключении

reader = easyocr.Reader(["ru", "en"], gpu=False)


def _read_lines(image):
    results = reader.readtext(image)
    items = []
    for box, text, confidence in results:
        xs = [point[0] for point in box]
        ys = [point[1] for point in box]
        items.append({
            "x": min(xs),
            "y": (min(ys) + max(ys)) / 2,
            "h": max(ys) - min(ys),
            "text": text,
        })

    items.sort(key=lambda item: item["y"])

    lines = []
    for item in items:
        if lines and abs(item["y"] - lines[-1]["y"]) < item["h"] * 0.6:
            lines[-1]["items"].append(item)
        else:
            lines.append({"y": item["y"], "items": [item]})

    result_lines = []
    for line in lines:
        ordered = sorted(line["items"], key=lambda item: item["x"])
        result_lines.append(" ".join(item["text"] for item in ordered))
    return "\n".join(result_lines)


def recognize(file_path):
    if os.path.splitext(file_path)[1].lower() == ".pdf":
        pages = []
        with fitz.open(file_path) as pdf:
            for page in pdf:
                png_bytes = page.get_pixmap(dpi=200).tobytes("png")
                pages.append(_read_lines(png_bytes))
        return "\n".join(pages)
    return _read_lines(file_path)