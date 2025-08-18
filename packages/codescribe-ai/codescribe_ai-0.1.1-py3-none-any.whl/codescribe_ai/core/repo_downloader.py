import os
import zipfile
import tempfile
import requests
from urllib.parse import urlparse

GITHUB_API = "https://api.github.com/repos"

def parse_github_url(url):
    """Parse GitHub repo URL into owner, repo, branch."""
    url = url.strip()
    if url.endswith(".git"):
        url = url[:-4]

    branch = None
    if "@" in url:
        url, branch = url.split("@", 1)

    path_parts = urlparse(url).path.strip("/").split("/")
    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub URL format")

    owner, repo = path_parts[:2]
    return owner, repo, branch


def get_default_branch(owner, repo):
    """Fetch default branch from GitHub API."""
    resp = requests.get(f"{GITHUB_API}/{owner}/{repo}")
    if resp.status_code == 200:
        return resp.json().get("default_branch", "main")
    else:
        raise RuntimeError(f"Failed to fetch repo info: {resp.status_code} - {resp.text}")


def download_and_extract_repo(repo_url, extract_to):
    """Download & extract GitHub repo ZIP for given branch."""
    owner, repo, branch = parse_github_url(repo_url)

    if not branch:
        branch = get_default_branch(owner, repo)

    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
    print(f"Downloading repository {repo_url} (branch: {branch})...")

    resp = requests.get(zip_url, stream=True)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to download repo zip from {zip_url} ({resp.status_code})")

    # Create a temp file, write, and close it before opening with ZipFile
    tmp_zip_path = os.path.join(tempfile.gettempdir(), f"{repo}-{branch}.zip")
    with open(tmp_zip_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    # Now open ZIP and extract
    with zipfile.ZipFile(tmp_zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    # Delete temp zip
    os.remove(tmp_zip_path)

    extracted_folders = os.listdir(extract_to)
    if extracted_folders:
        return os.path.join(extract_to, extracted_folders[0])
    return extract_to
