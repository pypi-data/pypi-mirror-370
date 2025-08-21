from typing import Tuple

# This should fail
a: Tuple[int, str] = (1, 2)

# This should succeed
b: Tuple[int, str] = (1, "hello")
