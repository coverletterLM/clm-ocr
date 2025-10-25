"""
고급 사용 예제
개별 클래스를 직접 사용하는 방법
"""
from clm_ocr import ClovaOCRClient, OCRProcessor, OCROutputManager
from clm_ocr.config import API_URL, SECRET_KEY


def example_direct_api_call():
    """API 직접 호출"""
    print("=" * 50)
    print("고급 예제: API 직접 호출")
    print("=" * 50)

    # 1. 클라이언트 생성
    client = ClovaOCRClient(API_URL, SECRET_KEY)

    # 2. OCR 실행
    result = client.ocr_from_file(
        'data/test.pdf',
        lang='ko',
        enable_table=False
    )

    # 3. 결과 처리
    if result:
        # 요약 출력
        OCRProcessor.print_summary(result)

        # DataFrame 변환
        df = OCRProcessor.to_dataframe(result)
        print(f"\n✅ DataFrame 생성: {len(df)} 행")

        # Markdown 변환
        markdown = OCRProcessor.to_markdown(result, include_confidence=True)
        print(f"\n✅ Markdown 변환 완료 ({len(markdown)} 문자)")

        return result, df

    return None, None


def example_custom_output_management():
    """커스텀 출력 관리"""
    print("\n" + "=" * 50)
    print("고급 예제: 커스텀 출력 관리")
    print("=" * 50)

    # 1. 출력 관리자 생성
    output_mgr = OCROutputManager(
        pdf_path='data/document.pdf',
        output_base='./my_custom_output',
        project_name='custom_project'
    )

    # 2. 디렉토리 설정
    output_mgr.setup_directories()
    print(f"✅ 출력 디렉토리: {output_mgr.project_dir}")

    # 3. OCR 실행
    client = ClovaOCRClient(API_URL, SECRET_KEY)
    result = client.ocr_from_file('data/document.pdf')

    # 4. 커스텀 저장 로직
    if result:
        import json

        # JSON 저장
        json_path = output_mgr.get_path('result.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # 텍스트 저장
        text = OCRProcessor.to_text(result)
        txt_path = output_mgr.get_path('extracted.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✅ 파일 저장 완료")
        print(f"  - {json_path}")
        print(f"  - {txt_path}")


def example_batch_processing():
    """배치 처리"""
    from pathlib import Path

    print("\n" + "=" * 50)
    print("고급 예제: 배치 처리")
    print("=" * 50)

    pdf_dir = Path('data')
    pdf_files = list(pdf_dir.glob('*.pdf'))

    print(f"📁 발견된 PDF 파일: {len(pdf_files)}개")

    client = ClovaOCRClient(API_URL, SECRET_KEY)

    for pdf_file in pdf_files:
        print(f"\n처리 중: {pdf_file.name}")

        try:
            result = client.ocr_from_file(str(pdf_file))

            if result:
                # 간단한 통계
                total_fields = sum(len(img['fields']) for img in result['images'])
                print(f"  ✅ {total_fields}개 텍스트 필드 추출")

        except Exception as e:
            print(f"  ❌ 실패: {e}")


if __name__ == '__main__':
    # 예제 실행

    # example_direct_api_call()
    # example_custom_output_management()
    # example_batch_processing()

    print("\n💡 이 예제들은 패키지의 개별 클래스를 직접 사용합니다")
    print("더 세밀한 제어가 필요할 때 유용합니다")