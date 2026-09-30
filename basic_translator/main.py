import sys

# Support Greek text and CrewAI emoji logs on Windows consoles.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

import dotenv

dotenv.load_dotenv()

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class TranslatorCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def translator_agent(self):
        return Agent(config=self.agents_config["translator_agent"])

    @agent
    def greek_translator_agent(self):
        return Agent(config=self.agents_config["greek_translator_agent"])

    @task
    def translate_task(self):
        return Task(config=self.tasks_config["translate_task"])

    @task
    def retranslate_task(self):
        return Task(config=self.tasks_config["retranslate_task"])

    @crew
    def assemble_crew(self):
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


result = TranslatorCrew().assemble_crew().kickoff(
    inputs={
        "sentence": "I'm Alex and I like to ride my bicycle in Napoli",
    }
)
