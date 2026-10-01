import unittest
from datetime import date
from unittest.mock import patch

import tools


class JobSearchTests(unittest.TestCase):
    def test_search_keeps_job_pages_and_deduplicates(self):
        class FakeResponse:
            success = True
            data = [
                {"title": "ABAP 개발", "url": "https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=123&source=search", "markdown": "제목\nD-5입사지원\nSAP ABAP 개발 및 운영 업무를 담당합니다."},
                {"title": "ABAP 개발", "url": "https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=123&source=other"},
                {"title": "기사", "url": "https://example.com/jobs/123"},
                {"title": "마감된 공고", "url": "https://www.jobkorea.co.kr/Recruit/GI_Read?Gno=9"},
            ]

        class FakeApp:
            def __init__(self, api_key):
                pass

            def search(self, **kwargs):
                return FakeResponse()

        with patch.object(tools, "FirecrawlApp", FakeApp):
            jobs = tools.search_jobs(("query",), "test-key")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["url"], "https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=123")
        self.assertIn("ABAP", jobs[0]["summary"])

    def test_only_explicitly_open_postings(self):
        today = date(2026, 9, 30)
        self.assertTrue(tools.is_open_posting("공고\nD-14입사지원\n마감일2026.10.14", today))
        self.assertTrue(tools.is_open_posting("공고\nD-10\n접수기간 : 채용시까지", today))
        self.assertFalse(tools.is_open_posting("공고\n접수마감\nD-14 추천공고", today))
        self.assertFalse(tools.is_open_posting("공고\nD-14입사지원\n마감되었습니다.", today))
        self.assertFalse(tools.is_open_posting("공고\nD-14입사지원\n마감일2026.09.10", today))
        self.assertFalse(tools.is_open_posting("공고\nABAP 개발자 모집", today))
        self.assertEqual(
            tools.canonical_url("https://m.jobkorea.co.kr/Recruit/GI_Read/50038407?sc=640"),
            "https://www.jobkorea.co.kr/Recruit/GI_Read/50038407",
        )

    def test_discord_messages_fit_limit(self):
        jobs = [
            {"title": f"공고 {index}", "summary": "ABAP 개발 " * 35, "url": f"https://example.com/{index}"}
            for index in range(50)
        ]
        messages = tools.format_discord_messages(jobs, "2026-09-30")
        self.assertGreater(len(messages), 1)
        self.assertTrue(all(len(message) <= 1900 for message in messages))
        self.assertEqual(sum(message.count("https://example.com/") for message in messages), 50)


if __name__ == "__main__":
    unittest.main()
