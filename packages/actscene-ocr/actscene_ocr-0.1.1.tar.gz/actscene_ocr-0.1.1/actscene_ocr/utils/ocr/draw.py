import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont


def draw_debug_overlays(
    oriented_rgb,
    polys_full,
    out_path,
    grid_cells=None,
    processed_cells=None,
    ocr_polys=None,
    segment_bands=None,
    vertical_cells=None,
    exclude_masks=None,
):
    try:
        img_bgr = cv2.cvtColor(oriented_rgb, cv2.COLOR_RGB2BGR)

        if segment_bands:
            overlay = img_bgr.copy()
            alphas = []
            for seg in segment_bands:
                try:
                    x0, y0, x1, y1 = seg.get("rect", (0, 0, 0, 0))
                    color = seg.get("color", (0, 128, 255))
                    alphas.append(float(seg.get("alpha", 0.22)))
                    cv2.rectangle(
                        overlay,
                        (int(x0), int(y0)),
                        (int(x1) - 1, int(y1) - 1),
                        color,
                        thickness=-1,
                    )
                except Exception:
                    continue
            alpha = float(np.clip(np.mean(alphas) if alphas else 0.22, 0.1, 0.35))
            cv2.addWeighted(overlay, alpha, img_bgr, 1 - alpha, 0, dst=img_bgr)
        if grid_cells:
            overlay = img_bgr.copy()
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
            for i, (x0, y0, x1, y1) in enumerate(grid_cells):
                color = palette[i % len(palette)]
                cv2.rectangle(
                    overlay,
                    (int(x0), int(y0)),
                    (int(x1) - 1, int(y1) - 1),
                    color,
                    thickness=-1,
                )
            alpha = 0.25
            cv2.addWeighted(overlay, alpha, img_bgr, 1 - alpha, 0, dst=img_bgr)

        if vertical_cells:
            for x0, y0, x1, y1 in vertical_cells:
                cv2.rectangle(
                    img_bgr,
                    (int(x0), int(y0)),
                    (int(x1) - 1, int(y1) - 1),
                    (255, 255, 0),
                    2,
                )

        if exclude_masks:
            overlay = img_bgr.copy()
            alphas = []
            for m in exclude_masks:
                try:
                    poly = m.get("poly")
                    rect = m.get("rect")
                    color = m.get("color", (0, 0, 255))
                    alphas.append(float(m.get("alpha", 0.35)))
                    if poly is not None:
                        pts = np.array(poly, dtype=int)
                        cv2.fillPoly(overlay, [pts], color)
                    elif rect is not None:
                        x0, y0, x1, y1 = rect
                        cv2.rectangle(
                            overlay,
                            (int(x0), int(y0)),
                            (int(x1) - 1, int(y1) - 1),
                            color,
                            thickness=-1,
                        )
                    else:
                        continue
                except Exception:
                    continue
            alpha = float(np.clip(np.mean(alphas) if alphas else 0.3, 0.15, 0.4))
            cv2.addWeighted(overlay, alpha, img_bgr, 1 - alpha, 0, dst=img_bgr)
        for poly in polys_full:
            try:
                pts = np.array(poly, dtype=int)
                cv2.polylines(
                    img_bgr, [pts], isClosed=True, color=(0, 255, 0), thickness=2
                )
            except Exception:
                continue
        if ocr_polys:
            for poly in ocr_polys:
                try:
                    pts = np.array(poly, dtype=int)
                    cv2.polylines(
                        img_bgr, [pts], isClosed=True, color=(0, 0, 255), thickness=2
                    )
                except Exception:
                    continue
        if grid_cells:
            for x0, y0, x1, y1 in grid_cells:
                cv2.rectangle(
                    img_bgr,
                    (int(x0), int(y0)),
                    (int(x1) - 1, int(y1) - 1),
                    (0, 255, 255),
                    2,
                )
        if processed_cells:
            for x0, y0, x1, y1 in processed_cells:
                cv2.rectangle(
                    img_bgr,
                    (int(x0), int(y0)),
                    (int(x1) - 1, int(y1) - 1),
                    (0, 200, 0),
                    2,
                )
        cv2.imwrite(out_path, img_bgr)
    except Exception:
        pass


def draw_ocr_boxes_with_text(oriented_rgb, polys, texts, out_path):
    try:
        img_bgr = cv2.cvtColor(oriented_rgb, cv2.COLOR_RGB2BGR)
        for poly in polys:
            try:
                pts = np.array(poly, dtype=int)
                cv2.polylines(
                    img_bgr, [pts], isClosed=True, color=(255, 0, 0), thickness=2
                )
            except Exception:
                continue
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(pil_img)

        def _candidate_font_paths():
            return [
                "/Library/Fonts/NotoSansCJKjp-Regular.otf",
                "/Library/Fonts/NotoSansCJKjp-Medium.otf",
                "/System/Library/Fonts/ヒラギノ角ゴ ProN W6.otf",
                "/System/Library/Fonts/ヒラギノ角ゴ ProN W3.otf",
                "/System/Library/Fonts/Hiragino Sans W6.ttc",
                "/System/Library/Fonts/Hiragino Sans W5.ttc",
                "/System/Library/Fonts/Language Support/NotoSansCJK.ttc",
            ]

        def _load_fonts(size):
            fonts = []
            for path in _candidate_font_paths():
                try:
                    fonts.append(ImageFont.truetype(path, size))
                except Exception:
                    continue
            if not fonts:
                fonts = [ImageFont.load_default()]
            return fonts

        base_font_size = 32
        base_fonts = _load_fonts(base_font_size)
        pad = 4
        for poly, text in zip(polys, texts):
            try:
                pts = np.array(poly, dtype=int)
                x = int(np.min(pts[:, 0]))
                y_top = int(np.min(pts[:, 1]))
                y_bottom = int(np.max(pts[:, 1]))
                box_h = max(1, y_bottom - y_top)
                label = str(text)
                dyn_size = max(14, min(base_font_size, int(box_h * 0.9)))
                fonts = (
                    base_fonts if dyn_size == base_font_size else _load_fonts(dyn_size)
                )

                def measure_with_fallback(text_str, font_list):
                    total_w = 0
                    max_h = 0
                    glyphs = []
                    for ch in text_str:
                        chosen = None
                        w = h = None
                        for fnt in font_list:
                            try:
                                tb = draw.textbbox((0, 0), ch, font=fnt)
                                w = tb[2] - tb[0]
                                h = tb[3] - tb[1]
                            except Exception:
                                try:
                                    bb = fnt.getbbox(ch)
                                    w = bb[2] - bb[0]
                                    h = bb[3] - bb[1]
                                except Exception:
                                    continue
                            if w is not None and h is not None:
                                chosen = fnt
                                break
                        if chosen is None:
                            chosen = ImageFont.load_default()
                            tb = draw.textbbox((0, 0), ch, font=chosen)
                            w = tb[2] - tb[0]
                            h = tb[3] - tb[1]
                        glyphs.append((ch, chosen, w))
                        total_w += w
                        max_h = max(max_h, h)
                    return total_w, max_h, glyphs

                tw, th, glyphs = measure_with_fallback(label, fonts)
                img_w, img_h = pil_img.size
                ix = max(0, min(img_w - 1, x + pad))
                iy = max(0, min(img_h - 1, y_top + pad))
                fits_inside = (ix + tw + pad <= img_w - 1) and (
                    iy + th + pad <= img_h - 1
                )
                if fits_inside:
                    draw.rectangle(
                        [ix - pad, iy - pad, ix + tw + pad, iy + th + pad],
                        fill=(255, 255, 255),
                    )
                    cx = ix
                    for ch, fnt, cw in glyphs:
                        draw.text((cx, iy), ch, font=fnt, fill=(0, 0, 0))
                        cx += cw
                else:
                    x0 = max(0, x)
                    y0 = y_top - th - 2 * pad
                    if y0 < 0:
                        y0 = y_bottom + 2
                    x0 = min(x0, max(0, img_w - (tw + 2 * pad)))
                    y0 = min(y0, max(0, img_h - (th + 2 * pad)))
                    x1 = min(img_w - 1, x0 + tw + 2 * pad)
                    y1 = min(img_h - 1, y0 + th + 2 * pad)
                    draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 255))
                    cx = x0 + pad
                    for ch, fnt, cw in glyphs:
                        draw.text((cx, y0 + pad), ch, font=fnt, fill=(0, 0, 0))
                        cx += cw
            except Exception:
                continue
        out_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        cv2.imwrite(out_path, out_bgr)
    except Exception:
        pass
