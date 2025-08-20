import numpy as np
import re
import unicodedata
import difflib
from typing import Dict, List


def normalize(s):
    """テキストを正規化する（NFKC正規化と空白除去）"""
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", "", s)


def is_vehicle_number_pattern(text):
    """車両番号のパターン（日本語+数字+日本語+数字）かどうかを判定する"""
    pattern = r"^[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+[0-9]+[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+[0-9]+$"
    return bool(re.match(pattern, text))


def normalize_chassis_part(text: str) -> str:
    """車台番号トークンを正規化（全角→半角、各種ダッシュ→'-'、空白除去）"""
    s = unicodedata.normalize("NFKC", text)
    s = (
        s.replace("―", "-")
        .replace("ー", "-")
        .replace("－", "-")
        .replace("–", "-")
        .replace("—", "-")
    )
    s = s.replace(" ", "")
    return s


def is_chassis_token(text: str) -> bool:
    """ASCII英数字とハイフンのみのトークンかどうか"""
    return bool(re.match(r"^[A-Za-z0-9-]+$", text))


def find_keyword_with_flexible_matching(text_items, keyword, max_attempts=3):
    """キーワードを最も類似度が高いものから検索する

    Returns:
        tuple[int, float]: (グループ内インデックス, 類似度)。見つからない場合は (-1, 0.0)
    """
    normalized_keyword = normalize(keyword)

    similarity_list = []
    for i, item in enumerate(text_items):
        item_text = (
            normalize(item["text"])
            if isinstance(item, dict) and "text" in item
            else normalize(str(item))
        )
        similarity = difflib.SequenceMatcher(
            None, item_text, normalized_keyword
        ).ratio()
        similarity_list.append((i, similarity))

    similarity_list.sort(key=lambda x: x[1], reverse=True)

    if similarity_list:
        top_index, top_similarity = similarity_list[0]
        return top_index, float(top_similarity)

    return -1, 0.0


def extract_value_text(keyword, right_items):
    """キーワードに応じて適切な値抽出を行う（共通実装）"""
    return "".join([item["text"] for item in right_items])


def extract_values_generic(
    ocr_results, keywords: List[str], y_tolerance: float = 20
) -> Dict[str, dict]:
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

    def search_keyword_recursive(keyword, current_y_tolerance):
        attempts = 0
        ys = [float(it["y"]) for it in text_items if it.get("y") is not None]
        min_y = min(ys) if ys else 0.0
        max_y = max(ys) if ys else 0.0
        max_tol = max(20000.0, (max_y - min_y) + 20.0)
        while True:
            best_match = None
            best_similarity = 0.0
            for item in text_items:
                similarity = find_keyword_with_flexible_matching([item], keyword)[1]
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = item
            if best_match and best_similarity > 0.3:
                same_line_items = [
                    it
                    for it in text_items
                    if abs(it["y"] - best_match["y"]) <= current_y_tolerance
                ]
                same_line_items.sort(key=lambda x: x["x"])
                keyword_index = -1
                for i, it in enumerate(same_line_items):
                    if it["index"] == best_match["index"]:
                        keyword_index = i
                        break
                value_text = ""
                if keyword_index >= 0 and keyword_index + 1 < len(same_line_items):
                    right_items = same_line_items[keyword_index + 1 :]
                    value_text = extract_value_text(keyword, right_items)
                if value_text:
                    return {
                        "value": value_text,
                        "y_position": float(best_match["y"]),
                        "similarity": float(best_similarity),
                        "keyword_position": keyword_index,
                        "used_y_tolerance": current_y_tolerance,
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
