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


def extract_values_jibaiseki(ocr_results) -> Dict[str, dict]:
    if not ocr_results:
        return {}

    text_items = _build_text_items(ocr_results)
    if not text_items:
        return {}

    results = {}

    anchor1_text = "自動車登録"
    anchor1_item, anchor1_sim = _find_best_match(text_items, anchor1_text)

    value_text = ""
    if anchor1_item and anchor1_sim > 0.3:
        anchor2_text = "車台番号"
        anchor2_item, anchor2_sim = _find_best_match(text_items, anchor2_text)

        if anchor2_item and anchor2_sim > 0.3:
            anchor1_x = anchor1_item["x"]
            anchor1_y = anchor1_item["y"]
            anchor1_min_y = anchor1_item["min_y"]
            anchor2_x = anchor2_item["x"]
            anchor2_y = anchor2_item["y"]
            anchor2_max_y = anchor2_item["max_y"]

            anchor2_right_x = anchor2_item["max_x"]
            anchor2_width = anchor2_right_x - anchor1_x
            search_range = anchor2_width * 5

            right_items = [
                it
                for it in text_items
                if it["x"] > anchor2_right_x
                and it["y"] >= anchor1_min_y
                and it["y"] <= anchor2_max_y
                and it["x"] <= anchor2_right_x + search_range
            ]

            if right_items:
                import re

                for item in right_items:
                    text = item["text"]

                    if re.match(r"^[A-Za-z0-9-]+$", text):
                        value_text = text
                        break

    results["車台番号"] = {
        "value": value_text,
        "y_position": float(anchor2_item["y"]) if anchor2_item else 0.0,
        "similarity": anchor2_sim if anchor2_item else 0.0,
        "keyword_position": 0 if anchor2_item else -1,
    }

    insurance_text = "保険期間"
    insurance_item, insurance_sim = _find_best_match(text_items, insurance_text)

    insurance_value_text = ""
    if insurance_item and insurance_sim > 0.3:
        insurance_x = insurance_item["x"]
        insurance_y = insurance_item["y"]
        insurance_height = insurance_item["max_y"] - insurance_item["min_y"]
        search_range_down = insurance_height * 3

        right_down_items = [
            it
            for it in text_items
            if it["x"] > insurance_x
            and it["y"] > insurance_y
            and it["y"] <= insurance_y + search_range_down
            and it["text"].startswith("至")
        ]

        if not right_down_items:
            insurance_text = "期間"
            insurance_item, insurance_sim = _find_best_match(text_items, insurance_text)

            if insurance_item and insurance_sim > 0.3:
                insurance_x = insurance_item["x"]
                insurance_y = insurance_item["y"]
                insurance_height = insurance_item["max_y"] - insurance_item["min_y"]
                search_range_down = insurance_height * 3

                right_down_items = [
                    it
                    for it in text_items
                    if it["x"] > insurance_x
                    and it["y"] > insurance_y
                    and it["y"] <= insurance_y + search_range_down
                    and it["text"].startswith("至")
                ]

        if right_down_items:
            anchor2_item = min(right_down_items, key=lambda it: (it["y"], it["x"]))
            anchor2_x = anchor2_item["x"]
            anchor2_y = anchor2_item["y"]

            right_items = [
                it
                for it in text_items
                if it["x"] >= anchor2_x and abs(it["y"] - anchor2_y) <= 50
            ]

            combined_parts = []
            for item in sorted(right_items, key=lambda it: it["x"]):
                text = item["text"]
                if "日" in text:
                    parts = text.split("日")
                    if parts[0]:
                        combined_parts.append(parts[0] + "日")
                    break
                combined_parts.append(text)

            insurance_value_text = "".join(combined_parts)

            if insurance_value_text.startswith("至"):
                insurance_value_text = insurance_value_text[1:]

    results["保険期間至"] = {
        "value": insurance_value_text,
        "y_position": float(insurance_item["y"]) if insurance_item else 0.0,
        "similarity": insurance_sim if insurance_item else 0.0,
        "keyword_position": 0 if insurance_item else -1,
    }

    return results
