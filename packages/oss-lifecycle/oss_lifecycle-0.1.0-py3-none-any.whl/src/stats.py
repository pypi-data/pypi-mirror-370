##### Code to collect stats for a given repo #####

import json
import logging
import os
import re

import subprocess
import tempfile
from typing import List, Tuple, TypedDict

import pypistats
import requests
from bs4 import BeautifulSoup
from pypistats.cli import _month, _last_month

# USAGE
# data = get_all_stats([
#   {"name": "Pandas", "repo": "pandas-dev/pandas", "pypi_package_name": "pandas"},
#   {"name": "Kubernetes", "repo": "kubernetes/kubernetes", "pypi_package_name": "kubernetes"},
#   {"name": "NumPy", "repo": "numpy/numpy", "pypi_package_name": "numpy"}
# ])


logger = logging.getLogger(__name__)


def get_default_branch(repo: str) -> str:
    """Returns the default branch of a Github repo"""

    url = f"https://api.github.com/repos/{repo}"
    headers = {
        "Authorization": f"Bearer {os.environ['GITHUB_API_TOKEN']}", 
        "Accept": "application/vnd.github.v3+json"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()

    return r.json()['default_branch']

def get_stars(repo: str) -> int:
    url = f"https://api.github.com/repos/{repo}"
    headers = {
        "Authorization": f"Bearer {os.environ['GITHUB_API_TOKEN']}", 
        "Accept": "application/vnd.github.v3+json"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()

    return r.json()['stargazers_count']


def get_monthly_pypi_downloads(package: str):
    start_date, end_date = _last_month()
    downloads = pypistats.overall(
        package, 
        total="monthly", 
        format="json", 
        start_date=start_date,
        end_date=end_date
    )

    downloads = json.loads(downloads)
    
    return sum(d['downloads'] for d in downloads['data'])
    

def get_total_contributors_from_web(repo: str) -> int:
    """Scrapes the Github repo page to get the no of contributors"""
    
    soup = BeautifulSoup(
        requests.get(f"https://github.com/{repo}").content, "html.parser"
    )
    for element in soup.find_all("a"):
        if("Contributors" in element.text):
            m = re.sub(r"\D", "", element.text)
            if m is not None:
                return int(m)


def get_total_contributors_from_api(repo: str) -> int:
    """Gets the total contributors from Github API
    
    Does not produce accurate results for repos that have higher 
    number of contributors than 500. See this issue for more info.
    https://github.com/orgs/community/discussions/24355
    """
    
    url = f"https://api.github.com/repos/{repo}/contributors?per_page=100&anon=1"
    headers = {
        "Authorization": f"Bearer {os.environ['GITHUB_API_TOKEN']}", 
        "Accept": "application/vnd.github.v3+json"
    }

    contributor_count = 0
    
    while url:
        r = requests.get(url, headers=headers)
        r.raise_for_status()

        contributor_count += len(r.json())
        try:
            url = r.links["next"]['url']
        except KeyError:
            url = None

    return contributor_count


def get_total_contributors(repo: str) -> int:
    """Returns total no of contributors for a Github repo"""
    
    return get_total_contributors_from_web(repo)


def merged_monthly_prs(repo: str) -> int:
    """Returns avg monthly merged PRs for a repo for the
    last 3 months.
    """
    
    url = "https://api.github.com/search/issues"
    headers = {
        "Authorization": f"Bearer {os.environ['GITHUB_API_TOKEN']}", 
        "Accept": "application/vnd.github.v3+json"
    }

    no_of_months_to_fetch = 3
    
    start_date, end_date = _last_n_month(no_of_months_to_fetch)
    
    params = {
        "q": f"repo:{repo} is:merged merged:{start_date}..{end_date}"
    }
    
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()

    return int(r.json()['total_count']/no_of_months_to_fetch)


def all_pr_count(repo: str) -> int:
    """Returns count of all PRs submitted for the repo"""

    url = "https://api.github.com/search/issues?per_page=1"
    headers = {
        "Authorization": f"Bearer {os.environ['GITHUB_API_TOKEN']}", 
        "Accept": "application/vnd.github.v3+json"
    }

    params = {
        "q": f"repo:{repo} is:pr"
    }
    
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()

    return int(r.json()['total_count'])


def total_additions_deletions(repo: str) -> int:
    """Returns total additions/deletions for a repo for
    all it's life.
    """
    
    total = 0
    branch = get_default_branch(repo)
    with tempfile.TemporaryDirectory() as directory:
        _clone_github_branch(f"https://github.com/{repo}", branch, directory)
        commit_log = _get_commit_log(directory)
        additions, deletions = _parse_commit_log(commit_log)
        total = additions + deletions
    
    return total


class Project(TypedDict):
    name: str
    repo: str
    pypi_package_name: str

def get_all_stats(projects: List[Project]) -> dict:
    data = []
    for project in projects:
        repo = project['repo']
        package = project['pypi_package_name']    
        name = project['name']
        print("Project Name:", name, end='..')
        data.append({
            "project": name,
            "stars": get_stars(repo),
            "monthly_merged_prs": merged_monthly_prs(repo),
            "contributors": get_total_contributors(repo),
            "pypi_monthly_downloads": get_monthly_pypi_downloads(package),
            "total_prs": all_pr_count(repo),
            "total_additions_deletions": total_additions_deletions(repo)
        })
        print("done")
    return data


def _last_n_month(n: int) -> tuple[str, str]:
    """Helper to return start_date and end_date of the past nth month as yyyy-mm-dd"""
    import datetime as dt
    from dateutil.relativedelta import relativedelta
    
    today = dt.date.today()
    d1 = today - relativedelta(months=1)
    end_month = _month(d1.isoformat()[:7])
    
    d2 = today - relativedelta(months=n)
    start_month = _month(d2.isoformat()[:7])

    return start_month[0], end_month[1]

def _parse_commit_log(commit_log: str) -> Tuple[int, int]:
    """Parses a git commit log and returns the total no of
    additions and deletions in the git repository.
    """

    pattern = r'(\d+) files? changed, (\d+) insertions?\(\+\), (\d+) deletions?\(-\)'

    matches = re.findall(pattern, commit_log)

    total_additions = 0
    total_deletions = 0

    for match in matches:
        _, adds, deletes = map(int, match)
        total_additions += adds
        total_deletions += deletes

    return total_additions, total_deletions    

def _clone_github_branch(repo_url: str, branch_name: str, directory: str):
    """Clone a specific branch of a GitHub repository into a temporary directory."""
    try:
        clone_command = [
            'git',
            'clone',
            '--branch', branch_name,
            '--single-branch',
            repo_url,
            directory
        ]
        
        subprocess.run(clone_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f"Successfully cloned branch '{branch_name}' from {repo_url} into {directory}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error cloning repository: {e}")

def _get_commit_log(directory: str) -> str:
    """Returns the short format commit log for a git repo."""

    try:
        log_command = [
            'git',
            '-C', directory,
            'log',
            '--shortstat'
        ]
        
        result = subprocess.run(
            log_command, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running git log command: {e}")

def total_downloads_6months(pypi_package_name):
    df = pypistats.overall(pypi_package_name, total=True, format="pandas")
    return df['downloads'].sum()
