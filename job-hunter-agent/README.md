# SAP ABAP 채용 공고 분석 실습

CrewAI와 Firecrawl로 사람인·잡코리아의 SAP ABAP 채용 공고를 찾고, 이력서와 비교해 기업·지원 전략을 한글로 정리합니다. 실행은 수동입니다. 검색 결과만으로 접수 상태를 보장할 수 없으므로 지원 전 공고 원문을 확인하세요.

## 준비

Python 3.13과 `uv`가 필요합니다. 이 폴더에서 다음 명령을 실행하세요.

```powershell
uv sync --locked
Copy-Item .env.example .env
Copy-Item knowledge/resume.example.txt knowledge/resume.txt
```

`.env`에 본인의 `OPENAI_API_KEY`와 `FIRECRAWL_API_KEY`를 입력하고, `knowledge/resume.txt`에 **실제 이력**을 적으세요. 두 파일은 Git에서 제외됩니다. API 호출에는 각 서비스의 사용량이 발생할 수 있습니다.

```powershell
uv run main.py
```

## 결과

실행 결과는 `output/`에 저장됩니다.

| 파일 | 내용 |
|---|---|
| `current_jobs.json` | 확인한 공고, 모집 상태, 마감일, 원문 링크 |
| `ranked_jobs.json` | 이력서와 비교한 적합도 및 근거 |
| `company_research.md` | 공고 목록과 회사별 분석 |
| `resume_guidance.md` | 공고별 이력서 작성 방향 |
| `interview_prep.md` | 예상 질문과 답변 요점 |

`output/`은 이력서에서 파생된 정보가 들어갈 수 있어 Git에 올리지 않습니다. 결과를 공유하기 전에는 날짜와 출처를 다시 확인하세요.

## 파일 구성

| 파일 | 역할 |
|---|---|
| `main.py` | 에이전트·작업 연결과 한 번 실행 |
| `tools.py` | Firecrawl 웹 검색 도구 |
| `models.py` | 공고와 평가 결과의 구조 |
| `config/agents.yaml` | 에이전트 역할 |
| `config/tasks.yaml` | 검색·평가·분석 작업 지시 |
| `.env.example` | 필요한 API 키 이름 예시 |
| `knowledge/resume.example.txt` | 개인 이력서 작성 예시 |

개인 이력서와 API 키는 로컬에만 보관합니다. 자동 실행과 디스코드 발송 기능은 포함하지 않았습니다.
