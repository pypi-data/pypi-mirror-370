from typing import Dict
import numpy as np

from .generic import find_keyword_with_flexible_matching
from ..geometry import (
    extract_y_intervals_from_polys,
    merge_intervals,
    compute_safe_cut_lines_y,
)


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


def extract_values_inkan(ocr_results) -> Dict[str, dict]:
    if not ocr_results:
        return {}

    text_items = _build_text_items(ocr_results)
    if not text_items:
        return {}

    polys = [it["box"] for it in text_items]
    if not polys:
        return {
            "氏名": {
                "value": "",
                "y_position": 0.0,
                "similarity": 0.0,
                "keyword_position": -1,
            }
        }

    max_y = max(float(it["max_y"]) for it in text_items)
    image_height = int(max(1.0, np.ceil(max_y)))

    intervals_y = extract_y_intervals_from_polys(polys)
    merged_y = merge_intervals(intervals_y, min_gap=0.0)
    safe_lines = compute_safe_cut_lines_y(merged_y, image_height)

    bounds = [0] + safe_lines + [image_height]
    line_bands = [
        (bounds[i], bounds[i + 1])
        for i in range(len(bounds) - 1)
        if bounds[i + 1] > bounds[i]
    ]

    keywords = ["取締役", "代表取締役", "支配人"]

    best_candidate = {
        "value": "",
        "y_position": 0.0,
        "similarity": 0.0,
        "keyword_position": -1,
    }
    best_addr = {
        "value": "",
        "y_position": 0.0,
        "similarity": 0.0,
        "keyword_position": -1,
    }

    for y0, y1 in line_bands:
        line_items = [it for it in text_items if y0 <= it["y"] < y1]
        if not line_items:
            continue
        line_items_sorted = sorted(line_items, key=lambda it: it["x"])

        best_line_keyword = ""
        best_line_similarity = 0.0
        best_line_combined_text = ""

        line_combined_text = "".join([it["text"] for it in line_items_sorted])

        # 先頭一致の類似度でキーワードを評価（代表取締役 > 取締役 のようにスコアで選ぶ）
        import difflib

        for kw in keywords:
            head_len = min(len(kw), len(line_combined_text))
            if head_len <= 0:
                continue
            sim = difflib.SequenceMatcher(
                None, line_combined_text[:head_len], kw
            ).ratio()
            if sim > best_line_similarity:
                best_line_similarity = float(sim)
                best_line_keyword = kw
                best_line_combined_text = line_combined_text

        if best_line_similarity > 0.3:
            # キーワード終端までの文字数を計算し、そこまでのトークンを全て捨てる
            cut_pos = len(best_line_keyword)
            right_items = []
            current_pos = 0
            for item in line_items_sorted:
                item_len = len(item["text"])
                end_pos = current_pos + item_len
                if end_pos > cut_pos:
                    right_items.append(item)
                current_pos = end_pos

            value_text = "".join([it["text"] for it in right_items])

            if right_items:
                right_min_x = min(float(it["min_x"]) for it in right_items)
                right_max_x = max(float(it["max_x"]) for it in right_items)
                right_min_y = min(float(it["min_y"]) for it in right_items)
                right_max_y = max(float(it["max_y"]) for it in right_items)
                right_h = max(1.0, right_max_y - right_min_y)
                win_y0 = right_max_y
                win_y1 = right_max_y + right_h

                below_items = [
                    it
                    for it in text_items
                    if (win_y0 < float(it["y"]) <= win_y1)
                    and (right_min_x <= float(it["x"]) <= right_max_x)
                ]
                if below_items:
                    below_items_sorted = sorted(
                        below_items, key=lambda t: (t["y"], t["x"])
                    )
                    value_text += "".join([it["text"] for it in below_items_sorted])

            if value_text and (
                best_line_similarity > best_candidate["similarity"]
                or (
                    abs(best_line_similarity - best_candidate["similarity"]) < 1e-6
                    and line_items_sorted[0]["y"] < best_candidate["y_position"]
                )
            ):
                best_candidate = {
                    "value": value_text,
                    "y_position": float(line_items_sorted[0]["y"]),
                    "similarity": float(best_line_similarity),
                    "keyword_position": 0,
                }

        addr_keywords = ["本店", "営業所"]
        best_line_similarity_addr = 0.0
        best_line_keyword_addr = ""
        best_line_combined_text = ""

        line_combined_text = "".join([it["text"] for it in line_items_sorted])

        for kw in addr_keywords:
            # 結合テキストの先頭部分で柔軟一致
            import difflib

            search_len = min(len(kw), len(line_combined_text))
            if search_len > 0:
                sim = difflib.SequenceMatcher(
                    None, line_combined_text[:search_len], kw
                ).ratio()
                if sim > best_line_similarity_addr:
                    best_line_similarity_addr = float(sim)
                    best_line_keyword_addr = kw
                    best_line_combined_text = line_combined_text

        if best_line_similarity_addr > 0.3:
            search_len = 2 if best_line_keyword_addr == "本店" else 3
            search_text = best_line_keyword_addr[:search_len]
            keyword_pos = best_line_combined_text.find(search_text)

            right_items = []
            current_pos = 0
            for item in line_items_sorted:
                item_len = len(item["text"])
                if current_pos + item_len > keyword_pos:
                    right_items.append(item)
                current_pos += item_len

            addr_text = "".join([it["text"] for it in right_items])

            # キーワード部分を除去
            if best_line_keyword_addr in addr_text:
                addr_text = addr_text.replace(best_line_keyword_addr, "")
            elif best_line_keyword_addr[:2] in addr_text:  # 本店、業所の場合
                addr_text = addr_text.replace(best_line_keyword_addr[:2], "")

            if right_items:
                right_min_x = min(float(it["min_x"]) for it in right_items)
                right_max_x = max(float(it["max_x"]) for it in right_items)
                right_min_y = min(float(it["min_y"]) for it in right_items)
                right_max_y = max(float(it["max_y"]) for it in right_items)
                right_h = max(1.0, right_max_y - right_min_y)
                win_y0 = right_max_y
                win_y1 = right_max_y + right_h

                below_items = [
                    it
                    for it in text_items
                    if (win_y0 < float(it["y"]) <= win_y1)
                    and (right_min_x <= float(it["x"]) <= right_max_x)
                ]
                if below_items:
                    below_items_sorted = sorted(
                        below_items, key=lambda t: (t["y"], t["x"])
                    )
                    addr_text += "".join([it["text"] for it in below_items_sorted])

            if addr_text and (
                best_line_similarity_addr > best_addr["similarity"]
                or (
                    abs(best_line_similarity_addr - best_addr["similarity"]) < 1e-6
                    and line_items_sorted[0]["y"] < best_addr["y_position"]
                )
            ):
                best_addr = {
                    "value": addr_text,
                    "y_position": float(line_items_sorted[0]["y"]),
                    "similarity": float(best_line_similarity_addr),
                    "keyword_position": 0,
                }

    return {"氏名": best_candidate, "住所": best_addr}
