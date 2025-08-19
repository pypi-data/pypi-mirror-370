"""
#!/bin/bash
Code to collect all commits and related information for a list of repos
"""

import os

repo_list = [
             "langchain-ai/langchain-aws",
             "jupyterlab/jupyter-ai",
             "jupyter-server/jupyter-scheduler",
            ]

for repo in repo_list:
    os.system('python oss_lifecycle/github_gather.py ' + repo)
    print(repo, '..Done')
