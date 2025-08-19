from pathlib import Path
import argparse
from ai_fuzzer.geminis.run import run
import os
import requests


def resolve_api_key(arg_val: str | None, debug: bool = False) -> str:
    key: str = ''
    env_key = os.getenv("GENAI_API_KEY")
    if env_key:
        key = env_key.strip()
        if debug:
            print(f"DEBUG: Using API key from environment variable")
    elif arg_val:
        maybe_path = Path(arg_val)
        if maybe_path.is_file():
            try:
                with maybe_path.open("r", encoding="utf-8") as f:
                    key = f.read().strip()
                if debug:
                    print(f"DEBUG: API key loaded from file")
            except Exception as e:
                print(f"Error reading API key file: {e}")
        else:
            key = arg_val.strip()
            if debug:
                print(f"DEBUG: Using API key passed as literal")
    else:
        print("No API key provided. Use --api-key or set GENAI_API_KEY.")
        exit()
    url = "https://generativelanguage.googleapis.com/v1/models"
    headers = {"x-goog-api-key": key}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            if debug:
                print("DEBUG: API key verified successfully.")
            return key
        else:
            print(f"API key verification failed (status: {resp.status_code})")
            exit()
    except requests.RequestException as e:
        print(f"Error verifying API key: {e}")
        exit()



def main():
    parser = argparse.ArgumentParser(description="AI-powered Python fuzzer with Gemini + Atheris.")

    parser.add_argument("--src-dir", type=Path, required=True,
                        help="Path to the Python source directory to fuzz.")

    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Where to store crash logs.")

    parser.add_argument("--prompts-path", type=Path, required=True,
                        help="Path to prompts.yaml config file (default: geminis/llm/prompts.yaml)")

    parser.add_argument("--prompt", default="base", required=True,
                        help="Prompt ID from prompts.yaml to use (default: 'base')")

    parser.add_argument("--mode", choices=["functions", "classes"], default="functions",
                        help="Target fuzzing of functions or classes, default is functions")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode to print internal states.")
    parser.add_argument("--api-key", type=str, required=True,
                        help="API key string or path to file containing it. This can be the api key itself, a path to the api as a single line txt file, or setting the enviorment variable GEMINI_API_KEY with bash: export GEMINI_API_KEY=<YOUR_API_KEY_HERE>")
    parser.add_argument("--smell", action="store_true",
                        help="Enable code smell to judge programatically if code should be fuzzed.")

    args = parser.parse_args()

    api_key=resolve_api_key(args.api_key, args.debug)

    try:
        run(
            source_dir=args.src_dir,
            output_dir=args.output_dir,
            prompt_id=args.prompt,
            mode=args.mode,
            prompt_yaml_path=args.prompts_path,
            debug=args.debug,
            api=api_key,
            smell=args.smell
        )
    except Exception as e:
        import traceback
        print("ERROR:", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()
