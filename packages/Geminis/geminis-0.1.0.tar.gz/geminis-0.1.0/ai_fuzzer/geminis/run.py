from pathlib import Path
from datetime import datetime
from typing import Sequence
import os
from ai_fuzzer.geminis.llm import gem_request as atherisai
from ai_fuzzer.geminis.sandbox import sandbox
from ai_fuzzer.geminis.parsing import function_parser
from ai_fuzzer.geminis.smell.smell import code_smells

def make_run_dir(base: Path, debug=False) -> Path:
    timestamp = datetime.now().strftime("%m-%d-%y_%I-%M-%S%p").lower()
    run_dir = base / f"run-{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    if debug:
        print(f"DEBUG: Created run directory at: {run_dir} (type: {type(run_dir)})")
    return run_dir

def retrieve_function_candidates(path: Path, prompt_id: str, prompt_yaml_path: Path, api: str, debug: bool = False, smell: bool = False) -> Sequence[str]:
    func_tests = []
    pyfiles = function_parser.get_python_file_paths(path, debug=debug)
    if debug and pyfiles:
        print(f"DEBUG: Found python files")
    for pyfile in pyfiles:
        funcs = function_parser.extract_functions(pyfile, debug=debug)
        if debug:
            print(f"DEBUG: Found {len(funcs)} functions in {pyfile}")
        for func in funcs:
            if smell:
                if not code_smells(python_code = func, debug = debug):
                    continue
            response = atherisai.get_response(
                prompt_id=prompt_id,
                target_func=func,
                yaml_path=prompt_yaml_path,
                debug=debug,
                api=api,
            )
            blocks = atherisai.extract_code_blocks(response)
            func_tests.append(blocks)
    return func_tests

def retrieve_class_candidates(path: Path, prompt_id: str, prompt_yaml_path: Path, api: str, debug: bool = False, smell: bool = False) -> Sequence[str]:
    class_tests = []
    pyfiles = function_parser.get_python_file_paths(path, debug=debug)
    if debug:
        print(f"DEBUG: Retrieved {len(pyfiles)} Python files from: {path}")
    for pyfile in pyfiles:
        classes = function_parser.extract_classes(pyfile, debug=debug)
        if debug:
            print(f"DEBUG: Found {len(classes)} classes in {pyfile}")
        for clss in classes:
            if smell:
                if not code_smells(python_code = clss, debug = debug):
                    continue
            response = atherisai.get_response(
                prompt_id=prompt_id,
                target_func=clss,
                yaml_path=prompt_yaml_path,
                debug=debug,
                api=api,
            )
            blocks = atherisai.extract_code_blocks(response)
            class_tests.append(response)
    return class_tests

def run_function_testing(code_snippets: Sequence[str], output_base: Path, debug: False):
    if debug:
        print(f"DEBUG: Running function tests, total snippets: {len(code_snippets)}")
    for code in code_snippets:
        path = make_run_dir(output_base, debug=debug)
        sandbox.save_to_file(code, path, debug=debug)
        sandbox.sandbox_venv(code, path, debug=debug)

def run(
    source_dir: Path, output_dir: Path, prompt_id: str, mode: str, prompt_yaml_path: Path, api: str, debug: False, smell: False
) -> None:
    if debug:
        print(f"DEBUG: run() called with mode={mode}, source_dir={source_dir}, output_dir={output_dir}, prompt_id={prompt_id}, prompt_yaml_path={prompt_yaml_path}")

    if mode == "functions":
        code_snippets = retrieve_function_candidates(source_dir, prompt_id, prompt_yaml_path, api=api, debug=debug, smell=smell)
    elif mode == "classes":
        code_snippets = retrieve_class_candidates(source_dir, prompt_id, prompt_yaml_path, api=api, debug=debug, smell=smell)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    run_function_testing(code_snippets, output_dir, debug=debug)
