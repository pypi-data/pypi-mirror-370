import os
from typing import List, Optional, Dict
import getpass


SECRET_HINTS = ("TOKEN", "SECRET", "KEY")


def _is_secret(var: str) -> bool:
    u = var.upper()
    return any(h in u for h in SECRET_HINTS)


def prompt_for_env(vars_needed: List[str]) -> Dict[str, str]:
    values: Dict[str, str] = {}
    for key in vars_needed:
        current = os.getenv(key)
        if current:
            continue
        try:
            if _is_secret(key):
                val = getpass.getpass(f"Enter value for {key} (leave blank to skip): ")
            else:
                val = input(f"Enter value for {key} (leave blank to skip): ")
        except EOFError:
            val = ""
        if val:
            os.environ[key] = val
            values[key] = val
    return values


def save_env_file(values: Dict[str, str], path: Optional[str] = None) -> Optional[str]:
    if not values:
        return None
    if not path:
        home = os.path.expanduser("~")
        path = os.path.join(home, ".docmaplabs_marketing", ".env")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for k, v in values.items():
            # avoid writing quotes; assume no newlines
            f.write(f"{k}={v}\n")
    return path


