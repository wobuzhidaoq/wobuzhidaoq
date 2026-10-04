"""Сбор статистики пользователя через GitHub GraphQL API.

Хватает стандартного GITHUB_TOKEN из Actions: он видит публичные данные.
Чтобы учесть приватные репозитории, можно передать личный токен (PAT).
"""

import datetime as dt
import json
import urllib.request

_QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    name
    createdAt
    followers { totalCount }
    following { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100,
                 orderBy: {field: STARGAZERS, direction: DESC}) {
      totalCount
      nodes {
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch(login: str, token: str) -> dict:
    payload = json.dumps({"query": _QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "anime-profile-readme",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return normalize(data["data"]["user"])


def normalize(user: dict) -> dict:
    """Превращает ответ GraphQL в плоский словарь (такой же формат у --snapshot)."""
    repos = user["repositories"]["nodes"]
    langs: dict[str, dict] = {}
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            entry = langs.setdefault(name, {"name": name, "color": edge["node"]["color"], "size": 0})
            entry["size"] += edge["size"]
    cc = user["contributionsCollection"]
    calendar = [
        {"date": day["date"], "count": day["contributionCount"]}
        for week in cc["contributionCalendar"]["weeks"]
        for day in week["contributionDays"]
    ]
    return {
        "login": user["login"],
        "name": user.get("name") or user["login"],
        "created_at": user["createdAt"],
        "followers": user["followers"]["totalCount"],
        "following": user["following"]["totalCount"],
        "public_repos": user["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "forks": sum(r["forkCount"] for r in repos),
        "prs_total": user["pullRequests"]["totalCount"],
        "issues_total": user["issues"]["totalCount"],
        "commits_year": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "prs_year": cc["totalPullRequestContributions"],
        "issues_year": cc["totalIssueContributions"],
        "reviews_year": cc["totalPullRequestReviewContributions"],
        "contributions_year": cc["contributionCalendar"]["totalContributions"],
        "languages": sorted(langs.values(), key=lambda lang: lang["size"], reverse=True),
        "calendar": calendar,
    }


def derive(stats: dict, today: dt.date | None = None) -> dict:
    """Считает производные показатели: серии, активность, недельный журнал."""
    days = sorted(stats.get("calendar", []), key=lambda d: d["date"])
    counts = [d["count"] for d in days]
    today = today or dt.date.today()

    # Текущая серия: если сегодня ещё не коммитил — считаем со вчера.
    current = 0
    idx = len(days) - 1
    if idx >= 0 and days[idx]["date"] >= today.isoformat() and counts[idx] == 0:
        idx -= 1
    while idx >= 0 and counts[idx] > 0:
        current += 1
        idx -= 1

    longest = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)

    last30 = counts[-30:]
    weekly = [sum(counts[i:i + 7]) for i in range(max(0, len(counts) - 26 * 7), len(counts), 7)]

    return {
        "streak_current": current,
        "streak_longest": longest,
        "active_days_30": sum(1 for c in last30 if c > 0),
        "weekly": weekly[-26:],
    }
