# SAP ABAP 채용공고 알림 (`job-list-agent`)

사람인과 잡코리아에서 SAP ABAP 채용공고를 검색하고, 접수 중임이 확인되는 공고의 제목·짧은 요약·원문 링크를 디스코드로 보내는 Python 프로젝트입니다. 검색 결과는 JSON 파일로도 저장합니다. 이력서나 OpenAI API는 사용하지 않습니다.

## 주요 기능

- 여러 검색어로 최근 공고를 찾고 사람인·잡코리아의 개별 공고 URL만 수집합니다.
- 추적 파라미터를 제거한 URL을 기준으로 중복 공고를 합칩니다.
- 본문에서 접수 중 상태를 확인하고, 마감됐거나 상태가 불분명한 공고는 제외합니다.
- 본문 일부에서 짧은 요약을 추출해 디스코드 메시지 길이에 맞춰 나누어 보냅니다.
- 검색 날짜와 공고 목록을 `output/current_jobs.json`에 저장합니다.

## 준비 및 실행

Python 3.13 이상과 [`uv`](https://docs.astral.sh/uv/)가 필요합니다. 이 폴더에서 다음 명령을 실행하세요.

```powershell
uv sync --locked
Copy-Item .env.example .env
```

macOS/Linux에서는 `cp .env.example .env`를 사용하면 됩니다. `.env`에 자신의 값을 입력합니다.

```dotenv
FIRECRAWL_API_KEY=발급받은_API_키
DISCORD_WEBHOOK_URL=발급받은_디스코드_웹훅_URL
```

Firecrawl API 키는 검색과 공고 본문 수집에, 디스코드 웹훅 URL은 알림 전송에 사용합니다. 두 서비스의 사용량이나 요금은 각 서비스의 정책을 확인하세요. 값 입력을 마쳤으면 실행합니다.

```powershell
uv run main.py
```

## 결과와 설정

실행 결과는 `output/current_jobs.json`에 `searched_on`, `count`, `jobs` 필드로 저장됩니다. 각 공고에는 `title`, `summary`, `url`이 들어갑니다. 디스코드에도 같은 공고의 제목·요약·원문 링크가 전송됩니다. 검색된 공고가 없어도 결과 파일과 알림이 생성됩니다.

검색어는 [`main.py`](main.py)의 `QUERIES`에서 바꿀 수 있습니다. 검색은 최근 한 달(`tbs="qdr:m"`)을 대상으로 하며, 검색어마다 최대 20개 결과를 요청합니다. 조건을 바꾸려면 [`tools.py`](tools.py)의 `search_jobs()`를 수정하세요.

접수 상태는 공고 본문에서 읽은 정보이므로 실시간 상태를 보장하지 않습니다. 지원 전 원문에서 모집 여부와 마감일을 다시 확인하세요. 일부 검색이나 스크랩 요청이 실패하면 해당 요청은 건너뛰고, 모든 검색이 실패하면 오류를 반환합니다.

## 개인정보와 테스트

실제 API 키와 웹훅 URL은 `.env`에만 두세요. `.env`와 `output/`은 Git에서 제외됩니다. 공개 저장소에 올릴 때는 `.env.example`처럼 **값이 비어 있는 예시 파일**만 사용하세요.

```powershell
uv run --locked python -m unittest test_tools -v
```
