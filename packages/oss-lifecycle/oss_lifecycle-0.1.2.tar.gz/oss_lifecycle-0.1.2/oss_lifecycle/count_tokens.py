import os
import sys
import shutil
from transformers import AutoTokenizer
import github_gather

def tokenize_and_count(repo_path):
    """
    Tokenizes all files in a GitHub repository and counts the total number of tokens.

    Args:
        repo_path (str): Path to the local GitHub repository.

    Returns:
        int: Total number of tokens in the repository.
    """
    # Load the StarCoder2 tokenizer
    tokenizer = AutoTokenizer.from_pretrained("huggingface/CodeBERTa-small-v1")

    total_tokens = 0

    # Walk through all files in the repository
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            if any(substring in file_path for substring in [".md", ".lock", ".png", ".jpeg", ".ipynb", ".git", "yarn", ".csv"]):
                # Skip non-code files
                print(f"Skipping file: {file_path}")
            else:
                try:
                    # Read the file content
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Tokenize the content and count tokens
                    tokens = tokenizer.encode(content, truncation=False)
                    total_tokens += len(tokens)
                    print(f"File: {file_path}, Tokens: {len(tokens)}")
                except (UnicodeDecodeError, FileNotFoundError):
                    # Skip files that cannot be read
                    print(f"Skipping file: {file_path}")

    return total_tokens


# Main run
if __name__ == "__main__":
    """
    To run: 
    python oss_lifecycle/count_tokens.py <owner>/<repo> (from root folder)
    """
    if len(sys.argv) < 2:
        print("Please provide a GitHub repository name in format '<owner>/<repo>'.")
    else:
        repo_name = sys.argv[1]
        owner, repo = repo_name.split('/', 1)
        print(f"Owner: {owner} | Repo: {repo}")
        repo_url = "https://github.com/" + repo_name + ".git"
        repo_path = github_gather.clone_github_repo(repo_url)
        total_tokens = tokenize_and_count(repo_path)
        print(f"Total tokens in repository {repo_name}: {total_tokens}")
        shutil.rmtree(repo_path) 
    