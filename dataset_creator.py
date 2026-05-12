"""
dataset_creator.py — Fetches GitHub repository data and builds a CSV dataset.
Run this once to generate github_dataset.csv used for analysis reference.
"""

import requests
import pandas as pd
import base64
import os
import time
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env file. Please add it.")

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

repos = [
    "tensorflow/tensorflow", "pytorch/pytorch", "keras-team/keras",
    "scikit-learn/scikit-learn", "huggingface/transformers", "openai/openai-python",
    "pallets/flask", "django/django", "fastapi/fastapi",
    "streamlit/streamlit", "pandas-dev/pandas", "matplotlib/matplotlib",
    "plotly/plotly.py", "numpy/numpy", "docker/compose",
    "kubernetes/kubernetes", "ansible/ansible", "sqlalchemy/sqlalchemy",
    "mongodb/mongo-python-driver", "pytest-dev/pytest",
    "robotframework/robotframework", "OWASP/CheatSheetSeries",
    "aquasecurity/trivy", "psf/requests", "encode/httpx",
    "celery/celery", "pydantic/pydantic", "scrapy/scrapy",
]


def fetch_with_retry(url, headers, retries=3, backoff=5):
    for attempt in range(retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response
        elif response.status_code == 403:
            reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset_time - int(time.time()), 10)
            print(f"  Rate limit hit. Waiting {wait}s...")
            time.sleep(wait)
        elif response.status_code == 404:
            return None
        else:
            time.sleep(backoff)
    return None


def get_contributor_count(repo, headers):
    url = f"https://api.github.com/repos/{repo}/contributors?per_page=1&anon=true"
    response = fetch_with_retry(url, headers)
    if response and "Link" in response.headers:
        link_header = response.headers["Link"]
        if 'rel="last"' in link_header:
            try:
                last_url = [l.split(";")[0].strip().strip("<>")
                            for l in link_header.split(",")
                            if 'rel="last"' in l][0]
                return int(last_url.split("page=")[-1])
            except Exception:
                pass
    return len(response.json()) if response else 0


def get_topics(repo, headers):
    url = f"https://api.github.com/repos/{repo}/topics"
    topic_headers = {**headers, "Accept": "application/vnd.github.mercy-preview+json"}
    response = fetch_with_retry(url, topic_headers)
    if response:
        return ", ".join(response.json().get("names", []))
    return ""


def get_readme(repo, headers):
    url = f"https://api.github.com/repos/{repo}/readme"
    response = fetch_with_retry(url, headers)
    if response:
        data = response.json()
        if "content" in data:
            try:
                return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
            except Exception:
                pass
    return ""


dataset = []

for repo in repos:
    print(f"\nFetching: {repo}")
    repo_response = fetch_with_retry(f"https://api.github.com/repos/{repo}", headers)
    if not repo_response:
        print(f"  Skipping {repo}")
        continue

    repo_data = repo_response.json()
    readme_text = get_readme(repo, headers)
    topics = get_topics(repo, headers)
    contributor_count = get_contributor_count(repo, headers)

    release_response = fetch_with_retry(f"https://api.github.com/repos/{repo}/releases/latest", headers)
    latest_release = ""
    if release_response:
        latest_release = release_response.json().get("tag_name", "")

    record = {
        "repo_name":         repo_data.get("name", ""),
        "full_name":         repo_data.get("full_name", ""),
        "description":       repo_data.get("description", ""),
        "language":          repo_data.get("language", ""),
        "topics":            topics,
        "stars":             repo_data.get("stargazers_count", 0),
        "forks":             repo_data.get("forks_count", 0),
        "open_issues":       repo_data.get("open_issues_count", 0),
        "watchers":          repo_data.get("watchers_count", 0),
        "size_kb":           repo_data.get("size", 0),
        "license":           (repo_data.get("license") or {}).get("name", ""),
        "default_branch":    repo_data.get("default_branch", ""),
        "is_fork":           repo_data.get("fork", False),
        "is_archived":       repo_data.get("archived", False),
        "has_wiki":          repo_data.get("has_wiki", False),
        "has_projects":      repo_data.get("has_projects", False),
        "created_at":        repo_data.get("created_at", ""),
        "updated_at":        repo_data.get("updated_at", ""),
        "pushed_at":         repo_data.get("pushed_at", ""),
        "contributor_count": contributor_count,
        "latest_release":    latest_release,
        "homepage":          repo_data.get("homepage", ""),
        "readme_length":     len(readme_text),
        "readme":            readme_text[:5000],
    }

    dataset.append(record)
    print(f"  Stars: {record['stars']:,} | Language: {record['language']}")
    time.sleep(1)

df = pd.DataFrame(dataset)
df.to_csv("github_dataset.csv", index=False)
print(f"\nDataset created! {len(df)} repositories saved to github_dataset.csv")
