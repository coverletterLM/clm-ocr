"""
OCRProcessor 테스트
"""
import pytest
from clm_ocr.processor import OCRProcessor


def test_to_text_basic(mock_env_vars):
    """OCR 결과를 텍스트로 변환 테스트"""
    mock_result = {
        'images': [
            {
                'fields': [
                    {'inferText': '안녕하세요'},
                    {'inferText': '테스트입니다'}
                ]
            }
        ]
    }

    text = OCRProcessor.to_text(mock_result)

    assert '안녕하세요' in text
    assert '테스트입니다' in text


def test_to_dataframe(mock_env_vars):
    """OCR 결과를 DataFrame으로 변환 테스트"""
    mock_result = {
        'images': [
            {
                'fields': [
                    {
                        'inferText': '테스트',
                        'inferConfidence': 0.95,
                        'boundingPoly': {
                            'vertices': [
                                {'x': 0, 'y': 0},
                                {'x': 100, 'y': 0},
                                {'x': 100, 'y': 50},
                                {'x': 0, 'y': 50}
                            ]
                        }
                    }
                ]
            }
        ]
    }

    df = OCRProcessor.to_dataframe(mock_result)

    assert len(df) == 1
    assert df.iloc[0]['text'] == '테스트'
    assert df.iloc[0]['confidence'] == 0.95
    assert df.iloc[0]['page'] == 0