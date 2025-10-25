# CLOVA OCR Processor

NAVER CLOVA OCR API를 사용한 PDF 텍스트 추출 라이브러리

## 📌 프로젝트 정보

- **버전**: 0.1.0 (Alpha)
- **Python**: 3.11+
- **목적**: PDF 문서에서 텍스트 자동 추출 및 구조화

## 🎯 구현된 기능

### 핵심 기능
- ✅ PDF → 텍스트 추출 (CLOVA OCR API)
- ✅ 다양한 출력 형식 (JSON, CSV, TXT, Markdown, Searchable PDF)
- ✅ 결과 캐싱 및 재사용
- ✅ 프로젝트별 결과 관리

### 출력 형식
| 형식 | 파일명 | 용도 |
|------|--------|------|
| JSON | `ocr_result.json` | API 원본 응답 |
| CSV | `ocr_data.csv` | 구조화된 데이터 (페이지, 텍스트, 신뢰도, 좌표) |
| Text | `extracted_text.txt` | 순수 텍스트 |
| Markdown | `document.md` | 마크다운 문서 |
| Searchable PDF | `searchable.pdf` | 검색 가능한 PDF |

## 🚀 설치 및 설정

### 1. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일에 CLOVA OCR API 정보 입력
```

**.env**:
```bash
CLOVA_OCR_API_URL=https://xxxxxxxx.apigw.ntruss.com/custom/v1/xxxxx/general
CLOVA_OCR_SECRET_KEY=your-secret-key
```

> ⚠️ **보안**: `.env` 파일은 절대 Git에 커밋하지 마세요!

### 2. 패키지 설치
```bash
# Poetry 사용 (권장)
poetry install

# 또는 pip
pip install -e .
```

## 💻 사용법

### 기본 사용
```python
from clm_ocr.main import process_pdf

# PDF 처리
ocr_result, df = process_pdf('data/sample.pdf')

# 결과 확인
print(f"추출 필드: {len(df)}")
print(f"평균 신뢰도: {df['신뢰도'].mean():.2%}")
```

### 출력 경로 구조
```
output/
└── sample/              # PDF 파일명
    ├── ocr_result.json  # API 원본
    ├── ocr_data.csv     # DataFrame
    └── extracted_text.txt
```

### 결과 재사용 (API 비용 절감)
```python
from clm_ocr.main import load_saved_result

# 저장된 결과 로드 (API 재호출 안함)
ocr_result, df = load_saved_result('sample')
```

### 커스텀 설정
```python
# 프로젝트명 지정
process_pdf('data/doc.pdf', project_name='계약서_분석')

# 출력 형식 선택
process_pdf('data/doc.pdf', output_formats=['json', 'text'])

# 테이블 인식
process_pdf('data/doc.pdf', enable_table=True)
```

## 🏗️ 프로젝트 구조

```
clm-ocr/
├── src/clm_ocr/
│   ├── config.py         # 환경 설정
│   ├── client.py         # OCR API 클라이언트
│   ├── processor.py      # 결과 처리 (변환, 분석)
│   └── main.py           # 워크플로우
├── tests/                # 단위 테스트
├── examples/             # 사용 예시
├── .env.example          # 환경 변수 템플릿
└── pyproject.toml        # 프로젝트 메타데이터
```

### 모듈 설명
- **config.py**: 환경 변수 로드 및 검증
- **client.py**:
  - `ClovaOCRClient`: API 호출, 캐싱
  - `OCROutputManager`: 파일 저장 관리
- **processor.py**:
  - `OCRProcessor`: 데이터 변환 (DataFrame, Text, Markdown 등)
- **main.py**:
  - `process_pdf()`: 메인 처리 함수
  - `load_saved_result()`: 결과 로드

## 🧪 테스트

```bash
# 전체 테스트
pytest

# 커버리지 포함
pytest --cov=clm_ocr

# 특정 테스트
pytest tests/test_processor.py
```

## 📊 DataFrame 구조

```python
# ocr_data.csv 열 구조
페이지 | 필드_번호 | 텍스트 | 신뢰도 | 타입 | 줄바꿈 | X1 | Y1
```

**활용 예시**:
```python
# 신뢰도 필터링
high_conf = df[df['신뢰도'] >= 0.95]

# 특정 페이지 추출
page1 = df[df['페이지'] == 1]
```

## 🔧 개발 가이드

### 코드 포맷팅
```bash
black src/ tests/
flake8 src/ tests/
```

### 타입 체크
```bash
mypy src/
```

## 📝 개발 현황

### 완료
- [x] CLOVA OCR API 연동
- [x] 다중 출력 형식 지원
- [x] 결과 캐싱
- [x] 단위 테스트
- [x] 환경 변수 관리

### 예정
- [ ] 배치 처리 (다중 PDF)
- [ ] 비동기 처리
- [ ] 진행률 표시
- [ ] 에러 복구 로직
- [ ] 테스트 커버리지 80%+

## 📄 라이선스

MIT License