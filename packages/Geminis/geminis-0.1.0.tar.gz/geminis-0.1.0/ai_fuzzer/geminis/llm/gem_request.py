import os
import sys
import time
from pathlib import Path
from typing import Optional, Tuple
import google.genai as genai
import yaml
from google.genai.types import GenerateContentConfig
from ai_fuzzer.geminis.fetch import fetch_docs
import re


def extract_code_blocks(text):
    pattern = r'```(?:[\w+-]*)\s*\n([\s\S]*?)```'
    matches = re.findall(pattern, text)
    return '\n\n'.join(matches)
    

def load_prompt_data(prompt_id: str, yaml_path: Path, debug=False) -> Tuple[float, str, str]:
    with open(yaml_path, "r", encoding="utf-8") as f:    
        if debug:
            print(f"DEBUG: found yaml file {yaml_path}")
        all_prompts = yaml.safe_load(f)
    if prompt_id not in all_prompts:
        raise KeyError(f"Prompt ID '{prompt_id}' not found in {yaml_path}")
    entry = all_prompts[prompt_id]
    return float(entry["temperature"]), entry["description"], entry["template"]


def format_prompt(template: str, target_func: str, debug=False) -> str:
    doc_block = f"{fetch_docs.fetch_atheris_readme(debug)}\n\n{fetch_docs.fetch_atheris_hooking_docs(debug)}"
    
    return template.replace("{{CODE}}", target_func).replace("{{DOCS}}", doc_block)


def get_response(prompt_id: str, target_func: str, yaml_path: Path, debug: False, api=str) -> str:
    if debug:
        print(f"DEBUG: Starting get_response with prompt_id={prompt_id}, target_func size={len(target_func)}")

    temperature, _, template = load_prompt_data(prompt_id, yaml_path, debug)
    full_prompt = format_prompt(template, target_func, debug)

    if debug:
        print(f"DEBUG: Initializing genai.Client")

    client = genai.Client(api_key=api)

    for attempt in range(5):
        try:
            if debug:
                print(f"DEBUG: Attempt {attempt + 1} to call generate_content")

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=GenerateContentConfig(response_modalities=['TEXT'], temperature=temperature)
            )
            if debug:
                print(f"DEBUG: Received response with text length: {len(response.text)}")
            return response.text
        except genai.errors.ServerError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    raise RuntimeError("Failed after multiple attempts.")
