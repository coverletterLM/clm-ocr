"""
메인 실행 로직
PDF OCR 처리 워크플로우 조율
"""
import json
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import pandas as pd

from .config import API_URL, SECRET_KEY, DEFAULT_OUTPUT_FORMATS, DEFAULT_LANG, DEFAULT_ENABLE_TABLE
from .client import ClovaOCRClient, OCROutputManager
from .processor import OCRProcessor


def process_pdf(
    pdf_path: str,
    output_formats: Optional[List[str]] = None,
    output_base: str = "./output",
    project_name: Optional[str] = None,
    api_url: str = API_URL,
    secret_key: str = SECRET_KEY,
    lang: str = DEFAULT_LANG,
    enable_table: bool = DEFAULT_ENABLE_TABLE
) -> Tuple[Optional[Dict[str, Any]], Optional[pd.DataFrame]]:
    """
    PDF OCR 처리 메인 함수

    Args:
        pdf_path: 처리할 PDF 파일 경로
        output_formats: 출력 형식 리스트 ['json', 'text', 'dataframe', 'markdown', 'searchable_pdf']
        output_base: 출력 루트 디렉토리 (기본값: ./output)
        project_name: 프로젝트 폴더명 (None이면 PDF 파일명 사용)
        api_url: CLOVA OCR API URL
        secret_key: CLOVA OCR Secret Key
        lang: 언어 코드 (기본값: 'ko')
        enable_table: 테이블 인식 활성화 (기본값: False)

    Returns:
        (ocr_result, df_result) 튜플

    Example:
        >>> ocr_result, df = process_pdf('data/test.pdf')
        >>> ocr_result, df = process_pdf('data/test.pdf', project_name='프로젝트A')
        >>> ocr_result, df = process_pdf('data/test.pdf', output_formats=['text', 'dataframe'])
    """
    if output_formats is None:
        output_formats = DEFAULT_OUTPUT_FORMATS

    print("🔧 CLOVA OCR 처리 시작\n")

    # ============================================
    # 1. 출력 관리자 생성 및 디렉토리 준비
    # ============================================
    output_mgr = OCROutputManager(pdf_path, output_base, project_name)
    output_mgr.setup_directories()

    # ============================================
    # 2. OCR 클라이언트 생성 및 실행
    # ============================================
    client = ClovaOCRClient(api_url, secret_key)

    try:
        # OCR 실행
        result = client.ocr_from_file(pdf_path, lang=lang, enable_table=enable_table)

        # 요약 출력
        OCRProcessor.print_summary(result)

        # DataFrame 변환
        df = OCRProcessor.to_dataframe(result)

        # ============================================
        # 3. 결과 저장
        # ============================================
        print(f"\n💾 결과 저장 중...")

        # JSON 저장
        if 'json' in output_formats:
            json_path = output_mgr.get_path('ocr_result.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"  ✅ JSON: {json_path}")

        # 텍스트 저장
        if 'text' in output_formats:
            full_text = OCRProcessor.to_text(result)
            txt_path = output_mgr.get_path('extracted_text.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            print(f"  ✅ 텍스트: {txt_path}")

        # DataFrame CSV 저장
        if 'dataframe' in output_formats:
            csv_path = output_mgr.get_path('ocr_data.csv')
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"  ✅ DataFrame: {csv_path}")

        # Markdown 저장
        if 'markdown' in output_formats:
            markdown = OCRProcessor.to_markdown(result, include_confidence=False)
            md_path = output_mgr.get_path('document.md')
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"  ✅ Markdown: {md_path}")

        # Searchable PDF 생성
        if 'searchable_pdf' in output_formats:
            pdf_out_path = output_mgr.get_path('searchable.pdf')
            OCRProcessor.to_searchable_pdf(pdf_path, result, str(pdf_out_path))

        # 테이블 저장 (enable_table=True일 때만)
        if enable_table and 'tables' in output_formats:
            tables = OCRProcessor.extract_tables(result)
            for table_info in tables:
                table_filename = f"page{table_info['page']}_table{table_info['table_idx']}.csv"
                table_path = output_mgr.get_path(table_filename)
                table_info['dataframe'].to_csv(table_path, index=False, encoding='utf-8-sig')
                print(f"  ✅ 테이블: {table_path}")

        print(f"\n✨ 모든 결과가 저장되었습니다: {output_mgr.project_dir}")

        return result, df

    except Exception as e:
        print(f"❌ 처리 실패: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def load_saved_result(
    project_name: str,
    output_base: str = "./output"
) -> Tuple[Optional[Dict], Optional[pd.DataFrame]]:
    """
    저장된 OCR 결과 불러오기

    Args:
        project_name: 프로젝트 폴더명 (예: 'test2' 또는 '자소서_분석_v1')
        output_base: 출력 루트 디렉토리 (기본값: ./output)

    Returns:
        (ocr_result, df_result) 튜플

    Example:
        >>> ocr_result, df = load_saved_result('test2')
        >>> ocr_result, df = load_saved_result('프로젝트A', output_base='./my_output')
    """
    project_dir = Path(output_base) / project_name

    # JSON 불러오기
    json_path = project_dir / 'ocr_result.json'
    if not json_path.exists():
        print(f"❌ {json_path} 파일이 없습니다")
        return None, None

    with open(json_path, 'r', encoding='utf-8') as f:
        ocr_result = json.load(f)

    # CSV 불러오기
    csv_path = project_dir / 'ocr_data.csv'
    if csv_path.exists():
        df_result = pd.read_csv(csv_path)
    else:
        print(f"⚠️ {csv_path} 파일이 없어 DataFrame을 재생성합니다")
        df_result = OCRProcessor.to_dataframe(ocr_result)

    print(f"✅ 결과 로딩 완료: {project_dir}")
    return ocr_result, df_result
