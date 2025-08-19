import cv2
import numpy as np
from PIL import Image


def order_points(pts):
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def detect_document_edges(
    image: np.ndarray,
    debug_dir: str = None,
    debug_basename: str = None,
) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    h, w = gray.shape[:2]
    min_area = float(h * w) * 0.02

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    quad = None
    for c in contours:
        if cv2.contourArea(c) < min_area:
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            quad = approx.reshape(4, 2).astype(np.float32)
            break

    if quad is None:
        return None

    pts = order_points(quad)

    if debug_dir:
        import os

        os.makedirs(debug_dir, exist_ok=True)
        base = (debug_basename or "document").strip()
        try:
            cv2.imwrite(os.path.join(debug_dir, f"{base}_edges.jpg"), edges)
            dbg = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            q = pts.astype(int)
            cv2.polylines(dbg, [q], True, (0, 0, 255), 2)
            cv2.imwrite(os.path.join(debug_dir, f"{base}_quad.jpg"), dbg)
        except Exception:
            pass

    return pts


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
    try:
        gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # 黒い線のみを検出するための二値化処理
        dark_mask = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # エッジ検出を黒い線のみに適用
        edges = cv2.Canny(dark_mask, 50, 150)
        h, w = gray.shape[:2]
        min_len = max(10, int(0.5 * max(w, h)))
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180, threshold=120, minLineLength=min_len, maxLineGap=20
        )
        if lines is None or len(lines) == 0:
            return bgr_image
        angles: list[float] = []
        for l in lines:
            x1, y1, x2, y2 = map(int, l[0])
            angle = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            norm = ((angle + 90.0) % 180.0) - 90.0
            if norm > 45.0:
                norm -= 90.0
            elif norm < -45.0:
                norm += 90.0
            if abs(norm) <= 20.0:
                angles.append(norm)
        if not angles:
            return bgr_image
        skew = float(np.median(angles))
        skew = max(-max_correction_deg, min(max_correction_deg, skew))
        print(f"Deskew - Detected {len(angles)} lines, median skew: {skew:.2f}°")
        print(f"Deskew - Skew range: {min(angles):.2f}° to {max(angles):.2f}°")
        if abs(skew) < 0.3:
            return bgr_image
        center = (w * 0.5, h * 0.5)
        M = cv2.getRotationMatrix2D(center, -skew, 1.0)
        print(f"Deskew - Applying skew correction: {skew:.2f}°")
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
    warped_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
    return Image.fromarray(warped_rgb)
