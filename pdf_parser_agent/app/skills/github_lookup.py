"""Skill 3: найти ссылку на GitHub в резюме и подтянуть публичный профиль/репозитории.

Без LLM — обычный вызов публичного GitHub REST API. Если ссылки нет, профиль
не находится или GitHub недоступен — просто возвращаем None, это не повод
валить весь /v1/parse (в отличие от skill 1, где нечитаемый PDF — фатальная
ошибка).
"""

import logging
import re

import httpx

from ..config import get_settings
from ..schemas import GithubProfile, GithubRepo

logger = logging.getLogger(__name__)

TOP_REPOS_LIMIT = 5
REQUEST_TIMEOUT = 10.0

# username захватывается тем же regex, что валидирует допустимый алфавит
# GitHub-логина (буквы/цифры/дефис, не более 39 символов, не начинается и не
# заканчивается дефисом) — так что дальше его можно безопасно подставлять в URL
_GITHUB_LINK_RE = re.compile(
    r"github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?)",
    re.IGNORECASE,
)

# сегменты github.com/<это>, которые точно не имя пользователя
_NOT_A_USERNAME = {
    "orgs", "topics", "search", "marketplace", "sponsors", "apps",
    "settings", "features", "about", "pricing", "collections",
}


def extract_github_username(resume_text: str) -> str | None:
    for match in _GITHUB_LINK_RE.finditer(resume_text):
        username = match.group(1)
        if username.lower() not in _NOT_A_USERNAME:
            return username
    return None


async def fetch_github_profile(username: str) -> GithubProfile | None:
    settings = get_settings()
    headers = {"Accept": "application/vnd.github+json"}
    token = settings.github_token.get_secret_value()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        async with httpx.AsyncClient(
            base_url="https://api.github.com", headers=headers, timeout=REQUEST_TIMEOUT
        ) as client:
            user_resp = await client.get(f"/users/{username}")
            if user_resp.status_code == 404:
                logger.info("GitHub-пользователь %s не найден", username)
                return None
            user_resp.raise_for_status()
            user = user_resp.json()

            repos_resp = await client.get(
                f"/users/{username}/repos",
                params={"sort": "pushed", "per_page": 100, "type": "owner"},
            )
            repos_resp.raise_for_status()
            repos = [r for r in repos_resp.json() if not r.get("fork")]
    except httpx.HTTPError as e:
        logger.warning("Не удалось получить GitHub-профиль %s (%s)", username, e)
        return None

    top_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)
    top_repos = top_repos[:TOP_REPOS_LIMIT]

    return GithubProfile(
        username=username,
        name=user.get("name"),
        bio=user.get("bio"),
        public_repos=user.get("public_repos", 0),
        profile_url=user.get("html_url", f"https://github.com/{username}"),
        top_repos=[
            GithubRepo(
                name=r["name"],
                description=r.get("description"),
                language=r.get("language"),
                stars=r.get("stargazers_count", 0),
                url=r["html_url"],
            )
            for r in top_repos
        ],
    )
