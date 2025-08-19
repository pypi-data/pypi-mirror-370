import os
import tempfile
from typing import Dict, Optional, Union

import numpy as np
from PIL import Image
from paddleocr import PaddleOCR

from .utils.ocr import run_ocr_pipeline_segmented
from .utils.ocr.extractors import (
    extract_values_generic,
    extract_values_shaken_kiroku,
    extract_values_shaken,
    extract_values_jouto,
    extract_values_recycle,
    extract_values_jibaiseki,
    extract_values_inkan,
)


ImageInput = Union[str, np.ndarray, Image.Image, object]


class ActsceneOCR:
    def __init__(self) -> None:
        self.base_ocr = PaddleOCR(
            lang="japan",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
        self.orientation_ocr = PaddleOCR(
            lang="japan",
            use_doc_orientation_classify=True,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )

    def shaken_kiroku(
        self,
        image: ImageInput,
        *,
        max_segment_pixels: int = 1_000_000,
        debug_dir: Optional[str] = None,
        binarize: bool = False,
        blur_sigma: float = 0.0,
        segment_only: bool = False,
    ) -> Dict[str, str]:
        image_path, temp_path = self._ensure_image_path(image)
        try:
            ocr_results, _ = run_ocr_pipeline_segmented(
                image_path,
                self.base_ocr,
                segment_max_height=None,
                orientation_detect_size=600,
                detect_size=1400,
                debug_dir=debug_dir,
                max_segment_pixels=max_segment_pixels,
                orientation_ocr=self.orientation_ocr,
                base_ocr=self.base_ocr,
                binarize=binarize,
                blur_sigma=blur_sigma,
                segment_only=segment_only,
            )

            keywords = [
                "所有者の氏名又は名称",
                "所有者の住所",
                "自動車登録番号又は車両番号",
                "初度登録年月",
                "有効期限の満了する日",
                "車台番号",
            ]
            extracted = extract_values_shaken_kiroku(
                ocr_results, keywords, y_tolerance=20
            )
            return {
                "所有者の氏名又は名称": extracted.get("所有者の氏名又は名称", {}).get(
                    "value", ""
                ),
                "所有者の住所": extracted.get("所有者の住所", {}).get("value", ""),
                "自動車登録番号又は車両番号": extracted.get(
                    "自動車登録番号又は車両番号", {}
                ).get("value", ""),
                "初度登録年月": extracted.get("初度登録年月", {}).get("value", ""),
                "有効期限の満了する日": extracted.get("有効期限の満了する日", {}).get(
                    "value", ""
                ),
                "車台番号": extracted.get("車台番号", {}).get("value", ""),
            }
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def shaken(
        self,
        image: ImageInput,
        *,
        max_segment_pixels: int = 1_000_000,
        debug_dir: Optional[str] = None,
        segment_only: bool = False,
    ) -> Dict[str, str]:
        image_path, temp_path = self._ensure_image_path(image)
        try:
            ocr_results, _ = run_ocr_pipeline_segmented(
                image_path,
                self.base_ocr,
                segment_max_height=None,
                orientation_detect_size=600,
                detect_size=1400,
                debug_dir=debug_dir,
                max_segment_pixels=max_segment_pixels,
                orientation_ocr=self.orientation_ocr,
                base_ocr=self.base_ocr,
                segment_only=segment_only,
            )

            extracted = extract_values_shaken(ocr_results)
            return {
                "使用者の氏名又は名称": extracted.get("使用者の氏名又は名称", {}).get(
                    "value", ""
                ),
                "自動車登録番号又は車両番号": extracted.get(
                    "自動車登録番号又は車両番号", {}
                ).get("value", ""),
                "初度登録年月": extracted.get("初度登録年月", {}).get("value", ""),
                "車台番号": extracted.get("車台番号", {}).get("value", ""),
            }
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def recycle(
        self,
        image: ImageInput,
        *,
        max_segment_pixels: int = 1_000_000,
        debug_dir: Optional[str] = None,
        segment_only: bool = False,
    ) -> Dict[str, str]:
        image_path, temp_path = self._ensure_image_path(image)
        try:
            ocr_results, _ = run_ocr_pipeline_segmented(
                image_path,
                self.base_ocr,
                segment_max_height=None,
                orientation_detect_size=600,
                detect_size=1400,
                debug_dir=debug_dir,
                max_segment_pixels=max_segment_pixels,
                orientation_ocr=self.orientation_ocr,
                base_ocr=self.base_ocr,
                segment_only=segment_only,
            )

            extracted = extract_values_recycle(ocr_results)
            return {
                "預託金額合計": extracted.get("預託金額合計", {}).get("value", ""),
                "車台番号": extracted.get("車台番号", {}).get("value", ""),
            }
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def inkan(
        self,
        image: ImageInput,
        *,
        max_segment_pixels: int = 1_000_000,
        debug_dir: Optional[str] = None,
        segment_only: bool = False,
    ) -> Dict[str, str]:
        image_path, temp_path = self._ensure_image_path(image)
        try:
            ocr_results, _ = run_ocr_pipeline_segmented(
                image_path,
                self.base_ocr,
                segment_max_height=None,
                orientation_detect_size=600,
                detect_size=1400,
                debug_dir=debug_dir,
                max_segment_pixels=max_segment_pixels,
                orientation_ocr=self.orientation_ocr,
                base_ocr=self.base_ocr,
                segment_only=segment_only,
            )
            keywords = ["本店", "取締役"]
            extracted = extract_values_generic(ocr_results, keywords, y_tolerance=20)
            return {
                "本店": extracted.get("本店", {}).get("value", ""),
                "取締役": extracted.get("取締役", {}).get("value", ""),
            }
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def jouto(
        self,
        image: ImageInput,
        *,
        max_segment_pixels: int = 1_000_000,
        debug_dir: Optional[str] = None,
        segment_only: bool = False,
    ) -> Dict[str, str]:
        image_path, temp_path = self._ensure_image_path(image)
        try:
            ocr_results, _ = run_ocr_pipeline_segmented(
                image_path,
                self.base_ocr,
                segment_max_height=None,
                orientation_detect_size=600,
                detect_size=1400,
                debug_dir=debug_dir,
                max_segment_pixels=max_segment_pixels,
                orientation_ocr=self.orientation_ocr,
                base_ocr=self.base_ocr,
                segment_only=segment_only,
            )
            extracted = extract_values_jouto(ocr_results)
            label_key = "譲渡人及び譲受人の氏名又は名称及び住所"
            return {
                label_key: extracted.get(label_key, {}).get("value", ""),
            }
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def jibaiseki(
        self,
        image: ImageInput,
        *,
        max_segment_pixels: int = 1_000_000,
        debug_dir: Optional[str] = None,
        segment_only: bool = False,
    ) -> Dict[str, str]:
        image_path, temp_path = self._ensure_image_path(image)
        try:
            ocr_results, _ = run_ocr_pipeline_segmented(
                image_path,
                self.base_ocr,
                segment_max_height=None,
                orientation_detect_size=600,
                detect_size=1400,
                debug_dir=debug_dir,
                max_segment_pixels=max_segment_pixels,
                orientation_ocr=self.orientation_ocr,
                base_ocr=self.base_ocr,
                segment_only=segment_only,
            )
            extracted = extract_values_jibaiseki(ocr_results)
            return {
                "車台番号": extracted.get("車台番号", {}).get("value", ""),
                "保険期間至": extracted.get("保険期間至", {}).get("value", ""),
            }
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def inkan(
        self,
        image: ImageInput,
        *,
        max_segment_pixels: int = 1_000_000,
        debug_dir: Optional[str] = None,
        segment_only: bool = False,
    ) -> Dict[str, str]:
        image_path, temp_path = self._ensure_image_path(image)
        try:
            ocr_results, _ = run_ocr_pipeline_segmented(
                image_path,
                self.base_ocr,
                segment_max_height=None,
                orientation_detect_size=600,
                detect_size=1400,
                debug_dir=debug_dir,
                max_segment_pixels=max_segment_pixels,
                orientation_ocr=self.orientation_ocr,
                base_ocr=self.base_ocr,
                segment_only=segment_only,
            )
            extracted = extract_values_inkan(ocr_results)
            return {
                "氏名": extracted.get("氏名", {}).get("value", ""),
                "住所": extracted.get("住所", {}).get("value", ""),
            }
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def _ensure_image_path(self, image: ImageInput) -> tuple[str, Optional[str]]:
        if isinstance(image, str):
            return image, None
        fd, temp_path = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        if isinstance(image, Image.Image):
            image.save(temp_path, format="JPEG")
            return temp_path, temp_path
        elif isinstance(image, np.ndarray):
            pil = Image.fromarray(image)
            pil.save(temp_path, format="JPEG")
            return temp_path, temp_path
        else:
            raise TypeError(
                "image はパス、numpy配列、またはPIL.Imageで指定してください"
            )
