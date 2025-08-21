import ast


def policy_caller_static_analysis(code: str, libraries: list[str] = []) -> str:
    """Analyze the code and return the name of the class that inherit from PolicyCaller"""

    # Parse the code to check imports
    tree = ast.parse(code)

    # Check all import statements
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in libraries:
                    raise ImportError(f"Import '{alias.name}' is not allowed. Allowed libraries: {libraries}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module not in libraries:
                raise ImportError(f"Import from '{node.module}' is not allowed. Allowed libraries: {libraries}")

    class_names = [
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and any(base.id == "PolicyCaller" for base in node.bases if isinstance(base, ast.Name))
    ]

    # check that there is only one class that inherit from PolicyCaller
    if len(class_names) > 1:
        raise TypeError(f"Multiple classes found in the agent code that inherit from PolicyCaller: {class_names}")
    elif len(class_names) == 0:
        raise TypeError("No class found in the agent code that inherit from PolicyCaller")

    return class_names[0]
