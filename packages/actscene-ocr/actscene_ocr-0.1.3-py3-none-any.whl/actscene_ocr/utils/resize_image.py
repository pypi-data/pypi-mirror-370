import cv2


def resize_image_array(img_array, max_size=1250):
    """画像配列をリサイズする関数"""
    if img_array is None:
        raise ValueError("画像配列がNoneです")

    height, width = img_array.shape[:2]

    if max(height, width) <= max_size:
        return img_array

    scale = max_size / max(height, width)
    new_width = int(width * scale)
    new_height = int(height * scale)

    resized_img = cv2.resize(
        img_array, (new_width, new_height), interpolation=cv2.INTER_AREA
    )
    return resized_img
