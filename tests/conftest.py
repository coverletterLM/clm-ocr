"""
Pytest 설정 및 공통 픽스처
"""
import os
import pytest
from pathlib import Path


@pytest.fixture
def mock_env_vars(monkeypatch):
    """환경 변수 모킹"""
    monkeypatch.setenv('CLOVA_OCR_API_URL', 'https://mock-api.example.com')
    monkeypatch.setenv('CLOVA_OCR_SECRET_KEY', 'mock_secret_key_12345')


@pytest.fixture
def sample_pdf_path(tmp_path):
    """테스트용 PDF 경로 (실제 파일 없음, 모킹용)"""
    return tmp_path / "test.pdf"


@pytest.fixture
def output_dir(tmp_path):
    """테스트용 출력 디렉토리"""
    output = tmp_path / "output"
    output.mkdir()
    return output