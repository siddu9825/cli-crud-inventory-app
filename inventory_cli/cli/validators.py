"""Input validation and interactive terminal prompt helpers."""

from typing import Optional, List, Any

# ANSI Colors for terminal feedback
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BOLD = "\033[1m"

def print_error(msg: str) -> None:
    """Print formatted error message."""
    print(f"{RED}✖ Error: {msg}{RESET}")

def print_success(msg: str) -> None:
    """Print formatted success message."""
    print(f"{GREEN}✔ {msg}{RESET}")

def print_warning(msg: str) -> None:
    """Print formatted warning message."""
    print(f"{YELLOW}▲ {msg}{RESET}")

def prompt_string(
    prompt: str,
    min_len: int = 1,
    default: Optional[str] = None,
    allow_blank: bool = False,
    to_upper: bool = False,
) -> Optional[str]:
    """Prompt user for a string with length and blankness checks."""
    default_hint = f" [{default}]" if default is not None else ""
    full_prompt = f"{CYAN}{prompt}{default_hint}: {RESET}"

    while True:
        try:
            val = input(full_prompt).strip()
            if not val:
                if default is not None:
                    return default.upper() if to_upper else default
                if allow_blank:
                    return ""
                print_error(f"Input cannot be empty. Minimum length: {min_len}.")
                continue
            if len(val) < min_len:
                print_error(f"Input must be at least {min_len} character(s).")
                continue
            return val.upper() if to_upper else val
        except (KeyboardInterrupt, EOFError):
            print("\n")
            raise

def prompt_float(
    prompt: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    default: Optional[float] = None,
    allow_blank: bool = False,
) -> Optional[float]:
    """Prompt user for a valid floating point number with bounds checks."""
    default_hint = f" [{default}]" if default is not None else ""
    full_prompt = f"{CYAN}{prompt}{default_hint}: {RESET}"

    while True:
        try:
            val_str = input(full_prompt).strip()
            if not val_str:
                if default is not None:
                    return default
                if allow_blank:
                    return None
                print_error("This field is required. Please enter a number.")
                continue

            val = float(val_str)
            if min_val is not None and val < min_val:
                print_error(f"Value must be greater than or equal to {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print_error(f"Value must be less than or equal to {max_val}.")
                continue
            return val
        except ValueError:
            print_error("Invalid input. Please enter a valid decimal number (e.g. 19.99).")
        except (KeyboardInterrupt, EOFError):
            print("\n")
            raise

def prompt_int(
    prompt: str,
    min_val: Optional[int] = None,
    max_val: Optional[int] = None,
    default: Optional[int] = None,
    allow_blank: bool = False,
) -> Optional[int]:
    """Prompt user for a valid integer with bounds checks."""
    default_hint = f" [{default}]" if default is not None else ""
    full_prompt = f"{CYAN}{prompt}{default_hint}: {RESET}"

    while True:
        try:
            val_str = input(full_prompt).strip()
            if not val_str:
                if default is not None:
                    return default
                if allow_blank:
                    return None
                print_error("This field is required. Please enter an integer.")
                continue

            val = int(val_str)
            if min_val is not None and val < min_val:
                print_error(f"Value must be greater than or equal to {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print_error(f"Value must be less than or equal to {max_val}.")
                continue
            return val
        except ValueError:
            print_error("Invalid input. Please enter a whole integer (e.g. 10).")
        except (KeyboardInterrupt, EOFError):
            print("\n")
            raise

def prompt_confirm(prompt: str, default: bool = False) -> bool:
    """Prompt user for binary Yes/No confirmation."""
    options = "[y/N]" if not default else "[Y/n]"
    full_prompt = f"{YELLOW}{prompt} {options}: {RESET}"

    while True:
        try:
            ans = input(full_prompt).strip().lower()
            if not ans:
                return default
            if ans in ("y", "yes"):
                return True
            if ans in ("n", "no"):
                return False
            print_error("Please respond with 'y' (yes) or 'n' (no).")
        except (KeyboardInterrupt, EOFError):
            print("\n")
            raise

def prompt_choice(prompt: str, choices: List[str]) -> str:
    """Prompt user to choose from a list of valid string options."""
    print(f"\n{BOLD}{prompt}:{RESET}")
    for idx, choice in enumerate(choices, 1):
        print(f"  [{idx}] {choice}")

    while True:
        try:
            sel = input(f"{CYAN}Select option (1-{len(choices)}): {RESET}").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(choices):
                return choices[int(sel) - 1]
            print_error(f"Please select a number between 1 and {len(choices)}.")
        except (KeyboardInterrupt, EOFError):
            print("\n")
            raise
