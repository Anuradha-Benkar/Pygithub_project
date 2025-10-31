# # import os, git, time, json
# # from github import Github
# # from langgraph.graph import StateGraph
# # from config import GITHUB_TOKEN, REPOS_DOWNLOAD_DIR

# # STATE_FILE = "last_run.json"

# # def get_last_run():
# #     if os.path.exists(STATE_FILE):
# #         with open(STATE_FILE, "r") as f:
# #             data = json.load(f)
# #             return data.get("last_run", 0)
# #     return 0

# # def set_last_run(ts):
# #     with open(STATE_FILE, "w") as f:
# #         json.dump({"last_run": ts}, f)

# # def sync_github_repos():
# #     """Download or update all repos from authenticated GitHub account."""
# #     os.makedirs(REPOS_DOWNLOAD_DIR, exist_ok=True)
# #     g = Github(GITHUB_TOKEN)

# #     if not GITHUB_TOKEN:
# #         raise ValueError("❌ Missing GitHub token")

# #     user = g.get_user()
# #     print(f"🔹User: {user.login}")
# #     print(f"🔹Total repos: {user.get_repos().totalCount}")

# #     for repo in user.get_repos():
# #         repo_path = os.path.join(REPOS_DOWNLOAD_DIR, repo.name)

# #         if not os.path.exists(repo_path):
# #             print(f"\n🔹Cloning: {repo.full_name}")
# #             try:
# #                 url = repo.clone_url.replace("https://", f"https://{GITHUB_TOKEN}@")
# #                 git.Repo.clone_from(url, repo_path, multi_options=["--recurse-submodules"])
# #             except git.exc.GitCommandError as e:
# #                 print(f"❌ Failed to clone {repo.name}: {e}")
# #         else:
# #             print(f"\n🔄 Checking updates: {repo.full_name}")
# #             try:
# #                 local_repo = git.Repo(repo_path)
# #                 local_commit = local_repo.head.commit.hexsha
# #                 remote_commit = repo.get_commits()[0].sha
# #                 if local_commit != remote_commit:
# #                     print(f"📌 Updating {repo.full_name}")
# #                     local_repo.remotes.origin.pull()
# #                     print(f"✅ Updated {repo.full_name}")
# #                 else:
# #                     print(f"⏩ No new commits")
# #             except Exception as e:
# #                 print(f"❌ Update failed: {repo.name}: {e}")

# #     set_last_run(time.time())
# #     return {"status": "✅ Sync complete"}

# # def download_repos_node():
# #     return StateGraph(
# #         name="download_repos",
# #         description="Download & sync all GitHub repos",
# #         func=lambda _: sync_github_repos()
# #     )


# import requests
# import os, git, time, json
# from github import Github
# from langgraph.graph import StateGraph
# from config import GITHUB_TOKEN, REPOS_DOWNLOAD_DIR
# import os, git, time, json
# from github import Github
# from config import GITHUB_TOKEN, REPOS_DOWNLOAD_DIR

# STATE_FILE = "last_run.json"

# def get_last_run():
#     if os.path.exists(STATE_FILE):
#         with open(STATE_FILE, "r") as f:
#             return json.load(f).get("last_run", 0)
#     return 0

# def set_last_run(ts):
#     with open(STATE_FILE, "w") as f:
#         json.dump({"last_run": ts}, f)

# def sync_github_repos():
#     os.makedirs(REPOS_DOWNLOAD_DIR, exist_ok=True)
#     g = Github(GITHUB_TOKEN)

#     headers = {"Authorization": f"token {g}"}
#     response = requests.get("https://api.github.com/user", headers=headers)

#     if response.status_code == 200:
#         print("✅ Token is valid!")
#         print("User:", response.json()["login"])
#     else:
#         print("❌ Invalid or expired token!", response.status_code, response.json())

#     user = g.get_user()

#     print(f"{('='*50)} \n📩 Downloading repositories...")
#     print(f"🔹User: {user.login}")
#     print(f"🔹Total repos: {user.get_repos().totalCount}")
#     print('='*50)

#     for repo in user.get_repos():
#         repo_path = os.path.join(REPOS_DOWNLOAD_DIR, repo.name)

#         if not os.path.exists(repo_path):
#             print(f"\n🔹Cloning: {repo.full_name}")
#             try:
#                 url = repo.clone_url.replace("https://", f"https://{GITHUB_TOKEN}@")
#                 git.Repo.clone_from(url, repo_path, multi_options=["--recurse-submodules"])
#             except git.exc.GitCommandError as e:
#                 print(f"❌ Failed to clone {repo.name}: {e}")
#         else:
#             print(f"\n🔄 Checking updates: {repo.full_name}")
#             try:
#                 local_repo = git.Repo(repo_path)
#                 local_commit = local_repo.head.commit.hexsha
#                 remote_commit = repo.get_commits()[0].sha
#                 if local_commit != remote_commit:
#                     print(f"📌 Updating {repo.full_name}")
#                     local_repo.remotes.origin.pull()
#                     print(f"✅ Updated {repo.full_name}")
#                 else:
#                     print(f"⏩ No new commits")
#             except Exception as e:
#                 print(f"❌ Update failed: {repo.name}: {e}")

#     set_last_run(time.time())
#     return {"status": "✅ Sync complete"}

# # ✅ Node
# def download_repos_node(state: dict) -> dict:
#     result = sync_github_repos()
#     state.update(result)
#     return state


######################################test2###################################
# nodes/download_repos.py
import requests
import os
import git
import time
import json
from github import Github
from config import GITHUB_TOKEN, REPOS_DOWNLOAD_DIR

STATE_FILE = "last_run.json"

def get_last_run():
    """Get timestamp of last sync"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f).get("last_run", 0)
    return 0

def set_last_run(ts):
    """Save timestamp of current sync"""
    with open(STATE_FILE, "w") as f:
        json.dump({"last_run": ts}, f)

def sync_github_repos():
    """Download and sync GitHub repositories"""
    os.makedirs(REPOS_DOWNLOAD_DIR, exist_ok=True)
    
    # Initialize GitHub client
    g = Github(GITHUB_TOKEN)
    
    # Validate token
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get("https://api.github.com/user", headers=headers)
    
    if response.status_code == 200:
        print("✅ GitHub token is valid!")
        print(f"👤 User: {response.json()['login']}")
    else:
        print(f"❌ Invalid or expired token! Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return {"status": "❌ Invalid GitHub token"}
    
    user = g.get_user()
    
    print(f"\n{'='*50}")
    print("📩 Downloading GitHub repositories...")
    print(f"{'='*50}")
    print(f"🔹 User: {user.login}")
    print(f"🔹 Total repos: {user.get_repos().totalCount}")
    print(f"{'='*50}\n")
    
    downloaded_count = 0
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for repo in user.get_repos():
        repo_path = os.path.join(REPOS_DOWNLOAD_DIR, repo.name)
        
        try:
            if not os.path.exists(repo_path):
                # Clone new repository
                print(f"📥 Cloning: {repo.full_name}")
                url = repo.clone_url.replace("https://", f"https://{GITHUB_TOKEN}@")
                git.Repo.clone_from(
                    url, 
                    repo_path, 
                    multi_options=["--recurse-submodules"]
                )
                downloaded_count += 1
                print(f"✅ Successfully cloned {repo.name}")
                
            else:
                # Check for updates in existing repo
                print(f"🔄 Checking updates: {repo.full_name}")
                try:
                    local_repo = git.Repo(repo_path)
                    local_commit = local_repo.head.commit.hexsha
                    remote_commit = repo.get_commits()[0].sha
                    
                    if local_commit != remote_commit:
                        print(f"📌 Updating {repo.full_name}")
                        local_repo.remotes.origin.pull()
                        updated_count += 1
                        print(f"✅ Updated {repo.full_name}")
                    else:
                        skipped_count += 1
                        print(f"⏩ No new commits for {repo.full_name}")
                        
                except Exception as e:
                    error_count += 1
                    print(f"❌ Failed to update {repo.name}: {e}")
                    
        except git.exc.GitCommandError as e:
            error_count += 1
            print(f"❌ Failed to clone {repo.name}: {e}")
        except Exception as e:
            error_count += 1
            print(f"❌ Unexpected error with {repo.name}: {e}")
    
    # Save sync timestamp
    set_last_run(time.time())
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Sync Summary")
    print(f"{'='*50}")
    print(f"✅ Downloaded: {downloaded_count}")
    print(f"🔄 Updated: {updated_count}")
    print(f"⏩ Skipped: {skipped_count}")
    print(f"❌ Errors: {error_count}")
    print(f"{'='*50}\n")
    
    return {
        "status": "✅ Sync complete",
        "downloaded": downloaded_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "errors": error_count
    }

# ✅ LangGraph Node
def download_repos_node(state: dict) -> dict:
    """LangGraph node for downloading repos"""
    print("🚀 Starting repository download/sync...")
    result = sync_github_repos()
    state.update(result)
    return state



############# test 3 ##############################
# nodes/download_repos.py
import os
import git
import time
import json
from github import Github
from config import GITHUB_TOKEN, REPOS_DOWNLOAD_DIR

STATE_FILE = "last_run.json"


def get_last_run():
    """Get timestamp of last sync"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f).get("last_run", 0)
    return 0


def set_last_run(ts):
    """Save timestamp of current sync"""
    with open(STATE_FILE, "w") as f:
        json.dump({"last_run": ts}, f)


def sync_github_repos():
    """Download and sync GitHub repositories"""
    print(f"\n{'='*60}")
    print("📥 Repository Download/Sync Node")
    print(f"{'='*60}\n")
    
    # Ensure directory exists
    os.makedirs(REPOS_DOWNLOAD_DIR, exist_ok=True)
    print(f"✅ Repos directory: {REPOS_DOWNLOAD_DIR}")
    
    # Check if directory is accessible
    if not os.path.isdir(REPOS_DOWNLOAD_DIR):
        return {"status": "❌ Cannot access repos directory"}
    
    # Initialize GitHub client
    print(f"🔑 Authenticating with GitHub...")
    try:
        g = Github(GITHUB_TOKEN)
        user = g.get_user()
        print(f"✅ Authenticated as: {user.login}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return {"status": "❌ Invalid GitHub token"}
    
    print(f"\n{'='*50}")
    print("📦 Fetching Repositories")
    print(f"{'='*50}")
    
    try:
        repos = list(user.get_repos())
        print(f"✅ Found {len(repos)} repositories")
    except Exception as e:
        print(f"❌ Failed to fetch repos: {e}")
        return {"status": "❌ Failed to fetch repositories"}
    
    if len(repos) == 0:
        print("⚠️  No repositories found for this user")
        return {
            "status": "⚠️ No repositories",
            "downloaded": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0
        }
    
    downloaded_count = 0
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, repo in enumerate(repos, 1):
        print(f"\n[{i}/{len(repos)}] Processing: {repo.full_name}")
        
        repo_path = os.path.join(REPOS_DOWNLOAD_DIR, repo.name)
        
        try:
            if not os.path.exists(repo_path):
                # Clone new repository
                print(f"  📥 Cloning repository...")
                url = repo.clone_url.replace("https://", f"https://{GITHUB_TOKEN}@")
                
                git.Repo.clone_from(
                    url, 
                    repo_path, 
                    multi_options=["--recurse-submodules"]
                )
                
                print(f"  ✅ Successfully cloned")
                downloaded_count += 1
                
            else:
                # Check for updates
                print(f"  🔄 Checking for updates...")
                
                try:
                    local_repo = git.Repo(repo_path)
                    
                    # Ensure we're on a branch
                    if local_repo.head.is_detached:
                        print(f"  ⚠️  Detached HEAD, skipping update")
                        skipped_count += 1
                        continue
                    
                    # Get local commit
                    local_commit = local_repo.head.commit.hexsha
                    
                    # Get remote commit
                    remote_commits = list(repo.get_commits())
                    if not remote_commits:
                        print(f"  ⚠️  No commits found, skipping")
                        skipped_count += 1
                        continue
                    
                    remote_commit = remote_commits[0].sha
                    
                    if local_commit != remote_commit:
                        print(f"  📌 Updates available")
                        print(f"     Local:  {local_commit[:8]}")
                        print(f"     Remote: {remote_commit[:8]}")
                        
                        local_repo.remotes.origin.pull()
                        print(f"  ✅ Successfully updated")
                        updated_count += 1
                    else:
                        print(f"  ⏩ Already up to date")
                        skipped_count += 1
                        
                except git.exc.InvalidGitRepositoryError:
                    print(f"  ❌ Invalid git repository at {repo_path}")
                    error_count += 1
                except Exception as e:
                    print(f"  ❌ Update failed: {e}")
                    error_count += 1
                    
        except git.exc.GitCommandError as e:
            print(f"  ❌ Git error: {e}")
            error_count += 1
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            error_count += 1
    
    # Save sync timestamp
    set_last_run(time.time())
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Download/Sync Summary")
    print(f"{'='*60}")
    print(f"✅ Downloaded: {downloaded_count}")
    print(f"🔄 Updated:    {updated_count}")
    print(f"⏩ Skipped:    {skipped_count}")
    print(f"❌ Errors:     {error_count}")
    print(f"📂 Total:      {len(repos)}")
    print(f"{'='*60}\n")
    
    # Check if any repos were processed
    total_success = downloaded_count + updated_count + skipped_count
    
    if total_success == 0:
        return {
            "status": "❌ No repositories processed",
            "downloaded": 0,
            "updated": 0,
            "skipped": 0,
            "errors": error_count
        }
    
    return {
        "status": "✅ Sync complete",
        "downloaded": downloaded_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "errors": error_count,
        "total_repos": len(repos)
    }


def download_repos_node(state: dict) -> dict:
    """LangGraph node for downloading repos"""
    print(f"\n{'='*60}")
    print("🚀 Starting Repository Download Node")
    print(f"{'='*60}\n")
    
    result = sync_github_repos()
    
    # Update state
    state.update(result)
    
    # Check if we have any repos
    repos_dir = REPOS_DOWNLOAD_DIR
    if os.path.exists(repos_dir):
        repo_count = len([d for d in os.listdir(repos_dir) if os.path.isdir(os.path.join(repos_dir, d))])
        print(f"✅ Total repositories in {repos_dir}: {repo_count}\n")
        state["local_repo_count"] = repo_count
    else:
        print(f"⚠️  Repos directory not found\n")
        state["local_repo_count"] = 0
    
    return state