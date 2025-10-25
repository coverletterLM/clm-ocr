"""
Config 모듈 테스트
"""
import pytest
import os


def test_config_loads_env_vars(mock_env_vars):
    """환경 변수가 올바르게 로드되는지 테스트"""
    # conftest의 mock_env_vars 픽스처가 환경 변수 설정
    # config 모듈을 import할 때 환경 변수가 이미 설정되어 있어야 함

    # config는 import 시점에 환경 변수를 체크하므로
    # 테스트 전에 환경 변수가 설정되어야 함
    from clm_ocr import config

    assert config.API_URL == 'https://mock-api.example.com'
    assert config.SECRET_KEY == 'mock_secret_key_12345'


def test_config_missing_api_url(monkeypatch):
    """API_URL이 없을 때 에러 발생 테스트"""
    # 환경 변수 제거
    monkeypatch.delenv('CLOVA_OCR_API_URL', raising=False)
    monkeypatch.setenv('CLOVA_OCR_SECRET_KEY', 'test_key')

    with pytest.raises(EnvironmentError, match="CLOVA_OCR_API_URL"):
        # config 모듈을 다시 로드해야 환경 변수 체크가 발생
        import importlib
        from clm_ocr import config
        importlib.reload(config)