import sys
from .core import download_github_dir

def main():
    if len(sys.argv) < 2:
        print("Usage: gitload <github-folder-url>")
        sys.exit(1)

    url = sys.argv[1].rstrip("/")

    # Example: https://github.com/jasmcaus/opencv-course/tree/master/Resources/Photos
    try:
        parts = url.split("github.com/")[1].split("/")
        owner, repo, tree, branch, *path = parts
        folder_path = "/".join(path)
    except Exception:
        print("Invalid GitHub URL format.")
        sys.exit(1)

    download_github_dir(owner, repo, folder_path, branch, save_dir=".")
    print("✅ Download complete!")
