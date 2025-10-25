"""
기본 사용 예제
Poetry 설치 후 패키지를 import하여 사용하는 방법
"""
from clm_ocr import process_pdf, load_saved_result


def example_1_process_pdf():
    """예제 1: PDF 파일 처리"""
    print("=" * 50)
    print("예제 1: PDF OCR 처리")
    print("=" * 50)

    # PDF 처리 (기본 출력 형식: json, text, dataframe)
    ocr_result, df = process_pdf(
        pdf_path='data/test.pdf',
        project_name='my_project'
    )

    if df is not None:
        print(f"\n✅ 총 {len(df)}개 텍스트 추출 완료")
        print("\n첫 5줄 미리보기:")
        print(df.head())


def example_2_custom_output():
    """예제 2: 커스텀 출력 형식"""
    print("\n" + "=" * 50)
    print("예제 2: 커스텀 출력 형식")
    print("=" * 50)

    # Markdown과 검색 가능한 PDF 생성
    ocr_result, df = process_pdf(
        pdf_path='data/report.pdf',
        output_formats=['markdown', 'searchable_pdf', 'json'],
        project_name='report_analysis',
        output_base='./custom_output'
    )

    print("✅ Markdown 및 Searchable PDF 생성 완료")


def example_3_table_extraction():
    """예제 3: 테이블 추출"""
    print("\n" + "=" * 50)
    print("예제 3: 테이블 추출")
    print("=" * 50)

    # 테이블 인식 활성화
    ocr_result, df = process_pdf(
        pdf_path='data/financial_report.pdf',
        output_formats=['json', 'dataframe', 'tables'],
        enable_table=True,
        project_name='financial_tables'
    )

    print("✅ 테이블 추출 완료")


def example_4_load_saved():
    """예제 4: 저장된 결과 불러오기"""
    print("\n" + "=" * 50)
    print("예제 4: 저장된 결과 불러오기")
    print("=" * 50)

    # 이전에 처리한 결과 불러오기
    ocr_result, df = load_saved_result('my_project')

    if df is not None:
        print(f"✅ 총 {len(df)}개 텍스트 로드 완료")
        print(f"\n텍스트 샘플:\n{df['text'].head(3).tolist()}")


if __name__ == '__main__':
    # 예제 실행 (필요한 것만 주석 해제)

    # example_1_process_pdf()
    # example_2_custom_output()
    # example_3_table_extraction()
    # example_4_load_saved()

    print("\n💡 사용 방법:")
    print("1. .env 파일에 CLOVA_OCR_API_URL과 CLOVA_OCR_SECRET_KEY 설정")
    print("2. poetry install로 패키지 설치")
    print("3. 위 함수들의 주석을 해제하여 실행")