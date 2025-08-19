# NADF — 나무위키 PDF 보고서 생성기

나무위키 문서를 크롤링해 구조화하고, 한글 폰트로 보기 좋은 PDF 보고서로 변환하는 파이썬 라이브러리입니다. <br>
패키지 내부에 Noto Serif KR 폰트가 포함되어 있어 별도 폰트 설치 없이 곧바로 사용하실 수 있습니다.

### 핵심 기능
나무위키 문서 크롤링 & 파싱 <br>
섹션(h2/h3/h4) 구조를 보존한 PDF 생성(fpdf2 기반) <br>
한글 폰트 포함(Noto Serif KR Regular/Bold)

### 빠른 설치
```bash
pip install nadf
```

지원 Python: 3.10 이상

### 빠른 시작
```python

import asyncio
from nadf.crawler import Crawler
from nadf.pdf import PDF


async def create_pdf(url : str):
    crawler = Crawler()
    name, data = await crawler.get_namuwiki_list(url)

    pdf = PDF(doc_title=f"{name} 분석 보고서")
    await pdf.create_pdf_from_namuwiki_list(data, "./")

if __name__ == "__main__":
    url = "https://namu.wiki/w/%EC%84%AC%EC%97%90%EC%96%B4"
    asyncio.run(create_pdf(url))
```

### 사용 팁
PDF 내부 폰트는 패키지 리소스로 자동 로드됩니다.

```bash
nadf/
 ├─ crawler/         # 크롤러 & HTTP 클라이언트
 ├─ decorator/       # URL 검증 등 데코레이터
 ├─ exception/       # 예외 정의
 ├─ fonts/           # NotoSerifKR Regular/Bold (동봉)
 ├─ parser/          # HTML 파서 등
 └─ pdf/             # PDF 생성기 
```

### 참고
PR과 이슈 환영합니다! <br>
버그 리포트 시 재현 코드/환경(Python 버전)과 로그를 함께 제공해 주세요.

### 라이선스
MIT License (패키지 내 LICENSE 참고)