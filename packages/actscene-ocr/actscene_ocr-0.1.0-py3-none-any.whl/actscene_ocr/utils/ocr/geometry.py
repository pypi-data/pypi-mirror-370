import numpy as np


def extract_y_intervals_from_polys(polys):
    intervals = []
    for poly in polys:
        try:
            arr = np.array(poly, dtype=float)
            ys = arr[:, 1]
            intervals.append((float(ys.min()), float(ys.max())))
        except Exception:
            continue
    return intervals


def extract_x_intervals_from_polys(polys):
    intervals = []
    for poly in polys:
        try:
            arr = np.array(poly, dtype=float)
            xs = arr[:, 0]
            intervals.append((float(xs.min()), float(xs.max())))
        except Exception:
            continue
    return intervals


def merge_intervals(intervals, min_gap=0.0):
    if not intervals:
        return []
    intervals_sorted = sorted(intervals, key=lambda x: x[0])
    merged = []
    cur_start, cur_end = intervals_sorted[0]
    for s, e in intervals_sorted[1:]:
        if s <= cur_end + min_gap:
            cur_end = max(cur_end, e)
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = s, e
    merged.append((cur_start, cur_end))
    return merged


def compute_safe_cut_lines_y(merged_intervals, image_height):
    if not merged_intervals:
        return [image_height // 2]
    lines = []
    prev_end = 0.0
    for s, e in merged_intervals:
        if s > prev_end:
            mid = (prev_end + s) / 2.0
            if 0 < mid < image_height:
                lines.append(int(round(mid)))
        prev_end = max(prev_end, e)
    if prev_end < image_height:
        mid = (prev_end + image_height) / 2.0
        if 0 < mid < image_height:
            lines.append(int(round(mid)))
    uniq = sorted(set([y for y in lines if 0 < y < image_height]))
    return uniq
