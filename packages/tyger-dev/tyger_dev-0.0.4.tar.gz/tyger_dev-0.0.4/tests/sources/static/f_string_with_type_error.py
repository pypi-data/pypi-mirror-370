x: int = 42
y: str = x  # This should fail
z: str = f"Value: {y}"  # This should work but y assignment fails
