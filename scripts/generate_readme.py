from collections import defaultdict
from github import Github
import json
import os

OUTPUT_FILE = "README.md"


def load_config():
    if not os.path.exists("config.json"):
        return {"organizations": []}

    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


config = load_config()

allowed_orgs = {
    org.lower()
    for org in config.get("organizations", [])
    if isinstance(org, str)
}

g = Github(os.getenv("GITHUB_TOKEN"))

target_username = os.getenv("TARGET_USERNAME", "").strip()
github_actor = os.getenv("GITHUB_ACTOR", "").strip()

if target_username:
    username = target_username
elif github_actor:
    username = github_actor
else:
    username = g.get_user().login

print(f"Generating contribution profile for: {username}")

prs_by_org = defaultdict(list)
issues_by_org = defaultdict(list)
reviews_by_org = defaultdict(list)

# --------------------------------------
# Pull Requests
# --------------------------------------

pr_query = f"author:{username} type:pr"

pr_results = g.search_issues(pr_query)

for pr in pr_results:
    org_name = pr.repository.owner.login

    if allowed_orgs and org_name.lower() not in allowed_orgs:
        continue

    repo = g.get_repo(pr.repository.full_name)
    full_pr = repo.get_pull(pr.number)

    prs_by_org[org_name].append({
        "repo": pr.repository.name,
        "title": pr.title,
        "number": pr.number,
        "url": pr.html_url,
        "state": (
            "Merged"
            if full_pr.merged
            else pr.state.capitalize()
        ),
        "created_at": pr.created_at.strftime("%Y-%m-%d"),
        "merged_at": (
            full_pr.merged_at.strftime("%Y-%m-%d")
            if full_pr.merged_at else "-"
        ),
    })

# --------------------------------------
# Issues
# --------------------------------------

issue_query = f"author:{username} type:issue"

issue_results = g.search_issues(issue_query)

for issue in issue_results:
    org_name = issue.repository.owner.login

    if allowed_orgs and org_name.lower() not in allowed_orgs:
        continue

    issues_by_org[org_name].append({
        "repo": issue.repository.name,
        "title": issue.title,
        "number": issue.number,
        "url": issue.html_url,
        "state": issue.state.capitalize(),
        "created_at": issue.created_at.strftime("%Y-%m-%d"),
        "closed_at": (
            issue.closed_at.strftime("%Y-%m-%d")
            if issue.closed_at else "-"
        ),
    })

# --------------------------------------
# PR Reviews
# --------------------------------------

review_query = f"reviewed-by:{username} type:pr"

review_results = g.search_issues(review_query)

for review in review_results:
    org_name = review.repository.owner.login

    if allowed_orgs and org_name.lower() not in allowed_orgs:
        continue

    reviews_by_org[org_name].append({
        "repo": review.repository.name,
        "title": review.title,
        "number": review.number,
        "url": review.html_url,
        "created_at": review.created_at.strftime("%Y-%m-%d"),
    })

# --------------------------------------
# Stats
# --------------------------------------

all_orgs = sorted(
    set(prs_by_org.keys())
    | set(issues_by_org.keys())
    | set(reviews_by_org.keys())
)

total_prs = sum(len(v) for v in prs_by_org.values())
merged_prs = sum(
    1
    for prs in prs_by_org.values()
    for pr in prs
    if pr["merged_at"] != "-"
)

total_issues = sum(len(v) for v in issues_by_org.values())
closed_issues = sum(
    1
    for issues in issues_by_org.values()
    for issue in issues
    if issue["closed_at"] != "-"
)

total_reviews = sum(len(v) for v in reviews_by_org.values())

# --------------------------------------
# README
# --------------------------------------

readme = f"""# 🚀 Open Source Proof of Work

GitHub contributions for @{username}

---

## 📊 Contribution Stats

| Metric | Count |
|---|---|
| Total PRs | {total_prs} |
| Merged PRs | {merged_prs} |
| Total Issues | {total_issues} |
| Closed Issues | {closed_issues} |
| PR Reviews | {total_reviews} |

"""

if not all_orgs:
    readme += "\n_No contributions found yet._\n"

for org in all_orgs:
    readme += f"\n# 🏢 {org}\n"

    prs = sorted(
        prs_by_org[org],
        key=lambda x: x["created_at"],
        reverse=True,
    )

    issues = sorted(
        issues_by_org[org],
        key=lambda x: x["created_at"],
        reverse=True,
    )

    reviews = sorted(
        reviews_by_org[org],
        key=lambda x: x["created_at"],
        reverse=True,
    )

    if prs:
        readme += "\n## Pull Requests\n\n"
        readme += "| Repo | Title | Status | Created | Link |\n"
        readme += "|---|---|---|---|---|\n"

        for pr in prs:
            readme += (
                f"| {pr['repo']} "
                f"| {pr['title']} "
                f"| {pr['state']} "
                f"| {pr['created_at']} "
                f"| [#{pr['number']}]({pr['url']}) |\n"
            )

    if issues:
        readme += "\n## Issues\n\n"
        readme += "| Repo | Title | Status | Created | Link |\n"
        readme += "|---|---|---|---|---|\n"

        for issue in issues:
            readme += (
                f"| {issue['repo']} "
                f"| {issue['title']} "
                f"| {issue['state']} "
                f"| {issue['created_at']} "
                f"| [#{issue['number']}]({issue['url']}) |\n"
            )

    if reviews:
        readme += "\n## PR Reviews\n\n"
        readme += "| Repo | Title | Created | Link |\n"
        readme += "|---|---|---|---|\n"

        for review in reviews:
            readme += (
                f"| {review['repo']} "
                f"| {review['title']} "
                f"| {review['created_at']} "
                f"| [#{review['number']}]({review['url']}) |\n"
            )

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(readme)

print("README generated successfully.")