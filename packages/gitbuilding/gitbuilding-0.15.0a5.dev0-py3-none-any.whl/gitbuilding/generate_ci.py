"""
This module automatically creates CI configurations to serve GitBuilding documentation
for GitLab, GitHub actions, and Netlify.
"""

import sys

from gitbuilding.native_file_operations import make_dir_if_needed, exists_on_disk, write_local_file

RECOMMENDED_PYTHON_VERSION = "3.7"



def get_branch():
    """
    Check which branch to deploy on
    """
    ans = input(BRANCH_PROMPT)
    if len(ans)==0:
        return "main"
    return ans

def generate_ci(working_dir):
    """
    Prompt user to sepecify a type of CI file and then generate it.
    """
    print("This will generate the necessary files to publish your documentation as a"
        "website on Gitlab, Github or Netlify.\n")

    ans = input(PROMPT)

    try:
        ans = int(ans)
        if ans > 3 or ans < 1:
            raise ValueError()
    except ValueError:
        print(f'Answer "{ans}" is not understood.')
        sys.exit(1)

    if ans == 1:
        path = ".gitlab-ci.yml"
        branch = get_branch()
        if exists_on_disk(path, working_dir):
            print(f"Error: {path} already exists. Not overwriting it.")
            sys.exit(1)
        else:
            write_file(path, working_dir, gitlab_ci_yaml(branch))

    elif ans == 2:
        folder = ".github/workflows/"
        path = folder+"gitbuilding.yml"
        branch = get_branch()
        if exists_on_disk(path, working_dir):
            print(f"Error: {path} already exists. Not overwriting it.")
            sys.exit(1)
        else:
            make_dir_if_needed(folder, working_dir)
            write_file(path, working_dir, github_action_yaml(branch))

    elif ans == 3:
        path_txt = "runtime.txt"
        path_toml = "netlify.toml"
        if exists_on_disk(path_txt, working_dir):
            print(f"{path_txt} already exists. Not overwriting it.")
        else:
            write_file(path_txt, working_dir, RECOMMENDED_PYTHON_VERSION + "\n")
        if exists_on_disk(path_toml, working_dir):
            print(f"Error: {path_toml} already exists. Not overwriting it.")
            sys.exit(1)
        else:
            write_file(path_toml, working_dir, NETLIFY_TOML_CONTENTS)


def write_file(path, working_dir, contents):
    """
    Write the CI file to disk
    """
    write_local_file(path, working_dir, contents)
    print(f"Generated {path}")


PROMPT = '''Which hosting service do you want to use?

1. Gitlab Pages
2. Github Pages
3. Netlify

Enter a number: '''

BRANCH_PROMPT = '''Enter the name of your default branch (default: main):  '''


def gitlab_ci_yaml(branch_name="main"):
    """
    Return the yaml for gitlab CI
    """
    return '''
image: "python:''' + RECOMMENDED_PYTHON_VERSION + '''"
before_script:
  - python --version
  - pip install gitbuilding

pages:
  stage: deploy
  script:
  - gitbuilding build-html
  - mv _site public
  # gzip the files so we get compression in gitlab pages
  - gzip -k -6 $(find public -type f)
  artifacts:
    paths:
    - public
  only:
  - '''+ branch_name +'''
'''

def github_action_yaml(branch_name="main"):
    """
    Return the yaml for github actions
    """
    return '''
name: Deploy Gitbuilding Project to Github Pages

on: [push]

jobs:
  build_and_deploy:
    runs-on: ubuntu-20.04
    steps:
      - uses: actions/checkout@v2
      - name: Install Python 3
        uses: actions/setup-python@v1
        with:
          python-version: "''' + RECOMMENDED_PYTHON_VERSION + '''"
      - name: Build
        run: |
          pip install gitbuilding
          gitbuilding build-html
      - name: Deploy
        uses: JamesIves/github-pages-deploy-action@3.7.1
        with:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          BRANCH: '''+ branch_name +'''
          FOLDER: _site/
          # Automatically remove deleted files from the deploy branch
          CLEAN: false
'''

NETLIFY_TOML_CONTENTS = '''
[build]
  command = "pip3 install gitbuilding && gitbuilding build-html"
  publish = "_site/"
'''
