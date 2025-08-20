from typing import Dict
import numpy as np

from .generic import find_keyword_with_flexible_matching


def _compute_box_bounds(box_like):
    box_array = np.array(box_like, dtype=float)
    xs = box_array[:, 0]
    ys = box_array[:, 1]
    return float(xs.min()), float(xs.max()), float(ys.min()), float(ys.max())


def _build_text_items(ocr_results):
    texts = ocr_results[0].get("rec_texts", [])
    boxes = ocr_results[0].get("rec_polys", [])
    confidences = ocr_results[0].get("rec_scores", [])

    text_items = []
    for i, (text, box, conf) in enumerate(zip(texts, boxes, confidences)):
        try:
            if isinstance(box, (list, np.ndarray)):
                box_array = np.array(box)
                center_y = float(np.mean(box_array[:, 1]))
                center_x = float(np.mean(box_array[:, 0]))
                min_x, max_x, min_y, max_y = _compute_box_bounds(box_array)
                text_items.append(
                    {
                        "text": text,
                        "y": center_y,
                        "x": center_x,
                        "confidence": float(conf),
                        "box": box_array.tolist(),
                        "min_x": min_x,
                        "max_x": max_x,
                        "min_y": min_y,
                        "max_y": max_y,
                        "index": i,
                    }
                )
        except Exception:
            continue
    return text_items


def _find_best_match(text_items, keyword):
    best_match_item = None
    best_similarity = 0.0
    for item in text_items:
        similarity = find_keyword_with_flexible_matching([item], keyword)[1]
        if similarity > best_similarity:
            best_similarity = similarity
            best_match_item = item
    return best_match_item, float(best_similarity)


def _group_by_rows(items, y_tol=18.0):
    if not items:
        return []
    items_sorted = sorted(items, key=lambda it: (it["y"], it["x"]))
    rows = []
    current_row = []
    current_y = None
    for it in items_sorted:
        if current_y is None or abs(it["y"] - current_y) <= y_tol:
            current_row.append(it)
            current_y = it["y"] if current_y is None else current_y
        else:
            rows.append(sorted(current_row, key=lambda r: r["x"]))
            current_row = [it]
            current_y = it["y"]
    if current_row:
        rows.append(sorted(current_row, key=lambda r: r["x"]))
    return rows


def extract_values_jouto(ocr_results) -> Dict[str, dict]:
    if not ocr_results:
        return {}

    text_items = _build_text_items(ocr_results)
    if not text_items:
        return {}

    results = {}

    label_text = "譲渡人及び譲受人の氏名又は名称及び住所"
    label_item, label_sim = _find_best_match(text_items, label_text)

    value_text = ""
    if label_item and label_sim > 0.3:
        lx0, lx1 = label_item["min_x"], label_item["max_x"]
        ly1 = label_item["max_y"]
        candidates = [
            it
            for it in text_items
            if it["y"] > ly1 and not (it["max_x"] < lx0 or it["min_x"] > lx1)
        ]
        row_groups = _group_by_rows(candidates)
        if row_groups:
            first_row_tokens = [it["text"] for it in row_groups[0]]
            pieces = ["".join(first_row_tokens)]
            if len(row_groups) >= 2:
                second_row_tokens = [it["text"] for it in row_groups[1]]
                if second_row_tokens:
                    pieces.append("".join(second_row_tokens))
            value_text = " ".join([p for p in pieces if p])

    results[label_text] = {
        "value": value_text,
        "y_position": float(label_item["y"]) if label_item else 0.0,
        "similarity": label_sim if label_item else 0.0,
        "keyword_position": 0 if label_item else -1,
    }

    return results
