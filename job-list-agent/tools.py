import json
import re
import time
from datetime import date
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen

from firecrawl import FirecrawlApp, ScrapeOptions


SKIP_LINE = re.compile(r"^(?:#|\[|!\[|https?://|로그인|회원가입|메뉴|홈|공유|스크랩|지원하기|채용정보|전체보기)")
OPEN_STATUS = re.compile(r"D-\d+|오늘마감|접수중|접수 중|상시채용")
CLOSED_STATUS = re.compile(r"접수마감|마감되었습니다|본 채용정보는\s*\*\*마감\*\*|^마감$")


def canonical_url(url: str) -> str | None:
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    host = (parsed.hostname or "").lower().removeprefix("www.")
    path = parsed.path.rstrip("/")
    if parsed.scheme not in ("http", "https"):
        return None
    saramin = (host == "saramin.co.kr" or host.endswith(".saramin.co.kr")) and path.lower() in ("/zf_user/jobs/view", "/zf_user/jobs/relay/view")
    jobkorea = (host == "jobkorea.co.kr" or host.endswith(".jobkorea.co.kr")) and bool(re.fullmatch(r"/recruit/gi_read/\d+", path.lower()))
    if not (saramin or jobkorea):
        return None
    if saramin:
        identifier = parse_qs(parsed.query).get("rec_idx", [None])[0]
        if not identifier or not identifier.isdigit():
            return None
        return f"https://www.saramin.co.kr/zf_user/jobs/view?rec_idx={identifier}"
    return f"https://www.jobkorea.co.kr/Recruit/GI_Read/{path.rsplit('/', 1)[-1]}"


def is_open_posting(markdown: str, today: date | None = None) -> bool:
    """공고 상단의 접수 상태가 명시적으로 진행 중일 때만 통과시킨다."""
    if not markdown:
        return False
    lines = [line.strip() for line in markdown.splitlines()]
    top = lines[:30]
    if any(CLOSED_STATUS.search(line) for line in top):
        return False
    # 본문 접수기간 영역의 '마감되었습니다'는 상단 배지보다 우선한다.
    if any("마감되었습니다." in line for line in lines[:200]):
        return False
    if not any(OPEN_STATUS.search(line) for line in top):
        return False
    # 스크랩 캐시가 낡았을 때 지난 마감일을 가진 공고는 제외한다.
    checked_on = today or date.today()
    for value in re.findall(r"마감일\s*(20\d{2})[.\-/](\d{1,2})[.\-/](\d{1,2})", "\n".join(lines[:200])):
        try:
            if date(*map(int, value)) < checked_on:
                return False
        except ValueError:
            return False
    return True


def summarize(markdown: str, description: str, title: str = "") -> str:
    source = markdown or description
    lines = []
    for raw in source.splitlines():
        line = re.sub(r"!?\[([^\]]+)\]\([^)]+\)", r"\1", raw)
        line = re.sub(r"\s+", " ", line.replace("**", " ").replace("\\", "")).strip(" -*#|\t")
        if len(line) < 12 or SKIP_LINE.search(line) or line.startswith("http") or line == title:
            continue
        if line not in lines:
            lines.append(line[:170])
        if len(lines) == 2:
            break
    return " · ".join(lines)[:300] or description[:300].strip() or "요약 정보 없음 — 원문 확인"


def search_jobs(queries: tuple[str, ...], api_key: str) -> list[dict[str, str]]:
    app = FirecrawlApp(api_key=api_key)
    jobs = {}
    failures = []
    successful_searches = 0
    for query in queries:
        try:
            response = app.search(
                query=query,
                limit=20,
                tbs="qdr:m",
                lang="ko",
                country="kr",
                scrape_options=ScrapeOptions(formats=["markdown"]),
            )
            if not response.success:
                raise RuntimeError("검색 API가 실패를 반환했습니다")
            successful_searches += 1
        except Exception as exc:
            failures.append(f"{query}: {exc}")
            continue
        for page in response.data:
            url = canonical_url(page.get("url", ""))
            if not url or url in jobs:
                continue
            title = re.sub(r"\s+", " ", page.get("title") or "").strip()
            markdown = page.get("markdown") or ""
            description = page.get("description") or ""
            if "ABAP" not in (title + markdown[:1500]).upper():
                continue
            # relay 페이지는 추천 공고만 보여 주기도 하므로 실제 개별 공고를 다시 읽는다.
            if "/jobs/relay/view" in page.get("url", ""):
                try:
                    detail = app.scrape_url(url, formats=["markdown"])
                    markdown = detail.markdown or ""
                except Exception as exc:
                    failures.append(f"공고 확인 실패 {url}: {exc}")
                    continue
            if not is_open_posting(markdown):
                continue
            jobs[url] = {
                "title": title or "제목 미기재",
                "summary": summarize(markdown, description, title),
                "url": url,
            }
    if failures:
        print(f"검색 {len(failures)}건 실패: " + " | ".join(failures), flush=True)
    if not successful_searches:
        raise RuntimeError("검색 결과를 가져오지 못했습니다.")
    return list(jobs.values())


def format_discord_messages(jobs: list[dict[str, str]], today: str) -> list[str]:
    header = f"SAP ABAP 채용공고 {len(jobs)}건 ({today})\n검색 시점 접수 중 확인. 지원 전 원문을 다시 확인하세요."
    if not jobs:
        return [header + "\n검색된 공고가 없습니다."]
    messages = []
    current = header
    for index, job in enumerate(jobs, 1):
        title = job["title"].replace("@", "＠")[:160]
        summary = job["summary"].replace("@", "＠")[:300]
        entry = f"\n\n{index}. **{title}**\n{summary}\n{job['url']}"
        if len(current) + len(entry) > 1900:
            messages.append(current)
            current = f"SAP ABAP 채용공고 ({today}, 이어서)"
        current += entry
    messages.append(current)
    return messages


def send_discord_messages(webhook_url: str, messages: list[str]) -> None:
    if not webhook_url.startswith("https://discord.com/api/webhooks/"):
        raise ValueError("DISCORD_WEBHOOK_URL이 올바른 디스코드 웹훅 URL이 아닙니다.")
    for message in messages:
        payload = json.dumps({"content": message, "allowed_mentions": {"parse": []}}).encode("utf-8")
        request = Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "JobListAgent/1.0"},
        )
        for attempt in range(4):
            try:
                with urlopen(request, timeout=30) as response:
                    if response.status not in (200, 204):
                        raise RuntimeError(f"디스코드 전송 실패: HTTP {response.status}")
                break
            except HTTPError as exc:
                if exc.code != 429:
                    try:
                        detail = json.loads(exc.read().decode("utf-8"))
                        reason = detail.get("message", "")
                    except (ValueError, UnicodeDecodeError):
                        reason = ""
                    raise RuntimeError(f"디스코드 전송 실패: HTTP {exc.code} {reason}") from None
                if attempt == 3:
                    raise RuntimeError("디스코드 전송 실패: 요청 제한이 계속됩니다") from None
                retry_after = float(exc.headers.get("Retry-After", "1"))
                time.sleep(min(max(retry_after, 1), 10))
