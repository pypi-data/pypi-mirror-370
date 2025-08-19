"""
Collects commit information from a specified GitHub repository and processes it to generate detailed and monthly commit data.
Functions:
    install_gitpython():
        Installs GitPython if it is not already installed.
    clone_github_repo(repo_url, local_path=None):
        Clones a GitHub repository to a local directory.
    collect_commits(repo_path):
        Collects commit information from a local git repository and returns it as a pandas DataFrame.
    get_commits_df(repo_url):
        Main function to clone a repository and collect commits, saving the data to CSV files.
    get_monthly_commits(df):
        Consolidates the commits data by month to give a time series for modeling, saving the data to a CSV file.
Usage:
    To run the script, use the following command:
    python github_gather.py "<owner>/<repo>"
"""

import os
import pandas as pd
from datetime import datetime
import subprocess
import sys
import shutil

def install_gitpython():
    """Install GitPython if not already installed"""
    try:
        import git
        print("Git already installed")
        return git
    except ImportError:
        print("Installing Git")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'GitPython'])
        import git
        return git

# Install GitPython
git = install_gitpython()

# Functions to collect GitHub commits
def clone_github_repo(repo_url, local_path=None):
    """
    Clone a GitHub repository to a local directory
    
    Parameters:
    -----------
    repo_url : str
        URL of the GitHub repository
    local_path : str, optional
        Local path to clone the repository. 
        If None, uses the repository name in current directory
    
    Returns:
    --------
    str
        Path to the cloned repository
    """
    # If no local path specified, use repo name
    if local_path is None:
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        local_path = os.path.join(os.getcwd(), repo_name)
    
    # Ensure directory doesn't exist or is empty
    if os.path.exists(local_path):
        print(f"Directory {local_path} already exists. Skipping clone.")
    else:
        # Clone the repository
        git.Repo.clone_from(repo_url, local_path)
        print(f"Repository cloned to {local_path}")
    
    return local_path

def collect_commits(repo_path):
    """
    Collect commit information from a local git repository
    
    Parameters:
    -----------
    repo_path : str
        Path to the local git repository
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with commit details
    """
    # Open the repository
    repo = git.Repo(repo_path)
    
    # Collect commit information
    commits_data = []
    for commit in repo.iter_commits():
        commit_info = {
            'hash': commit.hexsha,
            'author': commit.author.name,
            'author_email': commit.author.email,
            'date': commit.authored_datetime,
            'message': commit.message.strip(),
            'additions': commit.stats.total['insertions'],
            'deletions': commit.stats.total['deletions'],
            'files_changed': commit.stats.total['files']
        }
        commits_data.append(commit_info)
        print(commit.authored_datetime, end='..')
    
    # Convert to DataFrame
    df_commits = pd.DataFrame(commits_data)
    
    return df_commits

def get_commits_df(repo_url, repo_name):
    """
    Main function to clone repo and collect commits
    
    Parameters:
    -----------
    repo_url : str
        URL of the GitHub repository
    """
    # Clone the repository
    repo_path = clone_github_repo(repo_url)
    package = repo_name.replace('/', '-')

    # Ensure data directory exists
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Collect commits
    df_commits = collect_commits(repo_path)
    df_commits.to_csv('data/' + package + '-commits_w_desc.csv', index=False)

    # Reformat df to clean up 
    df = df_commits[['hash','author','date','additions','deletions']]
    df.columns = ['commit_id','author','date','lines_added','lines_removed']
    
    # Save to CSV
    output_file = os.path.join(data_dir, package + '-monthly.csv')
    df.to_csv(output_file, index=False)
    print(f"\nCommits collected. Total commits: {len(df)}")
    print(f"Saved commits to {output_file}")
    
    return df

# Create monthly data frame
def get_monthly_commits(df, repo_name):
    """
    Consolidates the commits data by month to give a time series for modeling
    """
    df.loc[:, 'date'] = pd.to_datetime(df['date'], utc=True)

    df1 = df.groupby(pd.Grouper(key='date', freq='ME')).agg({
        'author': 'nunique',          # Count unique authors
        'lines_added': 'sum',           # Total lines added
        'lines_removed': 'sum',           # Total lines removed
    }).reset_index()

    df1['total_changes'] = df1['lines_added'] + df1['lines_removed']
    df1.drop(['lines_added', 'lines_removed'], axis=1, inplace=True)
    df1.columns = ['date', 'contributors', 'total_changes']
    print("Monthly dataframe shape =", df1.shape)

    package = repo_name.replace('/', '-')
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    output_file = os.path.join(data_dir, package + '-monthly.csv')
    df1.to_csv(output_file)
    print(f"Saved monthly data to {output_file}")

    return df1


def collect(repo_name):
    """
    To run: 
    python oss_lifecycle/github_gather.py <owner>/<repo> (from root folder)
    """
    if not "/" in repo_name:
        print("Please provide a GitHub repository name in format '<owner>/<repo>'.")
        # EXAMPLES
        # repo_name = 'jupyterlab/jupyter-ai'
        # repo_name = 'jupyter-server/jupyter-scheduler'
        # repo_name = 'pandas-dev/pandas'
        # repo_name = 'jupyterlab/jupyterlab'
        # repo_name = 'langchain-ai/langchain'
        # repo_name = 'langchain-ai/langchain-aws'        
    else:  
        # repo_name = sys.argv[1]
        owner, repo = repo_name.split('/', 1)
        print(f"Owner: {owner} | Repo: {repo}")
        repo_url = "https://github.com/" + repo_name + ".git"
        df = get_commits_df(repo_url, repo_name)
        df1 = get_monthly_commits(df, repo_name)
        shutil.rmtree(repo)



# Main run
if __name__ == "__main__":
    """
    To run: 
    python oss_lifecycle/github_gather.py <owner>/<repo> (from root folder)
    """
    if len(sys.argv) < 2:
        print("Please provide a GitHub repository name in format '<owner>/<repo>'.")
        # EXAMPLES
        # repo_name = 'jupyterlab/jupyter-ai'
        # repo_name = 'jupyter-server/jupyter-scheduler'
        # repo_name = 'pandas-dev/pandas'
        # repo_name = 'jupyterlab/jupyterlab'
        # repo_name = 'langchain-ai/langchain'
        # repo_name = 'langchain-ai/langchain-aws'        
    else:  
        repo_name = sys.argv[1]
        collect(repo_name)
