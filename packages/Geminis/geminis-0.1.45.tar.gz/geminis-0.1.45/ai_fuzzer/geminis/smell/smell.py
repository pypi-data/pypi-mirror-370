from radon.metrics import mi_visit
from ai_fuzzer.geminis.logger.logs import log

def code_smells(python_code: str, threshold: float = 65.0, debug: bool = False) -> bool:
    """
    Determines if the given Python code smells based on the Maintainability Index (MI).
    Returns bool: True if the code smells, False otherwise.
    """
    results = mi_visit(python_code, True)
    if not results:
        return False

    decision = results < threshold

    action = "will fuzz" if decision else "will skip fuzzing"
    log(f"MI score = {results} (threshold = {threshold}) → {action}", debug)

    return decision