import os
import re
import pandas as pd
import numpy as np
import sys
import boto3
import json


def make_activity_df(monthly_commits_file_w_desc, month):
    """
    Generates an activity dataframe for the month
    
    Parameters:
    -----------
    monthly_commits_file_w_desc : str
        Path to the monthly commits file with descriptions
    month : str
        Month to generate the report for
    """
    # Load the data
    df = pd.read_csv(monthly_commits_file_w_desc)
    
    # Filter by month
    df['YYYY-MM'] = [j[:7] for j in df['date']]
    df = df[df['YYYY-MM'] == month]
    
    # Save to CSV
    output_file = 'data/' + month + '-activity-report.csv'
    df.to_csv(output_file, index=False)
    print(f"Activity report for {month} saved to {output_file}")
    
    return df


def call_claude(prompt):
    # Create a Bedrock Runtime client
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime', 
        region_name='us-west-2'  # adjust region as needed
    )
    
    # Prepare the request payload
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "top_p": 0.9
    })
    
    # Make the API call
    try:
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-5-haiku-20241022-v1:0',
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

PROMPT = """Combine the following text into a single summary paragraph, 
            retaining the first line as the title with no line return. 
            Remove any sentences that contain the string 'commit'. 
            Drop any lines that begin with SHA256.
            Do not say "Here's the summary paragraph:"
            Do not leave a line after the title.
            Don't use the words "pull request"
            Text: """

def make_activity_report(df):
    all_text = []
    df = df[['author','message']]
    i = 0
    for j in range(len(df)):
        if df["author"].iloc[j] != "pre-commit-ci[bot]":
            i += 1
            author = df["author"].iloc[j]
            msg = df["message"].iloc[j]
            prompt = PROMPT
            text = prompt + msg
            response = call_claude(text)
            response = response.replace("\n", ". ")
            print(f"{i}. {response}", end='\n\n')
            all_text.append(response)
    all_text = "\n\n".join(all_text)
    prompt = """Summarize the main points of the following text."""
    response = call_claude(prompt + all_text)
    response = response.replace("\n", ". ")
    print(f"{response}")
    return None


# Main run
if __name__ == "__main__":
    """
    To run: 
    First, collect the repo data by running from the root folder:
        python oss_lifecycle/github_gather.py <owner>/<repo>

    Next, run
        python oss_lifecycle/activity_report.py <owner>/<repo> YYYY-MM (from root folder)
    """
    if len(sys.argv) < 3:
        print("Please provide a GitHub repository name in format `<owner>/<repo> YYYY-MM`> .")
        # EXAMPLES
        # repo_name = 'jupyterlab/jupyter-ai'
        # repo_name = 'jupyter-server/jupyter-scheduler'
        # repo_name = 'pandas-dev/pandas'
        # repo_name = 'jupyterlab/jupyterlab'
        # repo_name = 'langchain-ai/langchain'
        # repo_name = 'langchain-ai/langchain-aws'        
    else:  
        repo_name = sys.argv[1]
        owner, repo = repo_name.split('/')
        repo_string = owner + '-' + repo
        month = sys.argv[2]
        print(f"Owner: {owner} | Repo: {repo}")
        commits_file = 'data/' + repo_string + '-commits_w_desc.csv'
        df = make_activity_df(commits_file, month)
        make_activity_report(df)
