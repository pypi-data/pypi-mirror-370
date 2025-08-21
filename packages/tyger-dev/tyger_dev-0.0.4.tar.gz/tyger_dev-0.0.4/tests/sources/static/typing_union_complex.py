from typing import Dict, Union, List


def get_config() -> Dict[str, Union[str, int, bool, List[str]]]:
    return {
        "server": "localhost",
        "port": 8080,
        "debug": True,
        "allowed_origins": ["localhost", "127.0.0.1"],
    }

a: str = 1