"""
설정 관리 모듈
환경 변수 및 프로젝트 설정
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드 (프로젝트 루트에서)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# ============================================
# API 설정
# ============================================
API_URL = os.getenv('CLOVA_OCR_API_URL')
SECRET_KEY = os.getenv('CLOVA_OCR_SECRET_KEY')

# 환경 변수 필수 체크
if not API_URL:
    raise EnvironmentError(
        "환경 변수 'CLOVA_OCR_API_URL'이 설정되지 않았습니다.\n"
        ".env 파일을 생성하고 API URL을 설정해주세요."
    )

if not SECRET_KEY:
    raise EnvironmentError(
        "환경 변수 'CLOVA_OCR_SECRET_KEY'가 설정되지 않았습니다.\n"
        ".env 파일을 생성하고 Secret Key를 설정해주세요."
    )

# ============================================
# 경로 설정
# ============================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'output'

# ============================================
# OCR 설정
# ============================================
DEFAULT_LANG = 'ko'
DEFAULT_TIMEOUT = 30
DEFAULT_ENABLE_TABLE = False

# ============================================
# 출력 설정
# ============================================
DEFAULT_OUTPUT_FORMATS = ['json', 'text', 'dataframe']
