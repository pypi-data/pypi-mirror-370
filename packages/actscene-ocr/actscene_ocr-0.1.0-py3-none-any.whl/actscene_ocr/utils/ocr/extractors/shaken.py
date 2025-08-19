from typing import Dict
import numpy as np

from .generic import (
    normalize,
    find_keyword_with_flexible_matching,
    is_vehicle_number_pattern,
    normalize_chassis_part,
    is_chassis_token,
)


def extract_values_shaken(ocr_results) -> Dict[str, dict]:
    if not ocr_results:
        return {}

    def _compute_box_bounds(box_like):
        box_array = np.array(box_like, dtype=float)
        xs = box_array[:, 0]
        ys = box_array[:, 1]
        return float(xs.min()), float(xs.max()), float(ys.min()), float(ys.max())

    def _build_text_items(ocr_results_local):
        texts = ocr_results_local[0].get("rec_texts", [])
        boxes = ocr_results_local[0].get("rec_polys", [])
        confidences = ocr_results_local[0].get("rec_scores", [])
        items = []
        for i, (text, box, conf) in enumerate(zip(texts, boxes, confidences)):
            try:
                if isinstance(box, (list, np.ndarray)):
                    box_array = np.array(box)
                    center_y = float(np.mean(box_array[:, 1]))
                    center_x = float(np.mean(box_array[:, 0]))
                    min_x, max_x, min_y, max_y = _compute_box_bounds(box_array)
                    items.append(
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
        return items

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

    def _leftdown_region_items(items, anchor_item):
        if not anchor_item:
            return []
        anchor_x = anchor_item["max_x"]
        anchor_y = anchor_item["max_y"]
        return [it for it in items if it["x"] < anchor_x and it["y"] > anchor_y]

    text_items = _build_text_items(ocr_results)
    if not text_items:
        return {}
    results = {}

    owner_label_item, owner_label_sim = _find_best_match(
        text_items, "使用者の氏名又は名称"
    )
    region_items = (
        _leftdown_region_items(text_items, owner_label_item)
        if owner_label_item and owner_label_sim > 0.3
        else []
    )
    region_rows = _group_by_rows(region_items)
    all_rows = _group_by_rows(text_items)

    owner_value_text = ""
    if region_rows:
        top_item = region_rows[0][0]
        combined_text = top_item["text"]

        for item in region_rows[0][1:]:
            y_diff = abs(item["y"] - top_item["y"])
            avg_height = (
                top_item["max_y"] - top_item["min_y"] + item["max_y"] - item["min_y"]
            ) / 2
            y_tolerance = avg_height * 0.5

            if item["x"] > top_item["x"] and y_diff <= y_tolerance:
                combined_text += item["text"]
            else:
                break

        owner_value_text = combined_text

    results["使用者の氏名又は名称"] = {
        "value": owner_value_text,
        "y_position": float(owner_label_item["y"]) if owner_label_item else 0.0,
        "similarity": owner_label_sim if owner_label_item else 0.0,
        "keyword_position": 0 if owner_label_item else -1,
    }

    def _find_vehicle_number_in_row(row_items):
        tokens_raw = [it["text"] for it in row_items]
        tokens_norm = [normalize(t) for t in tokens_raw]
        n = len(tokens_norm)
        for i in range(n):
            acc_raw = ""
            acc_norm = ""
            for j in range(i, n):
                acc_raw += tokens_raw[j]
                acc_norm += tokens_norm[j]
                if is_vehicle_number_pattern(acc_norm):
                    return acc_raw
        return ""

    vehicle_label_item, vehicle_label_sim = _find_best_match(
        text_items, "自動車登録番号又は車両番号"
    )
    vehicle_rows = (
        _group_by_rows(_leftdown_region_items(text_items, vehicle_label_item))
        if vehicle_label_item and vehicle_label_sim > 0.3
        else []
    )
    vehicle_number_value = ""
    if vehicle_rows:
        candidate = _find_vehicle_number_in_row(vehicle_rows[0])
        if candidate:
            vehicle_number_value = candidate
    if not vehicle_number_value:
        for row in all_rows:
            candidate = _find_vehicle_number_in_row(row)
            if candidate:
                vehicle_number_value = candidate
                break
    if not vehicle_number_value:
        vehicle_number_value = region_rows[0][0]["text"] if region_rows else ""
    results["自動車登録番号又は車両番号"] = {
        "value": vehicle_number_value,
        "y_position": float(vehicle_label_item["y"]) if vehicle_label_item else 0.0,
        "similarity": vehicle_label_sim if vehicle_label_item else 0.0,
        "keyword_position": 0 if vehicle_label_item else -1,
    }

    chassis_label_item, chassis_label_sim = _find_best_match(text_items, "車台番号")
    chassis_rows = (
        _group_by_rows(_leftdown_region_items(text_items, chassis_label_item))
        if chassis_label_item and chassis_label_sim > 0.3
        else []
    )

    def _join_chassis_from_row(row):
        parts = []
        for it in row:
            token = normalize_chassis_part(it["text"])
            if is_chassis_token(token):
                parts.append(token)
            else:
                if parts:
                    break
        return "".join(parts)

    chassis_value = ""
    if chassis_rows:
        candidate = _join_chassis_from_row(chassis_rows[0])
        if len(candidate) >= 6:
            chassis_value = candidate
    if not chassis_value:
        for row in all_rows:
            candidate = _join_chassis_from_row(row)
            if len(candidate) >= 10:
                chassis_value = candidate
                break
    if not chassis_value:
        chassis_value = region_rows[0][0]["text"] if region_rows else ""
    results["車台番号"] = {
        "value": chassis_value,
        "y_position": float(chassis_label_item["y"]) if chassis_label_item else 0.0,
        "similarity": chassis_label_sim if chassis_label_item else 0.0,
        "keyword_position": 0 if chassis_label_item else -1,
    }

    init_label_item, init_label_sim = _find_best_match(text_items, "初度登録年月")
    init_value = ""
    if init_label_item and init_label_sim > 0.3:
        lx0, lx1 = init_label_item["min_x"], init_label_item["max_x"]
        ly1 = init_label_item["max_y"]
        candidates = [
            it
            for it in text_items
            if it["y"] > ly1 and not (it["max_x"] < lx0 or it["min_x"] > lx1)
        ]
        candidates.sort(key=lambda it: (it["y"], it["x"]))
        if candidates:
            combined_text = ""
            for candidate in candidates:
                text = candidate["text"]
                if "月" in text:
                    parts = text.split("月")
                    if parts[0]:
                        combined_text += parts[0] + "月"
                    break
                combined_text += text
            init_value = combined_text
    results["初度登録年月"] = {
        "value": init_value,
        "y_position": float(init_label_item["y"]) if init_label_item else 0.0,
        "similarity": init_label_sim if init_label_item else 0.0,
        "keyword_position": 0 if init_label_item else -1,
    }

    return results
