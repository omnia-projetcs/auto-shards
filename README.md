# Automated Git Repository Updater Script

## Description

This Python script automates the process of managing a Git repository. It clones a specified repository (or pulls updates if it already exists locally), creates five uniquely named text files (`info1.txt` to `info5.txt`) containing the current timestamp within an `output` subdirectory, and then commits and pushes these files to the `main` branch of the remote repository.

The script is designed to handle potential push conflicts by first attempting to pull changes from the remote using a rebase strategy, and then force-pushing the local changes.

## Features

- Clones a remote Git repository or pulls updates if a local copy exists.
- Creates timestamped text files in an `output/` subdirectory within the repository.
- Commits the changes with a standardized message.
- Pushes changes to the `main` branch.
- Handles push conflicts by attempting `git pull --rebase` followed by `git push --force`.
- Configurable via constants in the script's main execution block.
- Class-based structure for better organization.

## Prerequisites

- Python 3 (developed and tested with Python 3.x)
- Git command-line tool installed and accessible in your system's PATH.

## Setup & Configuration

1.  **Get the Script:**
    Download or copy the `git_auto_script.py` file to your local machine.

2.  **Configure Credentials (IMPORTANT!):**
    Open `git_auto_script.py` in a text editor. You **MUST** configure your Git credentials and repository details in the `if __name__ == "__main__":` block at the end of the file:

    ```python
    # !!! IMPORTANT SECURITY WARNING !!!
    # You must replace the placeholder GIT_USERNAME and GIT_TOKEN with your
    # actual GitHub username and a Personal Access Token (PAT).
    # Hardcoding credentials directly in the script is a security risk.
    # Consider using environment variables or a more secure credential management
    # system for production use. This script is for demonstration purposes of the
    # requested functionality. Ensure the PAT has the necessary permissions
    # (e.g., 'repo' scope) to clone and push to the specified repository.
    # Do not commit this file with your real credentials to a public repository.
    BASE_REPO_URL = "https://github.com/omnia-projetcs/auto-shards.git" # Target repository
    LOCAL_REPO_PATH = "./auto-shards-repo-class"      # Local directory for the clone
    GIT_USERNAME = "YOUR_GITHUB_USERNAME"             # Replace with your GitHub username
    GIT_TOKEN = "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"   # Replace with your GitHub PAT
    ```

    *   **`BASE_REPO_URL`**: The URL of the Git repository you want to manage.
    *   **`LOCAL_REPO_PATH`**: The local directory where the script will clone the repository. This will be created if it doesn't exist.
    *   **`GIT_USERNAME`**: Your GitHub username.
    *   **`GIT_TOKEN`**: Your GitHub Personal Access Token (PAT). **Do not use your password.**
        *   Create a PAT from your GitHub account settings (Developer settings -> Personal access tokens).
        *   The PAT needs appropriate permissions (scopes) to read and write to the repository (e.g., the `repo` scope).

    **Security Warning:** Hardcoding credentials (like your PAT) directly into a script is a significant security risk, especially if the script is shared or committed to version control. For production or sensitive environments, use more secure methods like environment variables, Git credential helpers, or SSH-based authentication. The check included in the script to prevent running with placeholder credentials is a safety measure, not a replacement for secure credential management.

## How to Run

1.  Navigate to the directory where you saved `git_auto_script.py`.
2.  Ensure you have configured your credentials as described in the "Setup & Configuration" section.
3.  Execute the script from your terminal:
    ```bash
    python git_auto_script.py
    ```

## Functionality Details

-   **Target Repository:** The script is configured to work with `https://github.com/omnia-projetcs/auto-shards.git` by default but can be changed via the `BASE_REPO_URL` constant.
-   **Local Clone:** A local copy of the repository will be stored in the directory specified by `LOCAL_REPO_PATH` (default: `./auto-shards-repo-class`).
-   **Output Files:** The script creates/updates `info1.txt` through `info5.txt` in an `output/` subdirectory within the cloned local repository. Each file contains the timestamp of its creation/update.
-   **Conflict Resolution:** If a direct `git push` fails due to new commits on the remote (non-fast-forward error), the script will automatically:
    1.  Attempt `git pull origin main --rebase` to rebase local commits on top of remote changes.
    2.  Attempt `git push origin main --force` to update the remote branch.
-   **Idempotency:** Running the script multiple times will update the timestamped files and attempt to push the new state to the repository.

## Disclaimer

This script uses `git push --force`. Force pushing can overwrite remote history and should be used with caution, especially in collaborative environments. Ensure you understand the implications before running this script. The authors are not responsible for any data loss or repository issues caused by the use of this script.