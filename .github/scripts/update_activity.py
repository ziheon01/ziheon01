import os
import re
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
USER_NAME = REPO_NAME.split("/")[0]

def fetch_user_orgs():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = "https://api.github.com/user/orgs?per_page=100"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching orgs: {response.text}")
        return []
    return [org["login"] for org in response.json()]

def fetch_open_source_activity(org_exclusions):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    exclude_orgs = " ".join(f"-org:{org}" for org in org_exclusions)
    query = f"is:pr is:merged author:{USER_NAME} -user:{USER_NAME} {exclude_orgs} is:public sort:created-desc"
    url = f"https://api.github.com/search/issues?q={query}&per_page=10"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching data: {response.text}")
        return []

    return response.json().get("items", [])

def format_activity(items):
    if not items:
        return "No recent open source contributions found."

    lines = []
    for item in items:
        title = item["title"]
        url = item["html_url"]
        repo_url = item["repository_url"]
        repo_name = repo_url.replace("https://api.github.com/repos/", "")
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
    orgs = fetch_user_orgs()
    print(f"Excluding orgs: {orgs}")
    items = fetch_open_source_activity(orgs)
    content = format_activity(items)
    update_readme(content)
