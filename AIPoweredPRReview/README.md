# AI-Powered GitHub PR Review with Engineering Efficiency Metrics

AI-assisted pre-review for GitHub Pull Requests that analyzes diffs, computes engineering efficiency metrics, visualizes a merge readiness heatmap, and generates actionable feedback using OpenAI GPT.

## Features

- AI code review on PR diffs with concise, prioritized feedback.
- Engineering efficiency metrics: files changed, lines added/deleted, total changes, commits count, PR open duration.
- Review comments sentiment and themes using NLP.
- CI status summary for the PR head commit.
- Merge readiness heatmap that scores key metrics and signals “good to merge” at a glance.
- Streamlit UI for quick testing and demos.


## Quick Start

1) Clone and enter the repo:
```
- git clone https://github.com/jishnunand/genai-poc-projects.git
```

- cd AIPoweredPRReview

2) Install dependencies:

- pip install -r requirements.txt
- Or: pip install streamlit openai requests pandas seaborn matplotlib

3) Configure secrets:

- Option A: Streamlit secrets in .streamlit/secrets.toml
- GITHUB_TOKEN = "your_github_token"
- OPENAI_API_KEY = "your_openai_api_key"
- Option B: Environment variables
- export GITHUB_TOKEN="your_github_token"
- export OPENAI_API_KEY="your_openai_api_key"

4) Run the app:

- streamlit run app.py

5) Use it:

- Paste a GitHub PR URL like https://github.com/owner/repo/pull/123 and click Analyze PR.


## App Overview

- Engineering Metrics: Computes files changed, lines added/deleted, total changes, commits count, and PR open duration from GitHub API.
- AI Review: Sends unified diff chunks to OpenAI for a clear summary, quality suggestions, efficiency/readability findings, and general feedback.
- Review Comments NLP: Summarizes tone and common themes of existing review comments.
- CI Status: Displays the latest status for the PR head commit.
- Merge Readiness Heatmap: Normalizes scores for lines changed, PR duration, commits, files changed, and CI pass/fail to visualize readiness.


## Files

- app.py: Streamlit app that powers the dashboard and analysis.
- .streamlit/secrets.toml: Optional secure storage for tokens (not committed).
- requirements.txt: Python dependencies.


## Configuration

- GITHUB_TOKEN requires read access to the target repository and PRs.
- OPENAI_API_KEY requires access to GPT-4 or a suitable model configured in the app.
- Thresholds for the heatmap scoring are configurable in build_merge_heatmap within app.py:
- Lines changed target: 0–500
- PR duration target: 0–72 hours
- Commits target: 0–10
- Files changed target: 0–20
- CI status: success = 1.0, otherwise 0.2 by default


## Security and Privacy

- Never commit secrets. Use GitHub/Streamlit secrets or environment variables.
- Large diffs may contain sensitive code. Consider redaction rules or repository allowlists.


## GitHub Actions (Optional)

Automate pre-review on each PR:

- .github/workflows/pr-review.yml:
- name: PR Pre-Review with AI
- on:
    - pull_request:
        - types: [opened, synchronize, reopened]
- jobs:
    - review:
        - runs-on: ubuntu-latest
        - steps:
            - uses: actions/checkout@v3
            - uses: actions/setup-python@v4
                - with:
                    - python-version: '3.10'
            - run: pip install -r requirements.txt
            - env:
                - GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}
                - OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}
            - run: python pr_review.py "\${{ github.event.pull_request.html_url }}"
- pr_review.py should:
    - Parse the PR URL
    - Fetch PR data and diffs
    - Generate AI feedback
    - Post a comment via GitHub Issues API


## Example Output

- Metrics:
    - Total files changed: 5
    - Total lines added: 120
    - Total lines deleted: 30
    - Total lines changed: 150
    - Number of commits: 4
    - PR open duration (hours): 36.75
- Heatmap: Green-leaning scores for small diffs and passing CI; red/yellow when large or slow PRs.
- AI Feedback: Summary of changes, concrete improvement suggestions, readability/performance flags, and unit test gaps.
- Comments Analysis: Mostly constructive tone; requests for naming consistency and more tests.
- CI: success – all checks passed.


## Troubleshooting

- GitHub API 403/404: Ensure GITHUB_TOKEN has required scope and repo access; check URL format.
- Empty diffs: Verify PR has changes and the token can read files endpoint.
- OpenAI errors: Verify OPENAI_API_KEY and model availability; reduce tokens for very large diffs.
- Charts not showing: Ensure matplotlib and seaborn installed; check Streamlit logs.


## Roadmap

- Adaptive chunking for very large diffs with per-file analysis.
- Security scanning (SAST/Dependency) signals in dashboard.
- Org-wide dashboards with trend analysis and developer profiles.
- Customizable scoring profiles per team/stack.


## License

- MIT © 2025 Jishnunand P K