import streamlit as st
import requests
import openai
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# API keys (replace with your own or use Streamlit secrets)
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN") or "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or "YOUR_OPENAI_API_KEY"
openai.api_key = OPENAI_API_KEY

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def extract_pr_info(pr_url):
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        st.error("Invalid GitHub PR URL format.")
        return None, None, None
    return match.group(1), match.group(2), int(match.group(3))

def fetch_github_api(url):
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        st.error(f"GitHub API error {res.status_code}: {res.json().get('message', '')}")
        return None
    return res.json()

def fetch_pr_data(owner, repo, pr_number):
    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    pr_data = fetch_github_api(pr_url)
    if not pr_data:
        return None, None, None, None, None
    files_url = pr_data.get('url') + "/files"
    commits_url = pr_data.get('url') + "/commits"
    comments_url = pr_data.get('url') + "/comments"
    status_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{pr_data.get('head')['sha']}/status"

    files = fetch_github_api(files_url)
    commits = fetch_github_api(commits_url)
    comments = fetch_github_api(comments_url)
    status = fetch_github_api(status_url)

    return pr_data, files, commits, comments, status

def calculate_efficiency_metrics(files, commits, pr_data):
    total_files = len(files) if files else 0
    total_additions = sum(f.get('additions', 0) for f in files) if files else 0
    total_deletions = sum(f.get('deletions', 0) for f in files) if files else 0
    total_changes = sum(f.get('changes', 0) for f in files) if files else 0
    total_commits = len(commits) if commits else 0
    created_at = datetime.strptime(pr_data['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    merged_at = pr_data.get('merged_at')
    closed_at = pr_data.get('closed_at')
    merged_time = None
    closed_time = None
    if merged_at:
        merged_time = (datetime.strptime(merged_at, "%Y-%m-%dT%H:%M:%SZ") - created_at).total_seconds()/3600
    if closed_at:
        closed_time = (datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ") - created_at).total_seconds()/3600

    return {
        "Total files changed": total_files,
        "Total lines added": total_additions,
        "Total lines deleted": total_deletions,
        "Total lines changed": total_changes,
        "Number of commits": total_commits,
        "PR open duration (hours)": round(merged_time or closed_time or 0, 2)
    }

def prepare_diff_text(files):
    diffs = []
    for file in files or []:
        if "patch" in file:
            diffs.append(f"File: {file['filename']}\n{file['patch']}\n")
    return "\n".join(diffs)

def analyze_pr_code_diff(code_diff):
    prompt = f"""
You are an expert software engineer. Review the following code diff from a pull request:
{code_diff}

Please provide:
1. A summary of the code changes.
2. Suggestions on code quality improvements.
3. Any noticeable efficiency or readability issues.
4. General feedback to help the author improve the PR.

Be concise and clear.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600,
        temperature=0.3,
    )
    return response['choices'][0]['message']['content']

def analyze_review_comments(comments):
    text = " ".join(comment['body'] for comment in comments or [])
    if not text:
        return "No review comments found."
    prompt = f"""
Analyze the sentiment and helpfulness of the following code review comments:
{text}

Summarize the tone (positive, negative, neutral) and major themes in the feedback.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert AI assistant specializing in code review analysis."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.5,
    )
    return response['choices'][0]['message']['content']

def summarize_ci_status(status):
    if not status or status.get('state') is None:
        return "CI status not available."
    state = status['state']
    desc = status.get('description', '')
    return f"CI Status: {state}. {desc}"

def normalize(value, vmin, vmax):
    if vmax - vmin == 0:
        return 0
    return max(0, min(1, (value - vmin)/(vmax - vmin)))

def build_merge_heatmap(metrics):
    lines_changed_score = 1 - normalize(metrics["Total lines changed"], 0, 500)
    pr_duration_score = 1 - normalize(metrics["PR open duration (hours)"], 0, 72)
    commits_score = 1 - normalize(metrics["Number of commits"], 0, 10)
    files_changed_score = 1 - normalize(metrics["Total files changed"], 0, 20)
    ci_pass_score = 1 if "success" in metrics.get("CI status", "").lower() else 0.2

    data = {
        "Metric": [
            "Lines Changed (Lower Better)",
            "PR Duration (Hours, Lower Better)",
            "Number of Commits (Lower Better)",
            "Files Changed (Lower Better)",
            "CI Status (Pass=1/Fail=0)"
        ],
        "Score": [
            lines_changed_score,
            pr_duration_score,
            commits_score,
            files_changed_score,
            ci_pass_score
        ]
    }

    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    df = pd.DataFrame(data).set_index("Metric")
    cmap = sns.diverging_palette(150, 10, s=80, l=55, n=9, as_cmap=True)
    fig, ax = plt.subplots(figsize=(7, 2.5))
    sns.heatmap(df.T, annot=True, cmap=cmap, vmin=0, vmax=1, cbar=False, linewidths=1, ax=ax)
    ax.set_title("PR Merge Readiness Heatmap")
    st.pyplot(fig)

st.title("GitHub PR Review with AI and Engineering Efficiency Metrics")

pr_url = st.text_input("Enter GitHub Pull Request URL")

if st.button("Analyze PR"):
    if not pr_url:
        st.warning("Please enter a GitHub PR URL.")
    else:
        owner, repo, pr_number = extract_pr_info(pr_url)
        if owner is None:
            st.stop()

        with st.spinner(f"Fetching PR data for {owner}/{repo} PR #{pr_number}..."):
            pr_data, files, commits, comments, status = fetch_pr_data(owner, repo, pr_number)

        if not pr_data or not files:
            st.info("No PR data or files found.")
        else:
            metrics = calculate_efficiency_metrics(files, commits, pr_data)
            metrics["CI status"] = summarize_ci_status(status)

            st.subheader("Engineering Efficiency Metrics")
            for k, v in metrics.items():
                st.write(f"**{k}:** {v}")

            build_merge_heatmap(metrics)

            pr_diff = prepare_diff_text(files)
            if pr_diff:
                with st.spinner("Analyzing PR diff with OpenAI..."):
                    feedback = analyze_pr_code_diff(pr_diff)
                st.subheader("AI Code Review Feedback")
                st.text(feedback)
            else:
                st.info("No diff data to analyze.")

            with st.spinner("Analyzing review comments with OpenAI..."):
                comment_analysis = analyze_review_comments(comments)
            st.subheader("Review Comments Analysis")
            st.text(comment_analysis)

            st.subheader("CI / Test Status")
            st.write(metrics["CI status"])
