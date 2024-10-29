# GitHub Teleporter

A Python script that teleports your files directly to a new GitHub repository with selected licenses and configurations.

## Features

- Select files from a directory to include in the repository
- Choose from multiple license types (MIT, Apache 2.0, BSD 3-Clause)
- Automatically initializes git repository
- Saves and recalls your GitHub username and email
- Supports GitHub personal access token through environment variable
- Creates remote repository on GitHub
- Pushes selected files to the new repository

## Requirements

- Python 3.x
- `requests` library
- Git installed and configured
- GitHub account and personal access token

## Installation

1. Clone this repository
2. Install required packages:
```bash
pip install requests
```

## Usage

1. Run the script:
```bash
python github-teleporter.py
```

2. Follow the interactive prompts:
   - Enter directory path (or use current directory)
   - Select files to include
   - Choose a license type
   - Enter GitHub credentials
   - Provide repository name

The script will:
- Create a new repository on GitHub
- Initialize a local git repository
- Add selected files
- Push everything to GitHub

## Environment Variables

- `GITHUBKEY`: Your GitHub personal access token (optional, can be entered manually)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
