import cv2
import numpy as np
from PIL import Image


def order_points(pts):
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect


def detect_document_edges(image: np.ndarray, debug_dir: str = None) -> np.ndarray:
    # 元の画像サイズで処理
    image_small = image.copy()
    gray = cv2.cvtColor(image_small, cv2.COLOR_BGR2GRAY)

    # 平滑化 → Canny → クロージング
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None

    # 最外側の大きな輪郭を対象
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    h, w = gray.shape[:2]
    min_area = float(h * w) * 0.02

    for c in cnts:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        # 折れや突起を無視するために凸包をとる
        hull = cv2.convexHull(c)
        rect = cv2.minAreaRect(hull)  # ((cx,cy),(rw,rh),angle)
        (cx, cy), (rw, rh), angle = rect
        if rw < 20 or rh < 20:
            continue
        # 矩形を内側に少し縮めて外縁の色ムラや折れを削る
        shrink_px = max(4.0, 0.02 * min(rw, rh))
        new_w = max(10.0, rw - 2.0 * shrink_px)
        new_h = max(10.0, rh - 2.0 * shrink_px)
        rect_shrunk = ((cx, cy), (new_w, new_h), angle)
        box = cv2.boxPoints(rect_shrunk)
        pts = order_points(box.astype(np.float32))
        return pts

    return None


def perspective_transform(image: np.ndarray, points: np.ndarray) -> np.ndarray:
    (tl, tr, br, bl) = points
    wA = np.linalg.norm(br - bl)
    wB = np.linalg.norm(tr - tl)
    hA = np.linalg.norm(tr - br)
    hB = np.linalg.norm(tl - bl)
    maxWidth = int(max(wA, wB))
    maxHeight = int(max(hA, hB))
    dst = np.array(
        [[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]],
        dtype="float32",
    )
    M = cv2.getPerspectiveTransform(points, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped


def deskew_image(bgr_image: np.ndarray, max_correction_deg: float = 7.5) -> np.ndarray:
    # 軽いデスキューで文書内の文字が水平・直角になるように補正
    try:
        gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        edges = cv2.Canny(gray, 50, 150)
        h, w = gray.shape[:2]
        min_len = max(10, int(0.3 * max(w, h)))
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180, threshold=120, minLineLength=min_len, maxLineGap=20
        )
        if lines is None or len(lines) == 0:
            return bgr_image
        angles: list[float] = []
        for l in lines:
            x1, y1, x2, y2 = map(int, l[0])
            angle = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))  # [-180, 180]
            # 90度周期で折り畳み、[-45, 45]に正規化
            norm = ((angle + 90.0) % 180.0) - 90.0
            if norm > 45.0:
                norm -= 90.0
            elif norm < -45.0:
                norm += 90.0
            # 水平成分に近い線だけ採用
            if abs(norm) <= 20.0:
                angles.append(norm)
        if not angles:
            return bgr_image
        skew = float(np.median(angles))
        # 補正角は過大にならないようにクリップ
        if skew > max_correction_deg:
            skew = max_correction_deg
        elif skew < -max_correction_deg:
            skew = -max_correction_deg
        if abs(skew) < 0.3:
            return bgr_image
        center = (w * 0.5, h * 0.5)
        M = cv2.getRotationMatrix2D(center, -skew, 1.0)
        rot = cv2.warpAffine(
            bgr_image,
            M,
            (w, h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )
        return rot
    except Exception:
        return bgr_image


def scan_document(pil_image: Image.Image, debug_dir: str = None) -> Image.Image:
    image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    points = detect_document_edges(image, debug_dir)
    if points is None:
        print("書類らしき四角形が見つかりませんでした")
        return pil_image
    warped = perspective_transform(image, points)
    # 文字列が水平・直角になるように軽く回転補正
    warped = deskew_image(warped)
    warped_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
    return Image.fromarray(warped_rgb)
