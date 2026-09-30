import os

from crewai.tools import tool
from firecrawl import FirecrawlApp, ScrapeOptions


@tool
def web_search_tool(query: str) -> list[dict]:
    """웹을 검색하고 제목, 링크, 본문 일부와 모집 상태 관련 문장을 반환합니다."""
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    response = app.search(
        query=query,
        limit=10,
        lang="ko",
        country="kr",
        scrape_options=ScrapeOptions(formats=["markdown"]),
    )
    if not response.success:
        raise RuntimeError("웹 검색에 실패했습니다. Firecrawl 설정을 확인하세요.")

    results = []
    for page in response.data:
        markdown = page.get("markdown") or page.get("description") or ""
        status_lines = [
            line.strip()[:180]
            for line in markdown.splitlines()
            if any(word in line for word in ("마감되었습니다", "접수기간", "상시채용", "채용시마감"))
        ][:8]
        results.append({
            "title": page.get("title", ""),
            "url": page.get("url", ""),
            "status_evidence": status_lines,
            "markdown": markdown[:4000],
        })
    return results
