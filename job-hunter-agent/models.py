from datetime import date

from pydantic import BaseModel, Field


class Job(BaseModel):
    job_title: str
    company_name: str
    job_location: str = "미기재"
    job_posting_url: str
    job_summary: str = "미기재"
    application_status: str
    application_deadline: str = "미기재"
    status_checked_on: date
    years_of_experience_required: str | None = None
    minimum_education: str | None = None
    required_technologies: list[str] = Field(default_factory=list)


class JobList(BaseModel):
    jobs: list[Job]


class RankedJob(BaseModel):
    job: Job
    match_score: int = Field(ge=1, le=5)
    reason: str


class RankedJobList(BaseModel):
    ranked_jobs: list[RankedJob]
