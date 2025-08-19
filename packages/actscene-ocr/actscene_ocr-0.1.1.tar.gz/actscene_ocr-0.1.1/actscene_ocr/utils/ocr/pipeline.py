import os
from dataclasses import dataclass
from typing import Optional

import numpy as np
import time
import cv2
from PIL import Image
from paddleocr import PaddleOCR

from ..document_scanner import scan_document
from ..resize_image import resize_image_array
from . import correct_orientation
from .draw import draw_debug_overlays
from .geometry import (
    extract_y_intervals_from_polys,
    extract_x_intervals_from_polys,
    merge_intervals,
    compute_safe_cut_lines_y,
)
from .extractors.generic import find_keyword_with_flexible_matching


def _convert_fullwidth_to_halfwidth(text: str) -> str:
    """全角文字を半角文字に変換する"""
    if not text:
        return text

    text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))

    text = text.translate(
        str.maketrans(
            "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        )
    )

    text = text.translate(str.maketrans("（）", "()"))
    return text


@dataclass
class SegmentOptions:
    segment_max_height: Optional[int] = None
    orientation_detect_size: int = 600
    detect_size: int = 1400
    debug_dir: Optional[str] = None
    max_segment_pixels: int = 1_000_000
    orientation_ocr: Optional[object] = None
    base_ocr: Optional[object] = None
    max_side_limit: int = 4000
    rec_short_side: int = 64
    cluster_expand_margin: int = 0
    cell_trim_margin: int = 4
    cut_guard_margin: int = 0
    binarize: bool = False
    blur_sigma: float = 0.0
    segment_only: bool = False


def group_texts_by_y_position(ocr_results, y_tolerance=None):
    if not ocr_results:
        return []
    texts = ocr_results[0].get("rec_texts", [])
    boxes = ocr_results[0].get("rec_polys", [])
    confidences = ocr_results[0].get("rec_scores", [])
    text_items = []
    for i, (text, box, conf) in enumerate(zip(texts, boxes, confidences)):
        try:
            if isinstance(box, (list, np.ndarray)):
                box_array = np.array(box)
                center_y = np.mean(box_array[:, 1])
                text_items.append(
                    {
                        "text": text,
                        "y": center_y,
                        "confidence": float(conf),
                        "box": box_array.tolist()
                        if isinstance(box_array, np.ndarray)
                        else box,
                    }
                )
        except Exception:
            continue
    if not text_items:
        return []
    text_items.sort(key=lambda x: x["y"])
    groups = []
    current_group = [text_items[0]]
    for item in text_items[1:]:
        y_diff = abs(item["y"] - current_group[-1]["y"])
        if y_tolerance is None or y_diff <= y_tolerance:
            current_group.append(item)
        else:
            groups.append(current_group)
            current_group = [item]
    groups.append(current_group)
    return groups


def find_keyword_and_value(groups, keywords):
    results = {}
    for keyword in keywords:
        best_group_index = -1
        best_group_sorted = None
        best_keyword_index = -1
        best_similarity = 0.0
        for group_idx, group in enumerate(groups):
            sorted_group = sorted(
                group, key=lambda x: np.mean([point[0] for point in x["box"]])
            )
            keyword_index, similarity = find_keyword_with_flexible_matching(
                sorted_group, keyword
            )
            if keyword_index >= 0 and similarity >= best_similarity:
                best_similarity = similarity
                best_keyword_index = keyword_index
                best_group_index = group_idx
                best_group_sorted = sorted_group
        if best_group_sorted is not None:
            value_text = ""
            if best_keyword_index + 1 < len(best_group_sorted):
                value_text = best_group_sorted[best_keyword_index + 1]["text"]
            if keyword in ["自動車登録番号又は車両番号", "車台番号"]:
                combined_parts = []
                for i in range(1, len(best_group_sorted) - best_keyword_index):
                    combined_parts.append(
                        best_group_sorted[best_keyword_index + i]["text"]
                    )
                value_text = "".join(combined_parts)
            results[keyword] = {
                "value": value_text,
                "group_index": best_group_index,
                "y_position": float(best_group_sorted[0]["y"]),
                "similarity": float(best_similarity),
            }
    return results


def _ensure_rgb_array(image_array):
    if len(image_array.shape) == 2:
        return cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
    return image_array


def run_ocr_pipeline(image_path, ocr, max_size=1300, orientation_detect_size=600):
    pil_image = Image.open(image_path)
    scanned_image = scan_document(pil_image)
    oriented_image = correct_orientation(
        scanned_image, max_size=orientation_detect_size
    )
    oriented_array = np.array(oriented_image)
    resized_array = resize_image_array(oriented_array, max_size=max_size)
    processed_array = _ensure_rgb_array(np.array(resized_array))
    ocr_results = ocr.predict(processed_array)
    return ocr_results, processed_array


def build_ocr_details(ocr_results):
    details = []
    if ocr_results and len(ocr_results) > 0:
        texts = ocr_results[0].get("rec_texts", [])
        boxes = ocr_results[0].get("rec_polys", [])
        confidences = ocr_results[0].get("rec_scores", [])
        for text, box, conf in zip(texts, boxes, confidences):
            if isinstance(box, (list, np.ndarray)):
                box_array = np.array(box)
                center_y = float(np.mean(box_array[:, 1]))
                center_x = float(np.mean(box_array[:, 0]))
                details.append(
                    {
                        "text": text,
                        "x": center_x,
                        "y": center_y,
                        "confidence": float(conf),
                        "box": box_array.tolist()
                        if isinstance(box_array, np.ndarray)
                        else box,
                    }
                )
    return details


def run_ocr_pipeline_segmented(
    image_path,
    ocr,
    segment_max_height=None,
    orientation_detect_size=600,
    detect_size=1400,
    debug_dir=None,
    max_segment_pixels=1_000_000,
    orientation_ocr=None,
    base_ocr=None,
    max_side_limit=4000,
    rec_short_side=64,
    cluster_expand_margin=0,
    cell_trim_margin=4,
    cut_guard_margin=0,
    binarize=False,
    blur_sigma: float = 0.0,
    segment_only: bool = False,
    config: Optional[SegmentOptions] = None,
):
    if config is not None:
        if config.segment_max_height is not None:
            segment_max_height = config.segment_max_height
        orientation_detect_size = config.orientation_detect_size
        detect_size = config.detect_size
        debug_dir = debug_dir or config.debug_dir
        max_segment_pixels = config.max_segment_pixels
        orientation_ocr = orientation_ocr or config.orientation_ocr
        base_ocr = base_ocr or config.base_ocr
        max_side_limit = config.max_side_limit
        rec_short_side = config.rec_short_side
        cluster_expand_margin = config.cluster_expand_margin
        cell_trim_margin = config.cell_trim_margin
        cut_guard_margin = config.cut_guard_margin
        binarize = config.binarize
        blur_sigma = config.blur_sigma
        segment_only = config.segment_only

    _unused_params = (
        segment_max_height,
        cluster_expand_margin,
        cell_trim_margin,
        cut_guard_margin,
        max_side_limit,
        rec_short_side,
    )
    pil_image = Image.open(image_path)
    scanned_image = scan_document(pil_image, debug_dir=debug_dir)
    oriented_image = correct_orientation(
        scanned_image, max_size=orientation_detect_size, orientation_ocr=orientation_ocr
    )
    oriented_rgb = np.array(oriented_image)

    if bool(binarize):
        try:
            gray = (
                oriented_rgb
                if len(oriented_rgb.shape) == 2
                else cv2.cvtColor(oriented_rgb, cv2.COLOR_RGB2GRAY)
            )
            if isinstance(blur_sigma, (int, float)) and float(blur_sigma) > 0.0:
                gray = cv2.GaussianBlur(gray, (0, 0), float(blur_sigma))
            _thr, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            oriented_rgb = cv2.cvtColor(bw, cv2.COLOR_GRAY2RGB)
        except Exception:
            pass
    else:
        if isinstance(blur_sigma, (int, float)) and float(blur_sigma) > 0.0:
            try:
                oriented_rgb = cv2.GaussianBlur(oriented_rgb, (0, 0), float(blur_sigma))
            except Exception:
                pass
    if len(oriented_rgb.shape) == 2:
        oriented_rgb = cv2.cvtColor(oriented_rgb, cv2.COLOR_GRAY2RGB)

    full_h, full_w = oriented_rgb.shape[:2]
    scale_area = 1.0
    if max_segment_pixels is not None:
        total_pixels = float(max(1, full_h * full_w))
        if total_pixels > float(max_segment_pixels):
            scale_area = (float(max_segment_pixels) / total_pixels) ** 0.5
    scale_dim = 1.0
    if detect_size is not None and max(full_h, full_w) > detect_size:
        scale_dim = float(detect_size) / float(max(full_h, full_w))
    scale = min(scale_area, scale_dim, 1.0)
    if scale < 1.0:
        new_w = max(1, int(round(full_w * scale)))
        new_h = max(1, int(round(full_h * scale)))
        detect_rgb = cv2.resize(
            oriented_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA
        )
    else:
        detect_rgb = oriented_rgb
    det_h, det_w = detect_rgb.shape[:2]
    scale_y = full_h / float(det_h)
    scale_x = full_w / float(det_w)

    if base_ocr is None:
        base_ocr = PaddleOCR(
            lang="japan",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
    det_results = base_ocr.predict(detect_rgb)
    rec_polys_det = det_results[0].get("rec_polys", []) if det_results else []

    intervals_y = extract_y_intervals_from_polys(rec_polys_det)
    merged_intervals_y = merge_intervals(intervals_y, min_gap=0.0)
    safe_lines_det_y = compute_safe_cut_lines_y(merged_intervals_y, det_h)

    intervals_x = extract_x_intervals_from_polys(rec_polys_det)
    merged_intervals_x = merge_intervals(intervals_x, min_gap=0.0)

    def _compute_safe_cut_lines_x(merged_intervals, image_width):
        return compute_safe_cut_lines_y(merged_intervals, image_width)

    safe_lines_det_x = _compute_safe_cut_lines_x(merged_intervals_x, det_w)
    _unused_safe_x = safe_lines_det_x

    safe_lines_full_y = [int(round(y * scale_y)) for y in safe_lines_det_y]
    _unused_safe_y = safe_lines_full_y
    polys_full = []
    for poly in rec_polys_det:
        try:
            arr = np.array(poly, dtype=float)
            arr[:, 0] = arr[:, 0] * scale_x
            arr[:, 1] = arr[:, 1] * scale_y
            polys_full.append(arr.tolist())
        except Exception:
            continue

    if debug_dir is not None:
        os.makedirs(debug_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(image_path))[0]
        oriented_path = os.path.join(debug_dir, f"{base}_oriented.jpg")
        cv2.imwrite(oriented_path, cv2.cvtColor(oriented_rgb, cv2.COLOR_RGB2BGR))

    def _build_y_bands_from_polys(polys, image_height):
        intervals = extract_y_intervals_from_polys(polys)
        merged = merge_intervals(intervals, min_gap=0.0)
        ranges = []
        for ys, ye in merged or [(0.0, float(image_height))]:
            y0i = max(0, int(np.floor(ys)))
            y1i = min(image_height, int(np.ceil(ye)))
            if y1i > y0i:
                ranges.append((y0i, y1i))
        if not ranges:
            ranges = [(0, image_height)]
        return ranges

    band_ranges_y = _build_y_bands_from_polys(polys_full, full_h)

    def _poly_bounds(poly):
        arr = np.array(poly, dtype=float)
        xs = arr[:, 0]
        ys = arr[:, 1]
        return float(xs.min()), float(xs.max()), float(ys.min()), float(ys.max())

    poly_infos = []
    for poly in polys_full:
        try:
            minx, maxx, miny, maxy = _poly_bounds(poly)
            cx = 0.5 * (minx + maxx)
            cy = 0.5 * (miny + maxy)
            poly_infos.append(
                {
                    "poly": poly,
                    "minx": minx,
                    "maxx": maxx,
                    "miny": miny,
                    "maxy": maxy,
                    "cx": cx,
                    "cy": cy,
                }
            )
        except Exception:
            continue

    band_includes = [[] for _ in band_ranges_y]
    for idx_band, (y0, y1) in enumerate(band_ranges_y):
        for info in poly_infos:
            if y0 <= info["cy"] <= y1:
                band_includes[idx_band].append(info)

    trim_margin = 6
    band_rects = []
    for idx_band, (y0, y1) in enumerate(band_ranges_y):
        includes = band_includes[idx_band]
        if includes:
            min_x = int(np.floor(min(info["minx"] for info in includes)))
            max_x = int(np.ceil(max(info["maxx"] for info in includes)))
            x0 = max(0, min_x - trim_margin)
            x1 = min(full_w, max_x + trim_margin)
            if x1 <= x0:
                x0, x1 = 0, full_w
        else:
            x0, x1 = 0, full_w
        band_rects.append((x0, y0, x1, y1))

    segment_bands = []
    palette = [
        (0, 128, 255),
        (0, 255, 128),
        (255, 128, 0),
        (128, 0, 255),
        (255, 0, 128),
        (128, 255, 0),
        (0, 255, 255),
        (255, 0, 0),
        (0, 128, 128),
        (128, 128, 0),
    ]
    for i, (x0, y0, x1, y1) in enumerate(band_rects):
        segment_bands.append(
            {
                "rect": (x0, y0, x1, y1),
                "color": palette[i % len(palette)],
                "alpha": 0.22,
            }
        )

    vertical_cells_all = []
    final_segments = []
    for idx_band, (x0, y0, x1, y1) in enumerate(band_rects):
        band_h = max(1, y1 - y0)
        band_w = max(1, x1 - x0)
        band_area = band_h * band_w
        included_infos = band_includes[idx_band]

        band_intervals_x_local = []
        for info in included_infos:
            lx0 = max(0.0, float(info["minx"]) - float(x0))
            lx1 = min(float(band_w), float(info["maxx"]) - float(x0))
            if lx1 > lx0:
                band_intervals_x_local.append((lx0, lx1))
        band_merged_x_local = merge_intervals(band_intervals_x_local, min_gap=0.0)
        safe_x_lines_local = []
        if band_merged_x_local:
            safe_x_lines_local = compute_safe_cut_lines_y(band_merged_x_local, band_w)
        safe_x_lines_abs = [
            int(x0 + lx) for lx in safe_x_lines_local if 0 < int(lx) < band_w
        ]

        if max_segment_pixels is not None and band_area > int(max_segment_pixels):
            safes = sorted(set([sx for sx in safe_x_lines_abs if x0 < sx < x1]))
            if safes:
                xs = [x0] + safes + [x1]
                for i in range(len(xs) - 1):
                    cx0, cx1 = xs[i], xs[i + 1]
                    if cx1 <= cx0:
                        continue
                    has_text = any(
                        not (info["maxx"] <= cx0 or info["minx"] >= cx1)
                        for info in included_infos
                    )
                    if not has_text:
                        continue
                    vertical_cells_all.append((cx0, y0, cx1, y1))
                    final_segments.append(
                        {"rect": (cx0, y0, cx1, y1), "band": idx_band}
                    )
            else:
                if included_infos:
                    final_segments.append({"rect": (x0, y0, x1, y1), "band": idx_band})
        else:
            if included_infos:
                final_segments.append({"rect": (x0, y0, x1, y1), "band": idx_band})

    if max_segment_pixels is not None:

        def _trim_band_rect(bx0, by0, bx1, by1, included):
            if included:
                min_x = int(np.floor(min(info["minx"] for info in included)))
                max_x = int(np.ceil(max(info["maxx"] for info in included)))
                tx0 = max(bx0, min_x - trim_margin)
                tx1 = min(bx1, max_x + trim_margin)
                if tx1 <= tx0:
                    return bx0, bx1
                return tx0, tx1
            return bx0, bx1

        def _safe_x_cuts(bx0, bx1, included):
            band_w2 = max(1, bx1 - bx0)
            intervals_local = []
            for info in included:
                lx0 = max(0.0, float(info["minx"]) - float(bx0))
                lx1 = min(float(band_w2), float(info["maxx"]) - float(bx0))
                if lx1 > lx0:
                    intervals_local.append((lx0, lx1))
            merged_local = merge_intervals(intervals_local, min_gap=0.0)
            if not merged_local:
                return []
            safe_local = compute_safe_cut_lines_y(merged_local, band_w2)
            safes_abs = [int(bx0 + lx) for lx in safe_local if 0 < int(lx) < band_w2]
            return sorted(set([sx for sx in safes_abs if bx0 < sx < bx1]))

        def _subdivide_segment(rect, parent_band_index):
            sx0, sy0, sx1, sy1 = rect
            infos_in_rect = [
                info
                for info in poly_infos
                if not (
                    info["maxx"] <= sx0
                    or info["minx"] >= sx1
                    or info["maxy"] <= sy0
                    or info["miny"] >= sy1
                )
            ]
            if not infos_in_rect:
                return []
            y_intervals = []
            for info in infos_in_rect:
                ys = max(float(sy0), float(info["miny"]))
                ye = min(float(sy1), float(info["maxy"]))
                if ye > ys:
                    y_intervals.append((ys, ye))
            if not y_intervals:
                return []
            merged_y = merge_intervals(y_intervals, min_gap=0.0)
            band_ranges = []
            for ys, ye in merged_y:
                y0b = max(sy0, int(np.floor(ys)))
                y1b = min(sy1, int(np.ceil(ye)))
                if y1b > y0b:
                    band_ranges.append((y0b, y1b))
            if not band_ranges:
                return []
            children = []
            for y0b, y1b in band_ranges:
                included = [info for info in infos_in_rect if y0b <= info["cy"] <= y1b]
                bx0, bx1 = _trim_band_rect(sx0, y0b, sx1, y1b, included)
                band_w2 = max(1, bx1 - bx0)
                band_h2 = max(1, y1b - y0b)
                band_area2 = band_w2 * band_h2
                safes = _safe_x_cuts(bx0, bx1, included)
                if band_area2 > int(max_segment_pixels) and safes:
                    xs = [bx0] + safes + [bx1]
                    for i in range(len(xs) - 1):
                        cx0, cx1 = xs[i], xs[i + 1]
                        if cx1 <= cx0:
                            continue
                        has_text = any(
                            not (info["maxx"] <= cx0 or info["minx"] >= cx1)
                            for info in included
                        )
                        if not has_text:
                            continue
                        children.append(
                            {"rect": (cx0, y0b, cx1, y1b), "band": parent_band_index}
                        )
                else:
                    if included:
                        children.append(
                            {"rect": (bx0, y0b, bx1, y1b), "band": parent_band_index}
                        )
            return children

        refined = []
        queue = list(final_segments)
        while queue:
            seg = queue.pop(0)
            x0, y0, x1, y1 = seg.get("rect", (0, 0, 0, 0))
            area = max(1, (x1 - x0)) * max(1, (y1 - y0))
            if area > int(max_segment_pixels):
                children = _subdivide_segment((x0, y0, x1, y1), seg.get("band", 0))
                if children and not (
                    len(children) == 1 and children[0].get("rect") == (x0, y0, x1, y1)
                ):
                    queue.extend(children)
                    continue
            refined.append(seg)
        final_segments = refined

    exclude_masks_all = []

    grid_cells = [seg["rect"] for seg in final_segments]
    final_cells = list(grid_cells)

    if bool(segment_only):
        grid_cells = list(final_cells)
        processed_cells = list(final_cells)
        if debug_dir is not None:
            base = os.path.splitext(os.path.basename(image_path))[0]
            grid_overlay_path = os.path.join(debug_dir, f"{base}_overlay_grid.jpg")
            draw_debug_overlays(
                oriented_rgb,
                polys_full,
                grid_overlay_path,
                grid_cells=grid_cells,
                processed_cells=processed_cells,
                ocr_polys=None,
                segment_bands=None,
                vertical_cells=None,
                exclude_masks=exclude_masks_all if exclude_masks_all else None,
            )

            segments_dir = os.path.join(debug_dir, "segments")
            try:
                os.makedirs(segments_dir, exist_ok=True)
            except Exception:
                segments_dir = None
            if segments_dir is not None:
                for i, (x0, y0, x1, y1) in enumerate(grid_cells, start=1):
                    try:
                        seg_rgb = oriented_rgb[y0:y1, x0:x1, :].copy()

                        seg_masks = []
                        for seg in final_segments:
                            if seg.get("rect") == (x0, y0, x1, y1):
                                seg_masks = seg.get("masks", [])
                                break
                        for m in seg_masks:
                            rect = m.get("rect")
                            poly = m.get("poly")
                            if rect is not None:
                                rx0, ry0, rx1, ry1 = rect
                                lx0 = max(0, int(rx0 - x0))
                                ly0 = max(0, int(ry0 - y0))
                                lx1 = min(seg_rgb.shape[1], int(rx1 - x0))
                                ly1 = min(seg_rgb.shape[0], int(ry1 - y0))
                                if lx1 > lx0 and ly1 > ly0:
                                    cv2.rectangle(
                                        seg_rgb,
                                        (lx0, ly0),
                                        (lx1 - 1, ly1 - 1),
                                        (255, 255, 255),
                                        -1,
                                    )
                            elif poly is not None:
                                pts = np.array(poly, dtype=int)
                                pts[:, 0] = pts[:, 0] - x0
                                pts[:, 1] = pts[:, 1] - y0
                                cv2.fillPoly(seg_rgb, [pts], (255, 255, 255))
                        seg_path = os.path.join(
                            segments_dir,
                            f"{base}_seg_{i:03d}_{y0}-{y1}_{x0}-{x1}.jpg",
                        )
                        cv2.imwrite(seg_path, cv2.cvtColor(seg_rgb, cv2.COLOR_RGB2BGR))
                    except Exception:
                        continue
            segments_json_path = os.path.join(debug_dir, f"{base}_segments.json")
            try:
                import json as _json

                h, w = oriented_rgb.shape[:2]
                payload = {
                    "image_width": int(w),
                    "image_height": int(h),
                    "segments": [
                        {"x0": int(x0), "y0": int(y0), "x1": int(x1), "y1": int(y1)}
                        for (x0, y0, x1, y1) in grid_cells
                    ],
                }
                with open(segments_json_path, "w", encoding="utf-8") as f:
                    _json.dump(payload, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
        merged_result = [{"rec_texts": [], "rec_polys": [], "rec_scores": []}]
        return merged_result, oriented_rgb

    merged_texts = []
    merged_scores = []
    merged_polys = []
    grid_cells = list(final_cells)
    processed_cells = []
    seg_counter = 0
    total_segments = len(grid_cells)
    bar_width = 20
    segments_dir = None
    ocred_cells = []
    if debug_dir is not None:
        segments_dir = os.path.join(debug_dir, "segments")
        try:
            os.makedirs(segments_dir, exist_ok=True)
        except Exception:
            segments_dir = None
    for x0, y0, x1, y1 in grid_cells:
        seg_counter += 1
        seg_w = max(1, x1 - x0)
        seg_h = max(1, y1 - y0)
        filled = int(bar_width * seg_counter / max(1, total_segments))
        bar = "#" * filled + "-" * (bar_width - filled)
        print(
            f"[{seg_counter:02d}/{total_segments:02d}] [{bar}] OCR 開始 | ROI x:{x0}-{x1} y:{y0}-{y1} | {seg_w}x{seg_h}"
        )
        seg_rgb = oriented_rgb[y0:y1, x0:x1, :].copy()
        if seg_rgb.size == 0:
            continue
        processed_cells.append((x0, y0, x1, y1))

        try:
            seg_masks = []
            for seg in final_segments:
                if seg.get("rect") == (x0, y0, x1, y1):
                    seg_masks = seg.get("masks", [])
                    break
            for m in seg_masks:
                rect = m.get("rect")
                poly = m.get("poly")
                if rect is not None:
                    rx0, ry0, rx1, ry1 = rect
                    lx0 = max(0, int(rx0 - x0))
                    ly0 = max(0, int(ry0 - y0))
                    lx1 = min(seg_rgb.shape[1], int(rx1 - x0))
                    ly1 = min(seg_rgb.shape[0], int(ry1 - y0))
                    if lx1 > lx0 and ly1 > ly0:
                        cv2.rectangle(
                            seg_rgb, (lx0, ly0), (lx1 - 1, ly1 - 1), (255, 255, 255), -1
                        )
                elif poly is not None:
                    pts = np.array(poly, dtype=int)
                    pts[:, 0] = pts[:, 0] - x0
                    pts[:, 1] = pts[:, 1] - y0
                    cv2.fillPoly(seg_rgb, [pts], (255, 255, 255))
        except Exception:
            pass

        if segments_dir is not None:
            try:
                base = os.path.splitext(os.path.basename(image_path))[0]
                seg_path = os.path.join(
                    segments_dir,
                    f"{base}_seg_{seg_counter:03d}_{y0}-{y1}_{x0}-{x1}.jpg",
                )
                cv2.imwrite(seg_path, cv2.cvtColor(seg_rgb, cv2.COLOR_RGB2BGR))
            except Exception:
                pass

        seg_scale = 1.0
        if max_segment_pixels is not None:
            seg_area = float(seg_w * seg_h)
            if seg_area > float(max_segment_pixels):
                seg_scale = (float(max_segment_pixels) / seg_area) ** 0.5
        if seg_scale < 1.0:
            ocr_w = max(1, int(round(seg_w * seg_scale)))
            ocr_h = max(1, int(round(seg_h * seg_scale)))
            seg_rgb_for_ocr = cv2.resize(
                seg_rgb, (ocr_w, ocr_h), interpolation=cv2.INTER_AREA
            )
        else:
            seg_rgb_for_ocr = seg_rgb
        t0 = time.perf_counter()
        _gray = cv2.cvtColor(seg_rgb_for_ocr, cv2.COLOR_RGB2GRAY)

        otsu_thresh, _ = cv2.threshold(
            _gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
        )

        conservative_thresh = max(0, otsu_thresh - 10)
        _, _bw = cv2.threshold(_gray, conservative_thresh, 255, cv2.THRESH_BINARY)
        _seg_for_ocr = cv2.cvtColor(_bw, cv2.COLOR_GRAY2RGB)

        if segments_dir is not None:
            try:
                base = os.path.splitext(os.path.basename(image_path))[0]
                binarized_path = os.path.join(
                    segments_dir,
                    f"{base}_seg_{seg_counter:03d}_{y0}-{y1}_{x0}-{x1}_binarized.jpg",
                )
                cv2.imwrite(
                    binarized_path, cv2.cvtColor(_seg_for_ocr, cv2.COLOR_RGB2BGR)
                )
            except Exception:
                pass

        seg_results = base_ocr.predict(_seg_for_ocr)
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        if not seg_results:
            filled = int(bar_width * seg_counter / max(1, total_segments))
            bar = "#" * filled + "-" * (bar_width - filled)
            print(
                f"[{seg_counter:02d}/{total_segments:02d}] [{bar}] 検出なし | {elapsed_ms} ms"
            )
            continue
        seg_dict = seg_results[0]
        seg_texts = seg_dict.get("rec_texts", [])
        seg_polys = seg_dict.get("rec_polys", [])
        seg_scores = seg_dict.get("rec_scores", [])
        filled = int(bar_width * seg_counter / max(1, total_segments))
        bar = "#" * filled + "-" * (bar_width - filled)
        print(
            f"[{seg_counter:02d}/{total_segments:02d}] [{bar}] 検出テキスト数: {len(seg_texts)} | {elapsed_ms} ms"
        )
        if seg_texts:
            ocred_cells.append((x0, y0, x1, y1))
        for t, p, s in zip(seg_texts, seg_polys, seg_scores):
            try:
                arr = np.array(p, dtype=float)

                if seg_scale < 1.0:
                    inv = 1.0 / float(seg_scale)
                    arr[:, 0] = arr[:, 0] * inv
                    arr[:, 1] = arr[:, 1] * inv
                arr[:, 0] = arr[:, 0] + x0
                arr[:, 1] = arr[:, 1] + y0
                merged_polys.append(arr.tolist())

                normalized_text = _convert_fullwidth_to_halfwidth(t)
                merged_texts.append(normalized_text)
                merged_scores.append(float(s))
            except Exception:
                continue

    merged_result = [
        {
            "rec_texts": merged_texts,
            "rec_polys": merged_polys,
            "rec_scores": merged_scores,
        }
    ]

    if debug_dir is not None:
        base = os.path.splitext(os.path.basename(image_path))[0]
        ocr_overlay_path = os.path.join(debug_dir, f"{base}_overlay_ocr.jpg")
        draw_debug_overlays(
            oriented_rgb, merged_polys, ocr_overlay_path, ocr_polys=merged_polys
        )
        grid_overlay_path = os.path.join(debug_dir, f"{base}_overlay_grid.jpg")
        segment_bands_show = None
        vertical_cells_show = None
        draw_debug_overlays(
            oriented_rgb,
            polys_full,
            grid_overlay_path,
            grid_cells=grid_cells,
            processed_cells=ocred_cells if ocred_cells else processed_cells,
            ocr_polys=merged_polys,
            segment_bands=segment_bands_show,
            vertical_cells=vertical_cells_show,
            exclude_masks=None,
        )
        merged_json_path = os.path.join(debug_dir, f"{base}_merged_ocr.json")
        try:
            import json as _json

            h, w = oriented_rgb.shape[:2]
            payload = {
                "image_width": int(w),
                "image_height": int(h),
                "rec_texts": merged_texts,
                "rec_polys": merged_polys,
                "rec_scores": merged_scores,
            }
            with open(merged_json_path, "w", encoding="utf-8") as f:
                _json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    return merged_result, oriented_rgb
