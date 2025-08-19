import logging
import time
import jwt
import google.cloud.logging
from git import Repo, NoSuchPathError
from pathlib import Path
import requests

# Initialize Google Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

# Configure the logger
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)


def auth_payload(client_id):
    return {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": client_id,
    }


def get_github_app_token(installation_id, secret, client_id):
    encoded_jwt = jwt.encode(auth_payload(client_id), secret, algorithm="RS256")
    logger.info("Getting github token...")
    auth_token = requests.post(
        url=f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {encoded_jwt}",
        },
    ).json()["token"]
    logger.info("Successfully got github token.")
    
    return auth_token


def generate_github_path(username, password, org, repo, github_org="github.com"):
    return f"https://{username}:{password}@{github_org}/{org}/{repo}.git"


def get_repo(path_of_git_repo, branch="main", path_to_local_repo="/tmp/repo"):
    try:
        path_to_local_repo = Path(path_to_local_repo)
        if path_to_local_repo.exists():
            logger.info("Pulling latest changes from the repository.")
            repo = Repo(path_to_local_repo)
            repo.remotes.origin.pull()
        else:
            logger.info("Cloning repository...")
            repo = Repo.clone_from(
                path_of_git_repo, str(path_to_local_repo), branch=branch
            )
        return repo
    except NoSuchPathError:
        logger.error("Repository path does not exist. Cloning fresh repository.")
        return Repo.clone_from(path_of_git_repo, str(path_to_local_repo), branch=branch)
    except Exception as e:
        logger.exception(f"Error accessing repo: {str(e)}")
        raise e


def git_push(repo, commit_message, files_to_push=None, branch="main"):
    try:
        logger.info(f"Attempting to push changes to Git with commit message: '{commit_message}'")
        if files_to_push:
            logger.info(f"Adding specific files to commit: {files_to_push}")
            repo.index.add(files_to_push)
        else:
            logger.info("Adding all changes to commit.")
            repo.git.add(all=True)
        logger.info(f"Committing changes with message: '{commit_message}'")
        repo.index.commit(commit_message)
        logger.info(f"Pushing changes to remote 'origin', branch '{branch}'")
        push_info = repo.remote(name="origin").push(refspec=f"{branch}:{branch}")
        for info in push_info:
            if info.flags > 0:
                logger.info(f"Git push info: {info.summary}")
            elif info.flags == 0:
                logger.info(f"Git push info: No update {info.summary}")

        logger.info("Successfully pushed changes to Git.")
    except Exception as e:
        logger.exception(f"Error pushing to Git: {str(e)}")
        raise e

def create_repo(org, repo, token, github_enterprise="github.com", branches=None):
    try:
        logger.info("Creating repository...")
        is_github_cloud = github_enterprise is "github.com"
        api_base = (
            "https://api.github.com"
            if is_github_cloud else f"https://{github_enterprise}/api/v3"
        )

        url = f"{api_base}/orgs/{org}/repos"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json"
        }
        data = {
            "name": repo,
            "private": True,
            "auto_init": True,
            "description": repo
        }

        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 201:
            logger.info("Successfully created repository.")
        else:
            logger.error(f"Failed to create repository: {res.status_code} {res.text}")
            res.raise_for_status()

        if branches:
            main_ref_url = f"{api_base}/repos/{org}/{repo}/git/refs/heads/main"
            res = requests.get(main_ref_url, headers=headers)
            res.raise_for_status()
            sha = res.json()["object"]["sha"]

            for br in branches:
                if br == "main":
                    continue
                ref_url = f"{api_base}/repos/{org}/{repo}/git/refs"
                data = {"ref": f"refs/heads/{br}", "sha": sha}
                r = requests.post(ref_url, headers=headers, json=data)
                if r.status_code == 201:
                    logger.info(f"Created branch {br}")
                elif r.status_code == 422 and "Reference already exists" in r.text:
                    logger.warning(f"Branch {br} already exists, skipping")
                else:
                    logger.error(f"Failed to create branch {br}: {r.status_code} {r.text}")

    except Exception as e:
        logger.exception(f"Error creating repository: {str(e)}")
        raise e