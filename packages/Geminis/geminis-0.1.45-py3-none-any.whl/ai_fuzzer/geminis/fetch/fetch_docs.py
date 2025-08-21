import re
import time
import requests
from ai_fuzzer.geminis.logger.logs import log

cache = {}

def fetch_atheris_readme(debug=False):
    if "readme" in cache:
        return cache["readme"]

    url = "https://raw.githubusercontent.com/google/atheris/master/README.md"

    for attempt in range(5):
        try:
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            break
        except (requests.exceptions.RequestException,
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError) as e:
            log(f"Attempt {attempt+1} failed fetching README: {e}", debug)
            time.sleep(2)
    else:
        raise Exception("Failed to fetch README after retries")

    content = response.text
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    content = re.sub(r'\[.*?\]\(https?:\/\/.*?\)', '', content)
    content = re.sub(r'\n{3,}', '\n\n', content)
    formatted = f"""
==== START OF ATHERIS DOCUMENTATION ====

This is the official README documentation for Google's Atheris fuzzing framework for Python.

{content}

==== END OF ATHERIS DOCUMENTATION ====
"""
    cache["readme"] = formatted
    log("fetched atheris readme", debug)
    return formatted


def fetch_atheris_hooking_docs(debug=False):
    if "hooking" in cache:
        return cache["hooking"]

    url = "https://raw.githubusercontent.com/google/atheris/refs/heads/master/hooking.md"

    for attempt in range(5):
        try:
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            break
        except (requests.exceptions.RequestException,
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError) as e:
            log(f"Attempt {attempt+1} failed fetching hooking docs: {e}", debug)
            time.sleep(2)
    else:
        raise Exception("Failed to fetch hooking docs after retries")

    content = response.text
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    content = re.sub(r'\[.*?\]\(https?:\/\/.*?\)', '', content)
    content = re.sub(r'\n{3,}', '\n\n', content)
    formatted = f"""
==== START OF ATHERIS' HOOKING DOCUMENTATION ====

This is the official README documentation for Google's Atheris fuzzing framework for Python.

{content}

==== END OF ATHERIS' HOOKING DOCUMENTATION ====
"""
    cache["hooking"] = formatted
    log("fetched atheris hooking documentation", debug)
    return formatted
