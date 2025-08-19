import numpy as np
import cv2
from PIL import Image
from ..resize_image import resize_image_array


def correct_orientation(image, max_size=1000000, orientation_ocr=None):
    """画像の向きを補正する（小さいサイズで向き判定用OCRを実行）"""
    try:
        if isinstance(image, Image.Image):
            image_array = np.array(image)
        else:
            image_array = image

        if len(image_array.shape) == 2:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)

        resized_image = resize_image_array(image_array, max_size=max_size)

        orientation_result = orientation_ocr.predict(resized_image)

        angle = 0
        if orientation_result and len(orientation_result) > 0:
            doc_preprocessor_res = orientation_result[0].get("doc_preprocessor_res", {})
            if hasattr(doc_preprocessor_res, "__getitem__"):
                try:
                    detected_angle = doc_preprocessor_res["angle"]
                    if detected_angle != -1:
                        angle = detected_angle
                except (KeyError, TypeError):
                    pass

        if angle != 0:
            if isinstance(image, Image.Image):
                rotated_image = image.rotate(angle, expand=True)
            else:
                height, width = image_array.shape[:2]
                center = (width // 2, height // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated_image_np = cv2.warpAffine(
                    image_array, rotation_matrix, (width, height)
                )
                rotated_image = Image.fromarray(rotated_image_np)
        else:
            rotated_image = (
                image
                if isinstance(image, Image.Image)
                else Image.fromarray(image_array)
            )

        return rotated_image

    except Exception as e:
        print(f"向き補正中にエラーが発生しました: {e}")
        return image if isinstance(image, Image.Image) else Image.fromarray(image)
