import requests
import re

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
    print("DEBUG: fetched atheris read me")
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

    print("DEBUG: fetched atheris hooking documentation")
    return formatted_content