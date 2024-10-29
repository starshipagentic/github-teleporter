import os
import subprocess
import requests
import shutil

def get_directory_path():
    path = input("Enter the full path of the directory or file (default is current directory '.'): ")
    if not path.strip():
        path = "."
    if os.path.isfile(path):
        return os.path.dirname(path)
    return path

def list_files(directory):
    files = os.listdir(directory)
    print("Files in directory:")
    for i, file in enumerate(files):
        print(f"{i + 1}: {file}")
    return files

def select_files(files):
    selected_indices = input("Enter the numbers of the files to include, separated by commas: ")
    try:
        selected_indices = [int(index.strip()) - 1 for index in selected_indices.split(",")]
        selected_files = [files[i] for i in selected_indices if 0 <= i < len(files)]
    except ValueError:
        print("Invalid input. Please enter valid numbers separated by commas.")
        return select_files(files)
    return selected_files
    return [files[i] for i in selected_indices]

def initialize_git_repo(directory):
    result = subprocess.run(["git", "init"], cwd=directory, capture_output=True, text=True)
    print("Git init output:", result.stdout, result.stderr)

def create_github_repo(repo_name, token, username):
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"token {token}"}
    data = {"name": repo_name, "private": False}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 422:
        print("Repository already exists on GitHub.")
        return f"https://github.com/{username}/{repo_name}"
    response.raise_for_status()
    return response.json()["html_url"]

def add_and_commit_files(directory, files):
    if not files:
        print("No files selected to commit.")
        return

    # Clear any existing staged files
    subprocess.run(["git", "reset"], cwd=directory)

    for file in files:    
        print(f"Adding file: {file}")
        subprocess.run(["git", "add", file], cwd=directory)
    result = subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=directory, capture_output=True, text=True)
    print("Git commit output:", result.stdout, result.stderr)

def set_git_user(directory, username, email):
    result = subprocess.run(["git", "config", "user.name", username], cwd=directory, capture_output=True, text=True)
    print("Set Git user.name output:", result.stdout, result.stderr)
    result = subprocess.run(["git", "config", "user.email", email], cwd=directory, capture_output=True, text=True)
    print("Set Git user.email output:", result.stdout, result.stderr)

def read_last_user_info():
    try:
        with open("user_info.txt", "r") as file:
            username, email = file.read().strip().split(',')
            return username, email
    except (FileNotFoundError, ValueError):
        return None, None

def save_user_info(username, email):
    with open("user_info.txt", "w") as file:
        file.write(f"{username},{email}")
def create_license_file(directory, license_type):
    licenses = {
        "MIT": """MIT License

Copyright (c) [Year] [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""",
        "Apache 2.0": """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

"License" shall mean the terms and conditions for use, reproduction, and
distribution as defined by Sections 1 through 9 of this document.

... (rest of the Apache 2.0 license text) ...""",
        "BSD 3-Clause": """BSD 3-Clause License

Copyright (c) [Year], [Your Name]
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

... (rest of the BSD 3-Clause license text) ..."""
    }

    license_text = licenses.get(license_type)
    if license_text:
        with open(os.path.join(directory, "LICENSE"), "w") as file:
            file.write(license_text)
    else:
        print(f"License type {license_type} not recognized.")
def main():
    directory = get_directory_path()
    files = list_files(directory)
    selected_files = select_files(files)
    target_directory = os.path.expanduser("~/starship/githubteleporter")
    # Choose a license
    license_choice = input("Choose a license (MIT, Apache 2.0, BSD 3-Clause) [MIT]: ") or "MIT"
    create_license_file(target_directory, license_choice)

    # Ensure the target directory exists and is empty
    if os.path.exists(target_directory):
        shutil.rmtree(target_directory)
    os.makedirs(target_directory)

    # Copy selected files to the target directory
    for file in selected_files:
        shutil.copy(os.path.join(directory, file), target_directory)

    # Add LICENSE file to the selected files
    selected_files.append("LICENSE")

    # Initialize the git repository in the target directory
    initialize_git_repo(target_directory)
    last_username, last_email = read_last_user_info()
    username = input(f"Enter your GitHub username [{last_username}]: ") or last_username
    email = input(f"Enter your GitHub email [{last_email}]: ") or last_email
    save_user_info(username, email)
    set_git_user(target_directory, username, email)

    repo_name = input("Enter the name for the GitHub repository: ")
    token = input("Enter your GitHub personal access token (or press Enter to use GITHUBKEY environment variable): ")
    if not token.strip():
        token = os.getenv("GITHUBKEY")
        if not token:
            raise EnvironmentError("GITHUBKEY environment variable not set.")
    repo_url = create_github_repo(repo_name, token, username)
    add_and_commit_files(target_directory, selected_files)
    push_to_github(target_directory, repo_url, username, token, repo_name)
    print(f"Repository created and files pushed to {repo_url}")

def push_to_github(directory, repo_url, username, token, repo_name):
    # Remove existing remote if it exists
    subprocess.run(["git", "remote", "remove", "origin"], cwd=directory, capture_output=True, text=True)
    # Include the token in the URL for authentication
    auth_repo_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    result = subprocess.run(["git", "remote", "add", "origin", auth_repo_url], cwd=directory, capture_output=True, text=True)
    if "already exists" in result.stderr:
        print("Remote origin already exists.")
    else:
        print("Git remote add output:", result.stdout, result.stderr)
    subprocess.run(["git", "branch", "-M", "main"], cwd=directory)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=directory)

if __name__ == "__main__":
    main()
