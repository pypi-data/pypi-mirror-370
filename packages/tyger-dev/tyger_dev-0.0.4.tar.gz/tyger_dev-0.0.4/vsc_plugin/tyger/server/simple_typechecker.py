import ast

def check_types(code):
    tree = ast.parse(code)
    errors = []
    # Implement a simple type-checking logic here
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # Simple check: Ensure the variable is not assigned a string if it was an integer
            # This is just a placeholder for actual type-checking logic
            if isinstance(node.value, ast.Str) and isinstance(node.targets[0], ast.Name):
                errors.append(f"Type Error: Variable '{node.targets[0].id}' is assigned a string")
    return errors

if __name__ == "__main__":
    import sys
    code = open(sys.argv[1]).read()
    for error in check_types(code):
        print(error)