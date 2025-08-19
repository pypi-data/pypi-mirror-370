# actscene-ocr

日本語の各種書類向けに最適化した OCR ライブラリ

## インストール

```
pip install actscene-ocr
```

## 使い方

```python
from actscene_ocr import ActsceneOCR

ocr = ActsceneOCR()
result = ocr.inkan("/path/to/image.jpg")
print(result)  # {"氏名": "...", "住所": "..."}
```

## ライセンス

MIT
