import os
import requests
from config import GITHUB_TOKEN, REPOS_DOWNLOAD_DIR

def download_github_repos():
    os.makedirs(REPOS_DOWNLOAD_DIR, exist_ok=True)
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get("https://api.github.com/user/repos", headers=headers)

    if response.status_code != 200:
        raise Exception("Failed to fetch repos: " + response.text)

    repos = response.json()
    for repo in repos:
        name = repo["name"]
        clone_url = repo["clone_url"]
        os.system(f"git clone {clone_url} {REPOS_DOWNLOAD_DIR}/{name}")

    return {"status": "completed", "repos_count": len(repos)}
