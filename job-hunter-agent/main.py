import json
import sys
from datetime import date

import dotenv
from crewai import Agent, Crew, Task
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai.project import CrewBase, agent, crew, task

from models import JobList, RankedJobList
from tools import web_search_tool


dotenv.load_dotenv()
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


def resume_source(name: str):
    return TextFileKnowledgeSource(
        file_paths=["resume.txt"],
        collection_name=f"resume_{name}",
    )


@CrewBase
class JobHunterCrew:
    @agent
    def job_search_agent(self):
        return Agent(config=self.agents_config["job_search_agent"], tools=[web_search_tool])

    @agent
    def job_matching_agent(self):
        return Agent(
            config=self.agents_config["job_matching_agent"],
            knowledge_sources=[resume_source("matching")],
        )

    @agent
    def company_research_agent(self):
        return Agent(
            config=self.agents_config["company_research_agent"],
            tools=[web_search_tool],
        )

    @agent
    def resume_optimization_agent(self):
        return Agent(
            config=self.agents_config["resume_optimization_agent"],
            knowledge_sources=[resume_source("resume")],
        )

    @agent
    def interview_prep_agent(self):
        return Agent(
            config=self.agents_config["interview_prep_agent"],
            knowledge_sources=[resume_source("interview")],
        )

    @task
    def job_extraction_task(self):
        return Task(config=self.tasks_config["job_extraction_task"], output_pydantic=JobList)

    @task
    def job_matching_task(self):
        return Task(config=self.tasks_config["job_matching_task"], output_pydantic=RankedJobList)

    @task
    def company_research_task(self):
        return Task(
            config=self.tasks_config["company_research_task"],
            context=[self.job_matching_task()],
        )

    @task
    def resume_rewriting_task(self):
        return Task(
            config=self.tasks_config["resume_rewriting_task"],
            context=[self.job_matching_task(), self.company_research_task()],
        )

    @task
    def interview_prep_task(self):
        return Task(
            config=self.tasks_config["interview_prep_task"],
            context=[self.job_matching_task(), self.company_research_task(), self.resume_rewriting_task()],
        )

    @crew
    def crew(self):
        return Crew(agents=self.agents, tasks=self.tasks, verbose=False)


def main():
    # 검색 결과를 먼저 전달해 에이전트가 검색을 생략하고 빈 목록을 반환하지 않도록 한다.
    queries = (
        "site:saramin.co.kr/zf_user/jobs/view ABAP 신입",
        "site:jobkorea.co.kr/Recruit/GI_Read ABAP 신입",
        "site:jobkorea.co.kr/Recruit/GI_Read ABAP 상시채용",
    )
    search_results = []
    for query in queries:
        results = web_search_tool.run(query=query)
        if not isinstance(results, list):
            raise RuntimeError(f"채용 검색 실패: {query}")
        search_results.extend(results)

    result = JobHunterCrew().crew().kickoff(
        inputs={
            "today": date.today().isoformat(),
            "search_results": json.dumps(search_results, ensure_ascii=False),
        }
    )
    for task_output in result.tasks_output:
        print(task_output.pydantic or task_output.raw)


if __name__ == "__main__":
    main()
