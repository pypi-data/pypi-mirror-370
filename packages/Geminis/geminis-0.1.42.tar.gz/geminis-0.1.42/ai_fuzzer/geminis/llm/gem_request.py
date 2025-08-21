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
from ai_fuzzer.geminis.logger.logs import log


def extract_code_blocks(text):
    pattern = r'```(?:[\w+-]*)\s*\n([\s\S]*?)```'
    matches = re.findall(pattern, text)
    return '\n\n'.join(matches)
    

def load_prompt_data(prompt_id: str, yaml_path: Path, debug=False) -> Tuple[float, str, str]:
    with open(yaml_path, "r", encoding="utf-8") as f:
        log(f"found yaml file {yaml_path}", debug)
        all_prompts = yaml.safe_load(f)
    if prompt_id not in all_prompts:
        raise KeyError(f"Prompt ID '{prompt_id}' not found in {yaml_path}")
    entry = all_prompts[prompt_id]
    return float(entry["temperature"]), entry["description"], entry["template"]


def format_prompt(template: str, target_func: str, debug=False) -> str:
    doc_block = f"{fetch_docs.fetch_atheris_readme(debug)}\n\n{fetch_docs.fetch_atheris_hooking_docs(debug)}"
    return template.replace("{{CODE}}", target_func).replace("{{DOCS}}", doc_block)


def get_response(prompt_id: str, target_func: str, yaml_path: Path, debug: False, api=str) -> str:
    log(f"Starting get_response with prompt_id={prompt_id}, target_func size={len(target_func)}", debug)

    temperature, _, template = load_prompt_data(prompt_id, yaml_path, debug)
    full_prompt = format_prompt(template, target_func, debug)

    log("Initializing genai.Client", debug)
    client = genai.Client(api_key=api)

    for attempt in range(5):
        try:
            log(f"Attempt {attempt + 1} to call generate_content", debug)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=GenerateContentConfig(response_modalities=['TEXT'], temperature=temperature)
            )
            fallback_txt = "## an error occurred with LLM response\nexit()"
            txt = (getattr(response, "text", None) or fallback_txt)
            log(f"Received response with text length: {len(txt)}", debug) if txt != fallback_txt else log("A response error occurred (empty/missing text); falling back to the python literal 'exit()'", debug)
            return txt
        except genai.errors.ServerError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    raise RuntimeError("Failed after multiple attempts.")
