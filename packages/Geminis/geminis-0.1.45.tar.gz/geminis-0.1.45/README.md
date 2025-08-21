
## Geminis:
This project creates a LLM-assisted Python fuzzing harness generator designed to leverage large language models like Gemini to automatically build fuzzing harnesses for target Python functions. It uses Google’s Atheris fuzzing engine to dynamically generate and test code, with the aim of uncovering bugs or vulnerabilities in software.

# Usage:
  geminis \
    --src-dir /path/to/code  
    --output-dir /path/to/logs   
    --prompts-path /path/to/prompts.yaml   
    --api-key /path/to/api.txt  
    --prompt prompt-id (base if using given yaml prompts)  
    --mode functions(classes)  
    --debug Outputs detailed debug statements  
    --smell Uses optional radon code smell using the maintainability index  

# Workflow:
  1. Load API key (enviorment variable, file, raw string), verify model.
  2. Discover .py files; parse target snippets.
  3. (Optional) Filter by maintainability index by radon.
  4. Build prompt with Atheris docs + code; send to Gemini.
  5. Creates python3.11 sandbox venv, writes harness, runs tests, cleans up temp venv, saves outputs.
