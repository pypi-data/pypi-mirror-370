# 나무위키 PDF 보고서 생성기

나무위키 문서를 크롤링해 PDF 보고서로 변환하는 프로젝트입니다.

---

## 디렉토리 구조
```bash
├── decorator # 커스텀 데코레이터
├── exception # 커스텀 예외
├── main.py # 애플리케이션 진입점
├── pdf # 클래스 구조 정의
├── service # 비즈니스 로직
├── templates # 화면 구성
└── parser # 범용 유틸 함수
```
---

## 설치 및 실행 방법

1. 저장소 클론

```bash
git clone https://github.com/pdh0128/namuwiki_to_pdf
cd namuwiki_to_pdf
```
2. 의존성 설치
```bash
pip install -r requirements.txt
```
3. 서버 실행
```bash
uvicorn main:app --reload
```
## 주요 기능
나무위키 문서 크롤링 및 파싱
크롤링한 문서를 PDF 형식으로 변환

## 환경 및 요구사항
Python 3.10 필수

---
## PR 안내
PR은 자유롭게 언제든지 환영합니다! 편하게 올려 주세요.
