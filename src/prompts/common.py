def fix_error_prompt(code: str, error_message: str) -> str:
    """Fix the error message."""
    return f"""
    You are a helpful assistant that fixes errors in code.

    # Code
    {code}

    # Error Message
    {error_message}
    """


def fix_by_reference_prompt(code: str, reference: str) -> str:
    """Fix the code by the reference documentation."""
    return f"""
    You are a helpful assistant. Please fix the code by the reference documentation.

    # Code
    {code}

    # Reference
    {reference}
    """
