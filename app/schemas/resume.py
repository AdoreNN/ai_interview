from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class ParsedResume(BaseModel):
    resume_topics: list[str]
    resume_experience: dict[str, int]
    target_position: str | None = None
    experience_level: Literal["intern", "junior", "middle", "senior"] | None = None


class GeneratedQuestion(BaseModel):
    topic: str
    question: str
    target_agent: Literal["tech", "hr", "manager"]


class GithubRepo(BaseModel):
    name: str
    description: str | None = None
    language: str | None = None
    stars: int = 0
    url: HttpUrl


class GithubProfile(BaseModel):
    username: str
    name: str | None = None
    bio: str | None = None
    public_repos: int = 0
    profile_url: HttpUrl
    top_repos: list[GithubRepo] = Field(default_factory=list)


class ResumeParseResponse(BaseModel):
    parsed_resume: ParsedResume
    github_profile: GithubProfile | None = None
    questions: list[GeneratedQuestion]
