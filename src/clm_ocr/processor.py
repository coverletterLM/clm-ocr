"""
OCR 결과 처리 (파싱, 변환, 분석)
OCR JSON을 다양한 형식으로 변환하는 비즈니스 로직
"""
import pandas as pd
import fitz  # PyMuPDF
from typing import Dict, Any, List


class OCRProcessor:
    """OCR 결과 처리 클래스"""

    @staticmethod
    def to_dataframe(ocr_result: Dict[str, Any]) -> pd.DataFrame:
        """
        OCR 결과를 DataFrame으로 변환

        Args:
            ocr_result: CLOVA OCR API 응답

        Returns:
            파싱된 결과 DataFrame
        """
        data = []

        for img_idx, image in enumerate(ocr_result.get('images', [])):
            for field_idx, field in enumerate(image.get('fields', [])):
                # boundingPoly 좌표 안전하게 추출
                x1, y1 = 0, 0
                try:
                    vertices = field.get('boundingPoly', {}).get('vertices', [])
                    if vertices and len(vertices) > 0:
                        x1 = float(vertices[0].get('x', 0))
                        y1 = float(vertices[0].get('y', 0))
                except (TypeError, ValueError, IndexError):
                    pass

                data.append({
                    '페이지': img_idx + 1,
                    '필드_번호': field_idx + 1,
                    '텍스트': str(field.get('inferText', '')),
                    '신뢰도': float(field.get('inferConfidence', 0)),
                    '타입': str(field.get('type', 'NORMAL')),
                    '줄바꿈': bool(field.get('lineBreak', False)),
                    'X1': x1,
                    'Y1': y1,
                })

        return pd.DataFrame(data)

    @staticmethod
    def to_text(ocr_result: Dict[str, Any]) -> str:
        """
        OCR 결과에서 전체 텍스트 추출

        Args:
            ocr_result: CLOVA OCR API 응답

        Returns:
            추출된 전체 텍스트
        """
        texts = []

        for image in ocr_result.get('images', []):
            page_text = []
            for field in image.get('fields', []):
                text = field.get('inferText', '')
                page_text.append(text)

                # lineBreak가 true면 줄바꿈 추가
                if field.get('lineBreak', False):
                    page_text.append('\n')
                else:
                    page_text.append(' ')

            texts.append(''.join(page_text))

        return '\n\n--- 페이지 구분 ---\n\n'.join(texts)

    @staticmethod
    def to_markdown(
        ocr_result: Dict[str, Any],
        include_confidence: bool = False
    ) -> str:
        """
        OCR 결과를 Markdown으로 변환

        Args:
            ocr_result: CLOVA OCR API 응답
            include_confidence: 낮은 신뢰도 텍스트에 신뢰도 표시 여부

        Returns:
            Markdown 형식 문자열
        """
        md_lines = []

        for page_idx, image in enumerate(ocr_result.get('images', [])):
            md_lines.append(f"## 페이지 {page_idx + 1}\n")

            current_paragraph = []
            for field in image.get('fields', []):
                text = field.get('inferText', '').strip()
                confidence = field.get('inferConfidence', 0)

                if not text:
                    continue

                # 낮은 신뢰도 표시
                if include_confidence and confidence < 0.9:
                    text = f"*{text}* ({confidence:.1%})"

                # 줄바꿈 처리
                if field.get('lineBreak', False):
                    current_paragraph.append(text)
                    md_lines.append(' '.join(current_paragraph) + '\n')
                    current_paragraph = []
                else:
                    current_paragraph.append(text)

            if current_paragraph:
                md_lines.append(' '.join(current_paragraph) + '\n')

            md_lines.append('\n---\n\n')

        return '\n'.join(md_lines)

    @staticmethod
    def to_searchable_pdf(
        original_pdf: str,
        ocr_result: Dict[str, Any],
        output_path: str
    ) -> bool:
        """
        OCR 결과로 검색 가능한 PDF 생성

        Args:
            original_pdf: 원본 PDF 파일 경로
            ocr_result: CLOVA OCR API 응답
            output_path: 출력 PDF 파일 경로

        Returns:
            성공 여부
        """
        try:
            doc = fitz.open(original_pdf)

            for page_num, image_result in enumerate(ocr_result.get('images', [])):
                if page_num >= len(doc):
                    break

                page = doc[page_num]

                for field in image_result.get('fields', []):
                    text = field.get('inferText', '')
                    vertices = field.get('boundingPoly', {}).get('vertices', [])

                    if not vertices or len(vertices) < 4:
                        continue

                    x0 = min(v.get('x', 0) for v in vertices)
                    y0 = min(v.get('y', 0) for v in vertices)
                    x1 = max(v.get('x', 0) for v in vertices)
                    y1 = max(v.get('y', 0) for v in vertices)

                    rect = fitz.Rect(x0, y0, x1, y1)
                    page.insert_textbox(rect, text, fontsize=11, render_mode=3)

            doc.save(output_path)
            doc.close()
            print(f"✅ Searchable PDF 생성: {output_path}")
            return True

        except Exception as e:
            print(f"❌ Searchable PDF 생성 실패: {e}")
            return False

    @staticmethod
    def extract_tables(ocr_result: Dict[str, Any]) -> List[Dict]:
        """
        OCR 결과에서 테이블 추출하여 DataFrame으로 변환

        Args:
            ocr_result: CLOVA OCR API 응답

        Returns:
            테이블 정보 딕셔너리 리스트
            [{'page': 1, 'table_idx': 1, 'dataframe': DataFrame}, ...]
        """
        tables_list = []

        for page_idx, image in enumerate(ocr_result.get('images', [])):
            tables = image.get('tables', [])

            for table_idx, table in enumerate(tables):
                cells = table.get('cells', [])
                if not cells:
                    continue

                # 테이블 크기 파악
                max_row = max(cell.get('rowIndex', 0) for cell in cells) + 1
                max_col = max(cell.get('columnIndex', 0) for cell in cells) + 1

                # 2D 배열 생성
                grid = [[''] * max_col for _ in range(max_row)]

                # 셀 배치
                for cell in cells:
                    row = cell.get('rowIndex', 0)
                    col = cell.get('columnIndex', 0)
                    text_lines = cell.get('cellTextLines', [])
                    text = text_lines[0].get('text', '') if text_lines else ''
                    grid[row][col] = text

                # DataFrame 생성
                df = pd.DataFrame(grid[1:], columns=grid[0] if grid else [])
                tables_list.append({
                    'page': page_idx + 1,
                    'table_idx': table_idx + 1,
                    'dataframe': df
                })

        return tables_list

    @staticmethod
    def print_summary(ocr_result: Dict[str, Any]) -> None:
        """
        OCR 결과 요약 출력

        Args:
            ocr_result: CLOVA OCR API 응답
        """
        print("\n" + "="*50)
        print("📊 OCR 결과 요약")
        print("="*50)

        # 페이지 수
        num_pages = len(ocr_result.get('images', []))
        print(f"📄 총 페이지 수: {num_pages}")

        # 각 페이지별 정보
        for idx, image in enumerate(ocr_result.get('images', [])):
            fields = image.get('fields', [])
            print(f"\n페이지 {idx + 1}:")
            print(f"  - 추출된 필드 수: {len(fields)}")

            if fields:
                # 평균 신뢰도 계산
                confidences = [f.get('inferConfidence', 0) for f in fields]
                avg_confidence = sum(confidences) / len(confidences)
                print(f"  - 평균 신뢰도: {avg_confidence:.2%}")

                # 최저 신뢰도 필드 찾기
                min_conf_field = min(fields, key=lambda x: x.get('inferConfidence', 0))
                print(f"  - 최저 신뢰도: {min_conf_field.get('inferConfidence', 0):.2%}")
                print(f"    텍스트: '{min_conf_field.get('inferText', '')[:50]}...'")

    # ============================================
    # 유틸리티 메서드
    # ============================================

    @staticmethod
    def filter_by_confidence(
        df: pd.DataFrame,
        min_confidence: float = 0.9
    ) -> pd.DataFrame:
        """
        특정 신뢰도 이상의 텍스트만 필터링

        Args:
            df: OCR 결과 DataFrame
            min_confidence: 최소 신뢰도 (기본값: 0.9)

        Returns:
            필터링된 DataFrame
        """
        if df is None or df.empty:
            print("DataFrame이 없습니다.")
            return None
        return df[df['신뢰도'] >= min_confidence]

    @staticmethod
    def extract_page_text(ocr_result: Dict[str, Any], page_num: int) -> str:
        """
        특정 페이지의 텍스트만 추출

        Args:
            ocr_result: CLOVA OCR API 응답
            page_num: 페이지 번호 (1부터 시작)

        Returns:
            해당 페이지의 텍스트
        """
        if page_num <= 0 or page_num > len(ocr_result.get('images', [])):
            return f"페이지 {page_num}은(는) 존재하지 않습니다."

        image = ocr_result['images'][page_num - 1]
        texts = []
        for field in image.get('fields', []):
            texts.append(field.get('inferText', ''))
            if field.get('lineBreak', False):
                texts.append('\n')
            else:
                texts.append(' ')

        return ''.join(texts)

    @staticmethod
    def has_tables(ocr_result: Dict[str, Any]) -> bool:
        """
        OCR 결과에 테이블이 있는지 확인

        Args:
            ocr_result: CLOVA OCR API 응답

        Returns:
            테이블 존재 여부
        """
        for image in ocr_result.get('images', []):
            if image.get('tables', []):
                return True
        return False

    @staticmethod
    def count_tables(ocr_result: Dict[str, Any]) -> Dict[str, int]:
        """
        페이지별 테이블 개수 카운트

        Args:
            ocr_result: CLOVA OCR API 응답

        Returns:
            페이지별 테이블 개수 딕셔너리
        """
        table_count = {}
        total = 0

        for idx, image in enumerate(ocr_result.get('images', [])):
            page_tables = len(image.get('tables', []))
            table_count[f'page_{idx+1}'] = page_tables
            total += page_tables

        table_count['total'] = total
        return table_count
