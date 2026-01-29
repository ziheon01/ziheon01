import os
import re
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
USER_NAME = REPO_NAME.split("/")[0]

def fetch_open_source_activity():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    # Query: Merged PRs, Author is me, Not my repos, Public, Sorted by creation
    query = f"is:pr is:merged author:{USER_NAME} -user:{USER_NAME} is:public sort:created-desc"
    url = f"https://api.github.com/search/issues?q={query}&per_page=10"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching data: {response.text}")
        return []
    
    data = response.json()
    return data.get("items", [])

def format_activity(items):
    if not items:
        return "No recent open source contributions found."
    
    lines = []
    for item in items:
        title = item["title"]
        url = item["html_url"]
        repo_url = item["repository_url"]
        # API returns repo url as https://api.github.com/repos/owner/repo
        # We want https://github.com/owner/repo
        repo_name = repo_url.replace("https://api.github.com/repos/", "")
        
        # Markdown format: - [RepoName] [PR Title](URL)
        line = f"- 🚀 Contributed to [{repo_name}](https://github.com/{repo_name}) - [{title}]({url})"
        lines.append(line)
        
    return "\n".join(lines)

def update_readme(content):
    file_path = "README.md"
    with open(file_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
    
    start_marker = "<!--START_SECTION:activity-->"
    end_marker = "<!--END_SECTION:activity-->"
    
    pattern = f"{start_marker}.*?{end_marker}"
    replacement = f"{start_marker}\n{content}\n{end_marker}"
    
    new_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)
    
    if new_content != readme_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("README.md updated.")
    else:
        print("No changes needed for README.md.")

if __name__ == "__main__":
    items = fetch_open_source_activity()
    content = format_activity(items)
    update_readme(content)
