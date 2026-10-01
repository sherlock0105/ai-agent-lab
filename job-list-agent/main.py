import json
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from tools import format_discord_messages, search_jobs, send_discord_messages


QUERIES = (
    "site:saramin.co.kr/zf_user/jobs/view SAP ABAP",
    "site:saramin.co.kr/zf_user/jobs/view ABAP 개발자",
    "site:saramin.co.kr/zf_user/jobs/relay/view SAP ABAP",
    "site:saramin.co.kr/zf_user/jobs/relay/view ABAP 개발자",
    "site:jobkorea.co.kr/Recruit/GI_Read/ SAP ABAP",
    "site:jobkorea.co.kr/Recruit/GI_Read/ ABAP 개발자",
    "site:jobkorea.co.kr/Recruit/GI_Read/ SAP 운영 ABAP",
)


def main() -> None:
    load_dotenv()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not firecrawl_key or not webhook_url:
        raise SystemExit(".env에 FIRECRAWL_API_KEY와 DISCORD_WEBHOOK_URL을 설정하세요.")

    jobs = search_jobs(QUERIES, firecrawl_key)
    today = date.today().isoformat()
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "current_jobs.json"
    output_path.write_text(
        json.dumps({"searched_on": today, "count": len(jobs), "jobs": jobs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    messages = format_discord_messages(jobs, today)
    send_discord_messages(webhook_url, messages)
    print(f"공고 {len(jobs)}건 저장 및 디스코드 전송 완료: {output_path}")


if __name__ == "__main__":
    main()
