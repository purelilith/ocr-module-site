import os

import easyocr
import numpy as np
import pymupdf
from PIL import Image
from scipy import ndimage

reader = easyocr.Reader(["ru", "en"], gpu=False)

OCR_OPTIONS = {"min_size": 5}
SHRINK_PAGE = True
USE_PDF_TEXT_LAYER = True


def prepare_image(image):
    pixels = np.asarray(image.convert("RGB")).copy()
    if not SHRINK_PAGE:
        return pixels

    blue = (pixels[..., 2].astype(int) - pixels[..., 0].astype(int) > 20) & (pixels[..., 2] > 90)
    pixels[ndimage.binary_dilation(blue, iterations=2)] = 255

    ink_rows = (pixels.min(axis=2) < 200).any(axis=1)
    keep = ndimage.binary_dilation(ink_rows, structure=np.ones(40))
    if not keep.any():
        return pixels
    return pixels[keep]


def _read_lines(image):
    results = reader.readtext(image, **OCR_OPTIONS)
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
        with pymupdf.open(file_path) as pdf:
            if USE_PDF_TEXT_LAYER:
                text = "\n".join(page.get_text() for page in pdf)
                if len(text.strip()) > 50:
                    return text
            pages = []
            for page in pdf:
                pix = page.get_pixmap(dpi=150)
                image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                pages.append(_read_lines(prepare_image(image)))
        return "\n".join(pages)
    return _read_lines(prepare_image(Image.open(file_path)))