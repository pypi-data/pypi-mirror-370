from radon.metrics import mi_visit

def code_smells(python_code: str, threshold: float = 65.0, debug: bool = False) -> bool:
    """
    Determines if the given Python code smells based on the Maintainability Index (MI).
    Returns bool: True if the code smells, False otherwise.
    """
    results = mi_visit(python_code, True)
    if not results:
        return False

    decision = results < threshold

    if debug:
        action = "will fuzz" if decision else "will skip fuzzing"
        print(
            f"DEBUG: MI score = {results} (threshold = {threshold}) → {action}"
        )

    return decision