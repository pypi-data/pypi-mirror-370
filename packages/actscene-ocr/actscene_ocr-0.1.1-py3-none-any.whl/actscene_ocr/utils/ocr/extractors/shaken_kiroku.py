from typing import Dict, List
import numpy as np

from .generic import find_keyword_with_flexible_matching, extract_value_text


def extract_values_shaken_kiroku(
    ocr_results,
    keywords: List[str],
    y_tolerance: float = 20,
    *,
    min_vertical_overlap_ratio: float = 0.1,
    downward_window_factor: float = 3.0,
) -> Dict[str, dict]:
    if not ocr_results:
        return {}
    texts = ocr_results[0].get("rec_texts", [])
    boxes = ocr_results[0].get("rec_polys", [])
    confidences = ocr_results[0].get("rec_scores", [])
    text_items = []
    for i, (text, box, conf) in enumerate(zip(texts, boxes, confidences)):
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
    if not text_items:
        return {}
    ys = [float(it["y"]) for it in text_items if it.get("y") is not None]
    min_y = min(ys) if ys else 0.0
    max_y = max(ys) if ys else 0.0
    max_tol = max(20000.0, (max_y - min_y) + 20.0)

    def search_keyword_recursive(keyword, current_y_tolerance):
        attempts = 0
        while True:
            best_match = None
            best_similarity = 0.0
            for item in text_items:
                similarity = find_keyword_with_flexible_matching([item], keyword)[1]
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = item
            if best_match and best_similarity > 0.3:
                anchor_arr = np.array(best_match["box"], dtype=float)
                anchor_min_y = float(anchor_arr[:, 1].min())
                anchor_max_y = float(anchor_arr[:, 1].max())

                def _overlap_ratio(min_a, max_a, min_b, max_b):
                    ov = max(0.0, min(max_a, max_b) - max(min_a, min_b))
                    hb = max(1e-6, max_b - min_b)
                    return ov / hb

                same_line_items = []
                for it in text_items:
                    ibox = np.array(it["box"], dtype=float)
                    cmin_y = float(ibox[:, 1].min())
                    cmax_y = float(ibox[:, 1].max())
                    cmin_x = float(ibox[:, 0].min())
                    cmax_x = float(ibox[:, 0].max())
                    ratio = _overlap_ratio(anchor_min_y, anchor_max_y, cmin_y, cmax_y)
                    if ratio >= float(min_vertical_overlap_ratio):
                        same_line_items.append(it)

                filtered_items = []
                for i, item1 in enumerate(same_line_items):
                    box1 = np.array(item1["box"], dtype=float)
                    min_x1 = float(box1[:, 0].min())
                    max_x1 = float(box1[:, 0].max())
                    min_y1 = float(box1[:, 1].min())
                    max_y1 = float(box1[:, 1].max())

                    should_exclude = False
                    for j, item2 in enumerate(same_line_items):
                        if i == j:
                            continue
                        box2 = np.array(item2["box"], dtype=float)
                        min_x2 = float(box2[:, 0].min())
                        max_x2 = float(box2[:, 0].max())
                        min_y2 = float(box2[:, 1].min())
                        max_y2 = float(box2[:, 1].max())

                        x_overlap = max(0, min(max_x1, max_x2) - max(min_x1, min_x2))
                        if x_overlap > 0:
                            if max_y1 < min_y2:
                                should_exclude = True
                                break

                    if not should_exclude:
                        filtered_items.append(item1)

                same_line_items = filtered_items
                same_line_items.sort(key=lambda x: x["x"])
                keyword_index = -1
                for i, it in enumerate(same_line_items):
                    if it["index"] == best_match["index"]:
                        keyword_index = i
                        break
                value_text = ""

                if keyword in ["所有者の氏名又は名称", "所有者の住所"]:
                    arr = np.array(best_match["box"], dtype=float)
                    anchor_center_x = float(np.mean(arr[:, 0]))
                    anchor_min_y = float(arr[:, 1].min())
                    anchor_max_y = float(arr[:, 1].max())
                    anchor_height = anchor_max_y - anchor_min_y

                    y_lo = anchor_min_y
                    y_hi = anchor_max_y + anchor_height * 3.0
                    x_lo = anchor_center_x

                    region_items = []
                    for it in text_items:
                        ibox = np.array(it["box"], dtype=float)
                        cmin_x = float(ibox[:, 0].min())
                        cmin_y = float(ibox[:, 1].min())
                        cmax_y = float(ibox[:, 1].max())
                        if cmin_x >= x_lo and y_lo <= cmin_y <= y_hi:
                            region_items.append((cmin_x, cmin_y, cmax_y, it))

                    region_items.sort(key=lambda t: t[0])

                    filtered_items = []
                    for i, (x1, y1_min, y1_max, item1) in enumerate(region_items):
                        should_exclude = False
                        for j, (x2, y2_min, y2_max, item2) in enumerate(region_items):
                            if i == j:
                                continue

                            x_overlap = max(0, min(x1 + 100, x2 + 100) - max(x1, x2))
                            y_overlap = max(
                                0, min(y1_max, y2_max) - max(y1_min, y2_min)
                            )
                            if x_overlap > 0 and y_overlap > 0:
                                if y1_min > y2_min:
                                    should_exclude = True
                                    break
                        if not should_exclude:
                            filtered_items.append(item1)

                    if keyword == "所有者の住所":
                        if filtered_items:
                            top_item = min(filtered_items, key=lambda item: item["y"])
                            top_y = top_item["y"]

                            same_line_items = []
                            top_box = np.array(top_item["box"], dtype=float)
                            top_height = float(
                                top_box[:, 1].max() - top_box[:, 1].min()
                            )

                            for item in filtered_items:
                                item_y = item["y"]
                                item_box = np.array(item["box"], dtype=float)
                                item_height = float(
                                    item_box[:, 1].max() - item_box[:, 1].min()
                                )

                                avg_height = (top_height + item_height) / 2
                                tolerance = avg_height * 0.5

                                if abs(item_y - top_y) <= tolerance:
                                    same_line_items.append(item)

                            same_line_items.sort(key=lambda x: x["x"])

                            combined_parts = []
                            for item in same_line_items:
                                text = item["text"]
                                if "[" in text:
                                    parts = text.split("[")
                                    if parts[0]:
                                        combined_parts.append(parts[0])
                                    break
                                combined_parts.append(text)
                            value_text = "".join(combined_parts)
                        else:
                            value_text = ""

                    else:
                        if filtered_items:
                            top_item = min(filtered_items, key=lambda item: item["y"])
                            top_y = top_item["y"]

                            same_line_items = []
                            top_box = np.array(top_item["box"], dtype=float)
                            top_height = float(
                                top_box[:, 1].max() - top_box[:, 1].min()
                            )

                            for item in filtered_items:
                                item_y = item["y"]
                                item_box = np.array(item["box"], dtype=float)
                                item_height = float(
                                    item_box[:, 1].max() - item_box[:, 1].min()
                                )

                                avg_height = (top_height + item_height) / 2
                                tolerance = avg_height * 0.5

                                if abs(item_y - top_y) <= tolerance:
                                    same_line_items.append(item)

                            same_line_items.sort(key=lambda x: x["x"])

                            value_text = "".join(
                                [item["text"] for item in same_line_items]
                            )
                        else:
                            value_text = ""

                elif keyword_index >= 0 and keyword_index + 1 < len(same_line_items):
                    right_items = same_line_items[keyword_index + 1 :]

                    if keyword == "初度登録年月":
                        combined_parts = []
                        for item in right_items:
                            text = item["text"]
                            if "月" in text:
                                parts = text.split("月")
                                if parts[0]:
                                    combined_parts.append(parts[0] + "月")
                                break
                            combined_parts.append(text)
                        value_text = "".join(combined_parts)

                    elif keyword == "有効期限の満了する日":
                        combined_parts = []
                        for item in right_items:
                            text = item["text"]
                            if "日" in text:
                                parts = text.split("日")
                                if parts[0]:
                                    combined_parts.append(parts[0] + "日")
                                break
                            combined_parts.append(text)
                        value_text = "".join(combined_parts)

                    elif keyword == "車台番号":
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
                        value_text = "".join(combined_parts)

                    elif keyword == "自動車登録番号又は車両番号":
                        combined_parts = []
                        for item in right_items:
                            text = item["text"]
                            combined_parts.append(text)

                            import re

                            pattern = r"^[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+[0-9]+[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+[0-9]+$"
                            if re.match(pattern, "".join(combined_parts)):
                                break
                        value_text = "".join(combined_parts)

                    else:
                        value_text = extract_value_text(keyword, right_items)
                        arr = np.array(best_match["box"], dtype=float)
                        anchor_max_x = float(arr[:, 0].max())
                        anchor_min_y = float(arr[:, 1].min())
                        anchor_max_y = float(arr[:, 1].max())
                        anchor_height = anchor_max_y - anchor_min_y

                        y_lo = anchor_max_y
                        y_hi = anchor_max_y + anchor_height * 3.0
                        x_lo = anchor_max_x

                        region_items = []
                        for it in text_items:
                            ibox = np.array(it["box"], dtype=float)
                            cmin_x = float(ibox[:, 0].min())
                            cmin_y = float(ibox[:, 1].min())
                            cmax_y = float(ibox[:, 1].max())
                            if cmin_x >= x_lo and y_lo <= cmin_y <= y_hi:
                                region_items.append((cmin_x, cmin_y, cmax_y, it))

                        region_items.sort(key=lambda t: t[0])

                        filtered_items = []
                        for i, (x1, y1_min, y1_max, item1) in enumerate(region_items):
                            should_exclude = False
                            for j, (x2, y2_min, y2_max, item2) in enumerate(
                                region_items
                            ):
                                if i == j:
                                    continue

                                x_overlap = max(
                                    0, min(x1 + 100, x2 + 100) - max(x1, x2)
                                )
                                y_overlap = max(
                                    0, min(y1_max, y2_max) - max(y1_min, y2_min)
                                )
                                if x_overlap > 0 and y_overlap > 0:
                                    if y1_min > y2_min:
                                        should_exclude = True
                                        break
                            if not should_exclude:
                                filtered_items.append(item1)

                        combined_parts = []
                        for item in filtered_items:
                            text = item["text"]
                            if "[" in text:
                                parts = text.split("[")
                                if parts[0]:
                                    combined_parts.append(parts[0])
                                break
                            combined_parts.append(text)
                        value_text = "".join(combined_parts)

                elif keyword_index >= 0 and keyword_index + 1 < len(same_line_items):
                    right_items = same_line_items[keyword_index + 1 :]

                    if keyword == "初度登録年月":
                        combined_parts = []
                        for item in right_items:
                            text = item["text"]
                            combined_parts.append(text)
                            if "月" in text:
                                break
                        value_text = "".join(combined_parts)

                    elif keyword == "有効期限の満了する日":
                        combined_parts = []
                        for item in right_items:
                            text = item["text"]
                            combined_parts.append(text)
                            if "日" in text:
                                break
                        value_text = "".join(combined_parts)

                    elif keyword == "車台番号":
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
                        value_text = "".join(combined_parts)

                    elif keyword == "自動車登録番号又は車両番号":
                        combined_parts = []
                        for item in right_items:
                            text = item["text"]
                            combined_parts.append(text)

                            import re

                            pattern = r"^[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+[0-9]+[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+[0-9]+$"
                            if re.match(pattern, "".join(combined_parts)):
                                break
                        value_text = "".join(combined_parts)

                    else:
                        value_text = extract_value_text(keyword, right_items)

                if value_text:
                    return {
                        "value": value_text,
                        "y_position": float(best_match["y"]),
                        "similarity": float(best_similarity),
                        "keyword_position": keyword_index,
                    }
            if current_y_tolerance >= max_tol:
                return {
                    "value": "",
                    "y_position": 0.0,
                    "similarity": 0.0,
                    "keyword_position": -1,
                }
            current_y_tolerance = min(current_y_tolerance * 2, max_tol)
            attempts += 1

    results = {}
    for keyword in keywords:
        results[keyword] = search_keyword_recursive(keyword, y_tolerance)
    return results
