#!/usr/bin/env python3
# git_auto_script.py
#
# Purpose:
# This script, structured as a Python class `GitRepoUpdater`, automates the management
# of a Git repository. It clones a specified repository (or pulls updates if it
# already exists locally), creates five text files (info1.txt to info5.txt)
# containing the current date and time within an 'output' subdirectory, and then
# commits and pushes these files to the 'main' branch of the remote repository.
#
# The script handles potential push conflicts by attempting to pull with rebase
# and then force-pushing the changes.
#
# Prerequisites:
# 1. Python 3 installed on your system.
# 2. Git command-line tool installed on your system.
#
# Configuration:
# This script loads its configuration (repository URL, local path, Git username,
# and Git Personal Access Token) from a JSON file named 'config.json'.
# You must create 'config.json' in the same directory as this script.
# You can copy 'config.example.json' to 'config.json' and then edit it
# with your actual details.
#
# !!! IMPORTANT SECURITY WARNING !!!
# Your Git Personal Access Token (PAT) and other configuration details are
# stored in 'config.json'.
# - Ensure 'config.json' is NOT committed to any version control system.
#   The provided .gitignore file should prevent this.
# - Protect 'config.json' as it contains sensitive credentials.
# - For production or highly sensitive environments, consider more secure
#   credential management (e.g., environment variables, vault solutions).
# This script includes a check to prevent running with default placeholder
# values from 'config.example.json' found in your 'config.json'.
#
# How to run:
# 1. Ensure 'config.json' is created and correctly populated with your
#    repository details and credentials (see 'config.example.json').
# 2. Save this script as `git_auto_script.py`.
# 3. Open your terminal or command prompt.
# 4. Navigate to the directory where you saved the script and `config.json`.
# 5. Make the script executable (on Linux/macOS): chmod +x git_auto_script.py
# 6. Run the script: ./git_auto_script.py  (or python3 git_auto_script.py)
#
# What the script does:
# - Initializes a `GitRepoUpdater` object with repository URL, local path,
#   and Git credentials.
# - Clones the repository if it's not found locally.
# - If the local repository exists, it pulls the latest changes from the 'main' branch.
# - Creates/updates five files (info1.txt to info5.txt) in an 'output/' subdirectory
#   within the cloned local repository, each containing the current timestamp.
# - Stages these files, commits them with a predefined message.
# - Pushes the commit to the 'main' branch of the remote repository using credentials.
# - If the push initially fails due to remote changes (non-fast-forward error),
#   it will:
#     1. Attempt to pull the latest changes from 'main' using rebase.
#     2. Attempt to force-push the rebased changes to 'main'.
#
# Local Repository Path:
# The script will create/use a directory specified by `LOCAL_REPO_PATH`
# (default: './auto-shards-repo-class') in the same directory where the script
# is executed. The timestamped files are placed in an 'output' subdirectory therein.
#
# Important:
# - Force pushing can overwrite remote history. Ensure you understand the
#   implications in a collaborative environment. This script is designed
#   based on the requirement to "force l'update".
# - Ensure the target repository (e.g., omnia-projetcs/auto-shards) exists and
#   your PAT has push access.

# --- Script Start ---
import os
import subprocess
from datetime import datetime
import shutil # shutil might be used later for directory cleanup
import json
import sys

class GitRepoUpdater:
    def __init__(self, base_repo_url, local_path, username, token):
        self.local_path = local_path
        self.username = username
        self.token = token
        self.base_repo_url = base_repo_url

        # Parse base_repo_url to construct authenticated_repo_url
        url_parts = base_repo_url.split("://")
        if len(url_parts) > 1:
            host_and_path = url_parts[1]
        else:
            host_and_path = url_parts[0] # In case URL is like 'github.com/user/repo.git'

        self.authenticated_repo_url = f"https://{self.username}:{self.token}@{host_and_path}"

        self.output_dir = os.path.join(self.local_path, "output")

    def clone_or_pull_repo(self):
        """
        Clones a repository using authenticated URL if local_path doesn't exist,
        or pulls if it's a git repository.
        Returns True on success, False on failure.
        """
        try:
            if os.path.exists(self.local_path):
                if os.path.exists(os.path.join(self.local_path, ".git")):
                    print(f"Path '{self.local_path}' exists and is a git repository. Pulling...")
                    try:
                        # For pulling, git usually uses the configured remote URL.
                        # If remote 'origin' is not set to the authenticated URL, this might need adjustment.
                        # However, 'git pull' should respect credentials from .git-credentials or helpers
                        # if the base URL matches. For explicit control, one might update remote URL first.
                        subprocess.run(["git", "pull", "origin", "main"], cwd=self.local_path, check=True, capture_output=True, text=True)
                        print(f"Successfully pulled repository in '{self.local_path}'.")
                        return True
                    except subprocess.CalledProcessError as e:
                        print(f"Error pulling repository in '{self.local_path}': {e.stderr}")
                        return False
                    except FileNotFoundError:
                        print("Error: git command not found. Please ensure git is installed and in your PATH.")
                        return False
                else:
                    print(f"Error: Path '{self.local_path}' exists but is not a git repository.")
                    return False
            else:
                print(f"Path '{self.local_path}' does not exist. Cloning repository from '{self.authenticated_repo_url}' into '{self.local_path}'...")
                try:
                    subprocess.run(["git", "clone", self.authenticated_repo_url, self.local_path], check=True, capture_output=True, text=True)
                    print(f"Successfully cloned repository from '{self.authenticated_repo_url}' to '{self.local_path}'.")
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"Error cloning repository: {e.stderr}")
                    return False
                except FileNotFoundError:
                    print("Error: git command not found. Please ensure git is installed and in your PATH.")
                    return False
        except Exception as e:
            print(f"An unexpected error occurred in clone_or_pull_repo: {e}")
            return False

    def create_info_files(self):
        """
        Creates or updates 5 info files with the current timestamp in self.output_dir.
        Returns True on success, False on failure.
        """
        try:
            # Ensure the output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
            print(f"Ensured output directory exists: '{self.output_dir}'")

            now = datetime.now()
            timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
            filenames = [f"info{i}.txt" for i in range(1, 6)]

            for filename in filenames:
                file_path = os.path.join(self.output_dir, filename)
                try:
                    with open(file_path, 'w') as f:
                        f.write(timestamp_str)
                    print(f"File '{file_path}' created/updated in output directory with timestamp: {timestamp_str}")
                except (IOError, OSError) as e:
                    print(f"Error writing to file '{file_path}': {e}")
                    return False
            return True
        except Exception as e:
            print(f"An unexpected error occurred in create_info_files: {e}")
            return False

    def commit_and_push_changes(self, commit_message):
        """
        Adds, commits, and pushes changes in the git repository at self.local_path.
        Uses self.authenticated_repo_url for push operations.
        If the initial push fails due to non-fast-forward errors,
        it attempts to pull with rebase (using authenticated URL for safety) and then force push.
        Restores original working directory regardless of success or failure.
        Returns True on success, False on failure.
        """
        original_cwd = os.getcwd()
        try:
            if not os.path.isdir(os.path.join(self.local_path, ".git")):
                print(f"Error: '{self.local_path}' is not a git repository.")
                return False

            os.chdir(self.local_path)
            print(f"Changed directory to '{self.local_path}'")

            # Git Add
            try:
                print("Executing 'git add .'")
                result = subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
                # print(f"'git add .' successful. Output:\n{result.stdout}") # stdout can be verbose
                print("'git add .' successful.")
            except subprocess.CalledProcessError as e:
                print(f"Error during 'git add .':\n{e.stderr}")
                return False
            except FileNotFoundError:
                print("Error: git command not found. Please ensure git is installed and in your PATH.")
                return False

            # Git Commit
            try:
                print(f"Executing 'git commit -m \"{commit_message}\"'")
                result = subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True, text=True)
                # print(f"'git commit' successful. Output:\n{result.stdout}") # stdout can be verbose
                print("'git commit' successful.")
            except subprocess.CalledProcessError as e:
                # If "nothing to commit" or "no changes added", it's not necessarily a failure for the script's purpose.
                if "nothing to commit" in e.stdout.lower() or "no changes added to commit" in e.stdout.lower() or \
                   "nothing to commit" in e.stderr.lower() or "no changes added to commit" in e.stderr.lower():
                    print("No changes to commit.")
                    return True # Considered success as there's nothing to push.
                print(f"Error during 'git commit':\n{e.stderr}")
                return False
            except FileNotFoundError:
                print("Error: git command not found. Please ensure git is installed and in your PATH.")
                return False

            # Git Push using authenticated URL
            try:
                print(f"Executing 'git push <authenticated_url> main'") # URL hidden for security in log
                # Using self.authenticated_repo_url directly in push command
                result = subprocess.run(["git", "push", self.authenticated_repo_url, "main"], check=True, capture_output=True, text=True)
                # print(f"'git push' successful. Output:\n{result.stdout}") # stdout can be verbose
                print("'git push' successful.")
            except subprocess.CalledProcessError as e:
                push_error_stderr = e.stderr.lower()
                if 'non-fast-forward' in push_error_stderr or 'rejected' in push_error_stderr or 'failed to push some refs to' in push_error_stderr:
                    print(f"Non-fast-forward error detected during 'git push':\n{e.stderr}")
                    print("Attempting to pull with rebase and force push using authenticated URL...")

                    # Git Pull --rebase (using authenticated URL for remote 'origin' might be complex here)
                    # For simplicity, assuming 'origin' is correctly configured or using default behavior
                    # A more robust way would be to specify the authenticated URL for pull too:
                    # git pull https://user:token@host/path.git main --rebase
                    try:
                        print(f"Executing 'git pull <authenticated_url> main --rebase'") # URL hidden for security
                        pull_rebase_result = subprocess.run(["git", "pull", self.authenticated_repo_url, "main", "--rebase"], check=True, capture_output=True, text=True)
                        # print(f"'git pull --rebase' successful. Output:\n{pull_rebase_result.stdout}")
                        print("'git pull --rebase' successful.")
                    except subprocess.CalledProcessError as pull_e:
                        print(f"Error during 'git pull --rebase':\n{pull_e.stderr}")
                        return False
                    except FileNotFoundError:
                        print("Error: git command not found during pull --rebase.")
                        return False

                    # Git Push --force using authenticated URL
                    try:
                        print(f"Executing 'git push <authenticated_url> main --force'") # URL hidden for security
                        force_push_result = subprocess.run(["git", "push", self.authenticated_repo_url, "main", "--force"], check=True, capture_output=True, text=True)
                        # print(f"'git push --force' successful. Output:\n{force_push_result.stdout}")
                        print("'git push --force' successful.")
                    except subprocess.CalledProcessError as force_push_e:
                        print(f"Error during 'git push --force':\n{force_push_e.stderr}")
                        return False
                    except FileNotFoundError:
                        print("Error: git command not found during push --force.")
                        return False
                else:
                    print(f"Error during 'git push':\n{e.stderr}") # Other push error
                    return False
            except FileNotFoundError:
                print("Error: git command not found during initial push.")
                return False
            return True
        except Exception as e:
            print(f"An unexpected error occurred in commit_and_push_changes: {e}")
            return False
        finally:
            os.chdir(original_cwd)
            print(f"Restored original working directory to '{original_cwd}'")

    def run_update(self):
        print("Starting repository update process...")
        # commit_message = f"Automated class-based update: info files to output directory - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        commit_message = "Automated class-based update: info files to output directory"


        if not self.clone_or_pull_repo():
            print("Error: Failed to clone or pull repository.")
            return False
        print("Repository cloned/pulled successfully.")

        if not self.create_info_files():
            print("Error: Failed to create info files.")
            return False
        print("Info files created successfully in output directory.")

        # Check if there are actual changes to commit before calling commit_and_push_changes
        # This can be done by checking `git status --porcelain`
        # For simplicity now, we rely on commit_and_push_changes to handle "nothing to commit"

        if not self.commit_and_push_changes(commit_message):
            # commit_and_push_changes now returns True if "nothing to commit", so this path
            # should ideally only be hit for actual errors.
            # However, if it returned False for "nothing to commit", this message would be misleading.
            # Assuming current behavior: True for "nothing to commit" or successful push.
            # False for actual errors.
            print("Error: Failed to commit and push changes. See logs above for details.")
            return False
        # The commit_and_push_changes method already prints detailed success or "nothing to commit"
        # print("Changes committed and pushed successfully (or no changes to commit).")

        print("Repository update process completed.")
        return True

if __name__ == "__main__":
    # !!! IMPORTANT SECURITY WARNING !!!
    # Configuration, including your GitHub username and Personal Access Token (PAT),
    # is loaded from 'config.json'. You MUST create this file (e.g., by copying
    # 'config.example.json') and populate it with your actual credentials.
    #
    # Committing 'config.json' with real credentials to version control is a
    # significant security risk. Ensure 'config.json' is listed in your .gitignore
    # file to prevent accidental commits.
    #
    # This script includes a check to prevent running with default placeholder
    # values. Ensure the PAT has the necessary permissions (e.g., 'repo' scope)
    # to clone and push to the repository. For production, consider more secure
    # credential management like environment variables or vault solutions.

    config_filename = "config.json"

    try:
        with open(config_filename, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_filename}' not found.")
        print(f"Please copy 'config.example.json' to '{config_filename}' and fill in your details.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{config_filename}'. Please check its format.")
        sys.exit(1)

    try:
        BASE_REPO_URL = config["BASE_REPO_URL"]
        LOCAL_REPO_PATH = config["LOCAL_REPO_PATH"]
        GIT_USERNAME = config["GIT_USERNAME"]
        GIT_TOKEN = config["GIT_TOKEN"]
    except KeyError as e:
        print(f"Error: Missing key {e} in '{config_filename}'.")
        print(f"Please ensure '{config_filename}' contains 'BASE_REPO_URL', 'LOCAL_REPO_PATH', 'GIT_USERNAME', and 'GIT_TOKEN'.")
        sys.exit(1)

    print(f"Starting script with configuration from '{config_filename}': User='{GIT_USERNAME}', LocalPath='{LOCAL_REPO_PATH}'")

    if GIT_USERNAME == "YOUR_GITHUB_USERNAME" or GIT_TOKEN == "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN":
        print(f"\nERROR: Please replace placeholder credentials in '{config_filename}' with your actual GitHub username and Personal Access Token.")
        print("Script will not execute with placeholder credentials.\n")
        sys.exit(1)

    updater = GitRepoUpdater(
        base_repo_url=BASE_REPO_URL,
        local_path=LOCAL_REPO_PATH,
        username=GIT_USERNAME,
        token=GIT_TOKEN
    )

    if updater.run_update():
        print("Script finished successfully.")
    else:
        print("Script finished with errors. Please review the output above.")
