# AI 에이전트 실습실

Python으로 검색, 도구 호출, 작업 연결, 알림 전송을 실습하는 저장소입니다. 일부 프로젝트는 CrewAI를 사용하며, 각 프로젝트는 독립된 설정과 의존성을 갖고 있습니다.

## 프로젝트

| 프로젝트 | 설명 | 배울 수 있는 내용 |
|---|---|---|
| [영어 → 한국어·그리스어 번역](basic_translator/) | 영어 문장 하나를 두 언어로 번역합니다. | 에이전트 역할 정의, YAML 설정, 순차 실행 |
| [뉴스 수집·요약 에이전트](news-reader-agent/) | 주제에 맞는 웹 문서를 검색하고 기사 본문을 읽어 뉴스 보고서를 작성합니다. | 검색 API, 브라우저 자동화, 사용자 정의 도구, 작업 간 결과 전달 |
| [SAP ABAP 채용 분석 실습](job-hunter-agent/) | 모집 중인 공고를 찾고 기업·지원 적합도·이력서 방향을 분석합니다. | 웹 검색 도구, 구조화된 결과, 이력서 지식 자료 |
| [SAP ABAP 채용공고 알림](job-list-agent/) | 접수 중인 공고를 모아 요약하고 디스코드로 알립니다. | 검색 API, 공고 상태 필터링, 중복 제거, 웹훅 전송 |

## 시작하기

Python 3.13과 uv를 준비한 뒤 저장소를 내려받습니다.

```powershell
git clone https://github.com/sherlock0105/ai-agent-lab.git
cd ai-agent-lab
```

실습할 프로젝트 폴더로 이동한 뒤 해당 README의 설치·실행 안내를 따르세요. `uv sync --locked`는 각 폴더의 `uv.lock`에 기록된 의존성을 설치합니다.

- [번역 프로젝트 사용법과 작동 원리](basic_translator/README.md)
- [뉴스 프로젝트 사용법과 작동 원리](news-reader-agent/README.md)
- [SAP ABAP 채용 분석 실습 사용법](job-hunter-agent/README.md)
- [SAP ABAP 채용공고 알림 사용법](job-list-agent/README.md)

API 키는 각 프로젝트의 `.env`에 입력합니다. `.env`, 가상환경, 개인 이력서와 실행 결과는 Git에서 제외합니다. 프로젝트에 따라 OpenAI, 검색 API 또는 디스코드 웹훅을 사용합니다.
