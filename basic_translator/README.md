# 영어 → 한국어·그리스어 번역 에이전트

영어 문장 하나를 입력하면 한국어 번역 에이전트와 그리스어 번역 에이전트가 각각 번역하는 CrewAI 실습입니다. 이름과 지명의 표기, 자연스러운 표현을 고려하도록 각 에이전트의 역할을 설정했습니다.

## 설치 및 실행

Python 3.13, uv, OpenAI API 키가 필요합니다. 저장소 루트에서 다음 명령을 실행하세요.

```powershell
cd basic_translator
uv sync --locked
Copy-Item .env.example .env
```

`.env`의 `OPENAI_API_KEY`를 본인의 키로 입력합니다. 이미 `.env`가 있다면 복사 단계는 건너뜁니다.

```powershell
uv run main.py
```

번역 진행 과정과 결과는 터미널에 표시됩니다. 별도의 결과 파일을 저장하지 않습니다.

## 입력 문장 바꾸기

`main.py` 마지막 부분의 `sentence` 값을 수정합니다.

```python
inputs={
    "sentence": "I'm Dohyun and I like to ride my bicycle in Napoli",
}
```

## 작동 원리

1. `dotenv.load_dotenv()`가 API 키를 환경변수로 읽습니다.
2. `@CrewBase`가 `config/agents.yaml`과 `config/tasks.yaml`을 읽습니다.
3. `@agent` 메서드가 한국어·그리스어 번역 에이전트를 생성합니다.
4. `@task` 메서드가 각 번역 작업을 담당 에이전트에 연결합니다.
5. `Process.sequential`로 한국어 번역과 그리스어 번역을 순서대로 실행합니다.

두 작업 모두 같은 영어 원문을 입력으로 사용합니다. 한국어 번역을 다시 그리스어로 번역하는 구조가 아닙니다. `tasks.yaml`의 `context: []`는 앞 작업의 결과를 번역 문맥으로 전달하지 않도록 설정합니다.

## 파일 구성

| 파일 | 역할 |
|---|---|
| `main.py` | 에이전트와 작업 생성, 입력 문장 설정, 실행 |
| `config/agents.yaml` | 두 번역가의 역할·목표·배경 |
| `config/tasks.yaml` | 번역 지시와 기대 출력, 담당 에이전트 |
| `.env.example` | API 키 설정 예시 |
| `pyproject.toml`, `uv.lock` | 의존성과 재현 가능한 설치 정보 |

Windows 콘솔에서 그리스어와 로그의 이모지가 표시되도록 출력 인코딩을 UTF-8로 설정합니다. 번역은 언어 모델이 생성하므로 중요한 문장은 검토해서 사용하세요.
