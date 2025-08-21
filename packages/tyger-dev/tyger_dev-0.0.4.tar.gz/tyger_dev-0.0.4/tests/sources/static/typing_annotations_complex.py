from typing import List, Dict, Any

# This should fail
a: List[int] = ["a", "b"]

# This should fail
b: Dict[str, int] = {"key": "value"}

# This should succeed
c: Any = "anything"
d: Any = 42

# This should succeed
e: List[str] = ["hello", "world"]
f: Dict[str, int] = {"one": 1, "two": 2}
