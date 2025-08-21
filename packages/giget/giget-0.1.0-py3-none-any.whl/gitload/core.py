import requests, os

def download_github_dir(owner, repo, path, branch="master", save_dir="."):
    """Download a GitHub folder recursively."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    response = requests.get(url).json()

    if isinstance(response, dict) and response.get("message"):
        raise Exception(f"GitHub API error: {response['message']}")

    for item in response:
        item_path = os.path.join(save_dir, item["path"])
        if item["type"] == "file":
            os.makedirs(os.path.dirname(item_path), exist_ok=True)
            print(f"Downloading {item['download_url']}")
            file_data = requests.get(item["download_url"]).content
            with open(item_path, "wb") as f:
                f.write(file_data)
        elif item["type"] == "dir":
            download_github_dir(owner, repo, item["path"], branch, save_dir)
