# 实时 OCR 集成测试
import sys
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='ch')
result = ocr.ocr('docs/arxiv-research-notes.md', cls=True)  # 测试一下是否能跑

print("✅ PaddleOCR 成功初始化")
for line in result[0] if result else []:
    print(f"  - {line}")
