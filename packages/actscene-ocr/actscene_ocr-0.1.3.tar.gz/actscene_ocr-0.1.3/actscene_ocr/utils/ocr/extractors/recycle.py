from typing import Dict
import numpy as np
import re

from .generic import find_keyword_with_flexible_matching


def extract_values_recycle(ocr_results) -> Dict[str, dict]:
    if not ocr_results:
        return {}
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
                text_items.append(
                    {
                        "text": text,
                        "y": center_y,
                        "x": center_x,
                        "confidence": float(conf),
                        "box": box_array.tolist(),
                        "index": i,
                    }
                )
        except Exception:
            continue
    if not text_items:
        return {}

    def _find_best_match(items, keyword):
        best_match_item = None
        best_similarity = 0.0
        for item in items:
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

    results = {}

    amount_label_item, amount_label_sim = _find_best_match(text_items, "預託金額合計")
    amount_value = ""
    if amount_label_item and amount_label_sim > 0.3:
        same_line_items = [
            it for it in text_items if abs(it["y"] - amount_label_item["y"]) <= 18.0
        ]
        same_line_items.sort(key=lambda x: x["x"])
        label_index = -1
        for i, it in enumerate(same_line_items):
            if it["index"] == amount_label_item["index"]:
                label_index = i
                break
        if label_index >= 0 and label_index + 1 < len(same_line_items):
            right_items = same_line_items[label_index + 1 :]

            currency_pattern = re.compile(r"^[￥¥]?[0-9]{1,3}(?:,[0-9]{3})*(?:円)?$")

            for item in reversed(right_items):
                t = item["text"].replace(" ", "")
                if currency_pattern.match(t):
                    amount_value = item["text"]
                    break
            else:
                amount_value = "".join([item["text"] for item in right_items])

    results["預託金額合計"] = {
        "value": amount_value,
        "y_position": float(amount_label_item["y"]) if amount_label_item else 0.0,
        "similarity": amount_label_sim,
    }

    chassis_label_item, chassis_label_sim = _find_best_match(text_items, "車台番号")
    chassis_value = ""
    if chassis_label_item and chassis_label_sim > 0.3:
        same_line_items = [
            it for it in text_items if abs(it["y"] - chassis_label_item["y"]) <= 18.0
        ]
        same_line_items.sort(key=lambda x: x["x"])
        label_index = -1
        for i, it in enumerate(same_line_items):
            if it["index"] == chassis_label_item["index"]:
                label_index = i
                break
        if label_index >= 0 and label_index + 1 < len(same_line_items):
            right_items = same_line_items[label_index + 1 :]

            combined_parts = []
            for item in right_items:
                raw = item["text"]
                normalized = (
                    raw.replace("―", "-")
                    .replace("ー", "-")
                    .replace("－", "-")
                    .replace("–", "-")
                    .replace("—", "-")
                    .replace(" ", "")
                )

                if not all(c.isalnum() or c == "-" for c in normalized):
                    break
                combined_parts.append(normalized)
            chassis_value = "".join(combined_parts)

    results["車台番号"] = {
        "value": chassis_value,
        "y_position": float(chassis_label_item["y"]) if chassis_label_item else 0.0,
        "similarity": chassis_label_sim,
    }

    return results
