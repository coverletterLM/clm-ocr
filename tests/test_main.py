"""
Main 함수 통합 테스트
"""
import pytest
from unittest.mock import Mock, patch, mock_open
from clm_ocr.main import process_pdf, load_saved_result


def test_process_pdf_integration(mock_env_vars, tmp_path):
    """process_pdf 통합 테스트 (API 모킹)"""
    # API 응답 모킹
    mock_response = {
        'images': [
            {
                'fields': [
                    {
                        'inferText': '테스트 문서',
                        'inferConfidence': 0.99,
                        'boundingPoly': {
                            'vertices': [
                                {'x': 10, 'y': 10},
                                {'x': 100, 'y': 10},
                                {'x': 100, 'y': 30},
                                {'x': 10, 'y': 30}
                            ]
                        }
                    }
                ]
            }
        ]
    }

    # ClovaOCRClient.ocr_from_file 메서드 모킹
    with patch('clm_ocr.main.ClovaOCRClient') as mock_client_class:
        mock_client = Mock()
        mock_client.ocr_from_file.return_value = mock_response
        mock_client_class.return_value = mock_client

        # PDF 파일 생성 (더미)
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b'%PDF-1.4 dummy')

        # 실행
        result, df = process_pdf(
            str(pdf_path),
            output_formats=['json', 'text'],
            output_base=str(tmp_path / "output")
        )

        # 검증
        assert result is not None
        assert df is not None
        assert len(df) == 1
        assert df.iloc[0]['text'] == '테스트 문서'


def test_load_saved_result(mock_env_vars, tmp_path):
    """저장된 결과 로딩 테스트"""
    import json
    import pandas as pd

    # 테스트 데이터 준비
    project_dir = tmp_path / "output" / "test_project"
    project_dir.mkdir(parents=True)

    mock_result = {'images': [{'fields': [{'inferText': '로딩 테스트'}]}]}

    # JSON 파일 생성
    json_path = project_dir / "ocr_result.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(mock_result, f)

    # CSV 파일 생성
    df_test = pd.DataFrame([{'text': '로딩 테스트', 'page': 0}])
    csv_path = project_dir / "ocr_data.csv"
    df_test.to_csv(csv_path, index=False)

    # 실행
    result, df = load_saved_result(
        'test_project',
        output_base=str(tmp_path / "output")
    )

    # 검증
    assert result is not None
    assert df is not None
    assert result['images'][0]['fields'][0]['inferText'] == '로딩 테스트'