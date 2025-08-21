import requests
import re
from ai_fuzzer.geminis.logger.logs import log

def fetch_atheris_readme(debug=False):
    url = "https://raw.githubusercontent.com/google/atheris/master/README.md"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch README: {response.status_code}")

    content = response.text
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    content = re.sub(r'\[.*?\]\(https?:\/\/.*?\)', '', content)
    content = re.sub(r'\n{3,}', '\n\n', content)
    formatted_content = f"""
    ==== START OF ATHERIS DOCUMENTATION ====

    This is the official README documentation for Google's Atheris fuzzing framework for Python.

    {content}

    ==== END OF ATHERIS DOCUMENTATION ====
    """
    log("fetched atheris read me", debug)
    return formatted_content

def fetch_atheris_hooking_docs(debug=False):
    url = 'https://raw.githubusercontent.com/google/atheris/refs/heads/master/hooking.md'

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch README: {response.status_code}")

    content = response.text
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    content = re.sub(r'\[.*?\]\(https?:\/\/.*?\)', '', content)
    content = re.sub(r'\n{3,}', '\n\n', content)
    formatted_content = f"""
    ==== START OF ATHERIS' HOOKING DOCUMENTATION ====

    This is the official README documentation for Google's Atheris fuzzing framework for Python.

    {content}

    ==== END OF ATHERIS' HOOKING DOCUMENTATION ====
    """

    log("fetched atheris hooking documentation", debug)
    return formatted_content
