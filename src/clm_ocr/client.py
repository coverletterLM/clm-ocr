"""
OCR 클라이언트 및 출력 관리
API 통신 + 파일 시스템 관리
"""
import requests
import uuid
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional

from .config import API_URL, SECRET_KEY, DEFAULT_TIMEOUT


class ClovaOCRClient:
    """CLOVA OCR API 클라이언트"""

    def __init__(self, api_url: str = API_URL, secret_key: str = SECRET_KEY):
        """
        Args:
            api_url: CLOVA OCR API URL
            secret_key: CLOVA OCR Secret Key
        """
        self.api_url = api_url
        self.secret_key = secret_key
        self.cache = {}

    def ocr_from_file(
        self,
        file_path: str,
        lang: str = 'ko',
        enable_table: bool = False
    ) -> Dict[str, Any]:
        """
        파일에서 OCR 수행

        Args:
            file_path: PDF/이미지 파일 경로
            lang: 언어 코드 (기본값: 'ko')
            enable_table: 테이블 인식 활성화

        Returns:
            OCR API 응답 (JSON)

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            requests.exceptions.RequestException: API 요청 실패 시
        """
        # 캐시 확인
        cache_key = f"{file_path}_{lang}_{enable_table}"
        if cache_key in self.cache:
            print("📦 캐시된 결과 반환")
            return self.cache[cache_key]

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        file_ext = file_path.suffix.lower().replace('.', '')

        request_json = {
            'images': [{
                'format': file_ext if file_ext != 'jpeg' else 'jpg',
                'name': file_path.stem
            }],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000)),
            'lang': lang,
            'enableTableDetection': enable_table
        }

        payload = {'message': json.dumps(request_json).encode('UTF-8')}
        files = [('file', open(file_path, 'rb'))]
        headers = {'X-OCR-SECRET': self.secret_key}

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                data=payload,
                files=files,
                timeout=DEFAULT_TIMEOUT
            )

            response.raise_for_status()
            result = response.json()

            # 캐시 저장
            self.cache[cache_key] = result
            print("✅ OCR 완료!")
            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ API 요청 실패: {e}")
            raise
        finally:
            files[0][1].close()


class OCROutputManager:
    """OCR 결과 저장 경로 관리"""

    def __init__(
        self,
        source_pdf: str,
        output_base: str = "./output",
        project_name: Optional[str] = None
    ):
        """
        Args:
            source_pdf: 원본 PDF 파일 경로
            output_base: 출력 루트 디렉토리 (기본값: ./output)
            project_name: 프로젝트 폴더명 (기본값: None, PDF 파일명 사용)
        """
        self.source_pdf = Path(source_pdf)
        self.pdf_name = self.source_pdf.stem
        self.output_base = Path(output_base)

        # 프로젝트명 결정: 사용자 지정 > PDF 파일명
        self.project_name = project_name or self.pdf_name

        # PDF별 전용 디렉토리
        self.project_dir = self.output_base / self.project_name

    def setup_directories(self) -> None:
        """필요한 디렉토리 생성"""
        self.project_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 출력 디렉토리: {self.project_dir}")

    def get_path(self, filename: str) -> Path:
        """
        저장 경로 반환

        Args:
            filename: 저장할 파일명 (예: 'ocr_result.json')

        Returns:
            전체 경로 (예: ./output/test2/ocr_result.json)
        """
        return self.project_dir / filename
