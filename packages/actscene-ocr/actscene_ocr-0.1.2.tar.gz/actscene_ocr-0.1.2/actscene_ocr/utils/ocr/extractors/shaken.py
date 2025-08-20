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

    def _find_vehicle_number_new_logic(text_items):
        """新しい自動車登録番号抽出ロジック"""
        import difflib

        if not text_items:
            return ""

        all_y_coords = [item["max_y"] for item in text_items]
        all_x_coords = [item["max_x"] for item in text_items]

        if not all_y_coords or not all_x_coords:
            return ""

        total_height = max(all_y_coords) - min(all_y_coords)
        total_width = max(all_x_coords) - min(all_x_coords)

        top_5_percent = min(all_y_coords) + total_height * 0.05
        left_10_percent = min(all_x_coords) + total_width * 0.10

        inspection_cert_item = None
        best_similarity = 0.0

        for item in text_items:
            if item["min_y"] > top_5_percent or item["min_x"] > left_10_percent:
                continue

            similarity = difflib.SequenceMatcher(
                None, item["text"], "自動車検査証"
            ).ratio()
            if similarity > best_similarity and similarity > 0.5:
                best_similarity = similarity
                inspection_cert_item = item

        if not inspection_cert_item:
            return ""

        search_bottom = (
            inspection_cert_item["max_y"]
            + (inspection_cert_item["max_y"] - inspection_cert_item["min_y"]) * 1
        )

        search_items = []
        for item in text_items:
            if (
                item["min_y"] <= search_bottom
                and item["max_y"] >= inspection_cert_item["min_y"]
                and item["max_x"] >= inspection_cert_item["min_x"]
                and item["min_x"] <= inspection_cert_item["max_x"]
            ):
                search_items.append(item)

        if not search_items:
            return ""

        anchor_item = min(search_items, key=lambda item: item["min_x"])

        def _is_japanese(text):
            import re

            return bool(re.search(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]", text))

        def _is_number(text):
            import re

            return bool(re.match(r"^[0-9]+$", text))

        right_items = []
        anchor_height = anchor_item["max_y"] - anchor_item["min_y"]

        for item in search_items:
            if item["min_x"] > anchor_item["min_x"]:
                item_height = item["max_y"] - item["min_y"]
                overlap_start = max(anchor_item["min_y"], item["min_y"])
                overlap_end = min(anchor_item["max_y"], item["max_y"])
                overlap_height = max(0, overlap_end - overlap_start)

                min_height = min(anchor_height, item_height)
                overlap_ratio = overlap_height / min_height if min_height > 0 else 0

                if overlap_ratio >= 0.6:
                    right_items.append(item)

        right_items.sort(key=lambda item: item["min_x"])

        combined_text = anchor_item["text"]

        for item in right_items:
            combined_text += item["text"]

        result_parts = []

        if combined_text:
            pattern = []
            current_text = ""

            for char in combined_text:
                current_text += char
                if _is_japanese(current_text):
                    if pattern and pattern[-1][0] == "japanese":
                        pattern[-1] = ("japanese", pattern[-1][1] + char)
                    else:
                        pattern.append(("japanese", current_text))
                    current_text = ""
                elif _is_number(current_text):
                    if pattern and pattern[-1][0] == "number":
                        pattern[-1] = ("number", pattern[-1][1] + char)
                    else:
                        pattern.append(("number", current_text))
                    current_text = ""

            if len(pattern) >= 4:
                if (
                    pattern[0][0] == "japanese"
                    and pattern[1][0] == "number"
                    and pattern[2][0] == "japanese"
                    and pattern[3][0] == "number"
                ):
                    result_parts = [
                        pattern[0][1],
                        pattern[1][1],
                        pattern[2][1],
                        pattern[3][1],
                    ]
        if not result_parts:
            return combined_text

        return "".join(result_parts)

    vehicle_number_value = _find_vehicle_number_new_logic(text_items)

    results["自動車登録番号又は車両番号"] = {
        "value": vehicle_number_value,
        "y_position": 0.0,
        "similarity": 1.0,
        "keyword_position": -1,
    }

    def _is_alphanumeric_only(text):
        """英語と数字の両方を必ず含むかチェック"""
        import re

        has_letter = bool(re.search(r"[A-Za-z]", text))
        has_digit = bool(re.search(r"[0-9]", text))
        return has_letter and has_digit

    def _extract_chassis_number_new_logic(text_items):
        """車台番号抽出ロジック"""
        if not text_items:
            return ""

        leftmost_item = min(text_items, key=lambda item: item["min_x"])
        anchor_x = leftmost_item["min_x"]

        all_x_coords = [item["max_x"] for item in text_items]
        if all_x_coords:
            image_width = max(all_x_coords) - min(all_x_coords)
            search_range = image_width * 0.10
        else:
            search_range = 100

        overlapping_items = []
        for item in text_items:
            if item["min_x"] <= anchor_x + search_range and item["max_x"] >= anchor_x:
                overlapping_items.append(item)

        alphanumeric_items = [
            item for item in overlapping_items if _is_alphanumeric_only(item["text"])
        ]

        if not alphanumeric_items:
            return ""

        top_item = min(alphanumeric_items, key=lambda item: item["min_y"])
        return top_item["text"]

    chassis_value = _extract_chassis_number_new_logic(text_items)

    results["車台番号"] = {
        "value": chassis_value,
        "y_position": 0.0,
        "similarity": 1.0,
        "keyword_position": -1,
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
