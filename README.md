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
- Configurable via a `config.json` file.
- Class-based structure for better organization.

## Prerequisites

- Python 3 (developed and tested with Python 3.x)
- Git command-line tool installed and accessible in your system's PATH.

## Setup & Configuration

1.  **Get the Script:**
    Download or copy the `git_auto_script.py` file to your local machine.

2.  **Create and Configure `config.json` (IMPORTANT!):**
    Configuration for the script, including your Git credentials and repository details, is managed through a `config.json` file.

    a.  **Create `config.json`:**
        In the same directory as `git_auto_script.py`, copy the example configuration file `config.example.json` to a new file named `config.json`.
        On Linux/macOS, you can do this with:
        ```bash
        cp config.example.json config.json
        ```
        On Windows:
        ```bash
        copy config.example.json config.json
        ```

    b.  **Edit `config.json`:**
        Open `config.json` in a text editor and replace the placeholder values with your actual details. The file should look like this:

        ```json
        {
          "BASE_REPO_URL": "https://github.com/your-user/your-repo.git",
          "GIT_USERNAME": "YOUR_GITHUB_USERNAME",
          "GIT_TOKEN": "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN",
          "LOCAL_REPO_PATH": "./my-local-clone-path"
        }
        ```

        *   **`BASE_REPO_URL`**: The URL of the Git repository you want to manage (e.g., `"https://github.com/omnia-projetcs/auto-shards.git"`).
        *   **`GIT_USERNAME`**: Your GitHub username.
        *   `GIT_TOKEN`: Your GitHub Personal Access Token (PAT). **Do not use your GitHub password.**
            To create a PAT:
            1.  Ensure your email address is verified on GitHub.
                2.  Navigate to your GitHub settings: Click on your profile picture in the upper-right corner, then click **Settings**.
                3.  In the left sidebar, scroll down and click **Developer settings**.
                4.  In the left sidebar, under **Personal access tokens**, click **Tokens (classic)**.
                    *(For a more secure, fine-grained token, you can select "Fine-grained tokens". This allows you to scope access to specific repositories and permissions, such as "Contents: Read & write" for the target repository. However, "Tokens (classic)" with the `repo` scope is often simpler for general command-line access to all your repositories.)*
                5.  Click **Generate new token**, and then confirm by clicking **Generate new token (classic)** if prompted.
                6.  In the **Note** field, give your token a descriptive name (e.g., "git_auto_script_token").
                7.  Set an **Expiration** for your token (e.g., 30 days, 90 days, or custom). GitHub recommends setting an expiration.
                8.  Under **Select scopes**, check the box next to **`repo`**. This will grant the token full control of private repositories, including read and write access, which is needed by this script to clone, pull, and push.
                9.  Scroll down and click **Generate token**.
                10. **Important:** Copy your new PAT immediately. GitHub will not show it to you again. Store it securely until you add it to your `config.json` file.
        *   **`LOCAL_REPO_PATH`**: The local directory path where the script will clone the repository (e.g., `"./auto-shards-repo-json-config"`). This will be created if it doesn't exist.

3.  **Security Warning & `.gitignore`:**
    *   **Crucial:** The `config.json` file contains your sensitive credentials (`GIT_TOKEN`). **DO NOT COMMIT `config.json` TO ANY GIT REPOSITORY.**
    *   The project includes a `.gitignore` file that lists `config.json` to help prevent accidental commits of this file.
    *   Hardcoding credentials, even in a local JSON file, carries risks. For production or highly sensitive environments, consider more advanced credential management solutions like environment variables, dedicated secrets management tools, or SSH-based authentication for Git.
    *   The script includes a check to prevent running if it detects the default placeholder values from `config.example.json` in your `config.json`. This is a safety measure, not a substitute for secure credential handling.

## How to Run

1.  Navigate to the directory where you saved `git_auto_script.py`.
2.  Ensure you have configured your credentials as described in the "Setup & Configuration" section.
3.  Execute the script from your terminal:
    ```bash
    python git_auto_script.py
    ```

Alternatively, on Unix-like systems (Linux/macOS), you can make the script executable first:
  ```bash
  chmod +x git_auto_script.py
  ```
Then run it directly:
  ```bash
  ./git_auto_script.py
  ```
This is possible due to the shebang line added at the top of the script.

## Functionality Details

-   **Target Repository:** The script is configured to work with the repository specified in `config.json` (`BASE_REPO_URL`).
-   **Local Clone:** A local copy of the repository will be stored in the directory specified in `config.json` (`LOCAL_REPO_PATH`).
-   **Output Files:** The script creates/updates `info1.txt` through `info5.txt` in an `output/` subdirectory within the cloned local repository. Each file contains the timestamp of its creation/update.
-   **Conflict Resolution:** If a direct `git push` fails due to new commits on the remote (non-fast-forward error), the script will automatically:
    1.  Attempt `git pull origin main --rebase` to rebase local commits on top of remote changes.
    2.  Attempt `git push origin main --force` to update the remote branch.
-   **Idempotency:** Running the script multiple times will update the timestamped files and attempt to push the new state to the repository.

## Disclaimer

This script uses `git push --force`. Force pushing can overwrite remote history and should be used with caution, especially in collaborative environments. Ensure you understand the implications before running this script. The authors are not responsible for any data loss or repository issues caused by the use of this script.