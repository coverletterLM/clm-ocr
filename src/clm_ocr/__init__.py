"""
CLOVA OCR PDF Processor
NAVER CLOVA OCR API를 사용한 PDF 텍스트 추출 라이브러리
"""

__version__ = "0.1.0"
__author__ = "chaewonjeong"

from .main import process_pdf, load_saved_result
from .processor import OCRProcessor
from .client import ClovaOCRClient, OCROutputManager

__all__ = [
    'process_pdf',
    'load_saved_result',
    'OCRProcessor',
    'ClovaOCRClient',
    'OCROutputManager',
]
