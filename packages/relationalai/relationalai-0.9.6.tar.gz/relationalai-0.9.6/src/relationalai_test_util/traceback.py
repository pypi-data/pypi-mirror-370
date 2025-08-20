import os
import sys
import re
from pathlib import Path
import traceback
from typing import Union
from colorama import Style

################################################################################
# Relative path selection
################################################################################


def find_project_root(path):
    path = Path(path).resolve()

    # Common project root indicators
    root_indicators = [
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        ".git",
        ".hg",
        ".svn",
        "requirements.txt",
        "Pipfile",
        "poetry.lock",
    ]

    current_path = path
    while current_path != current_path.parent:
        if any((current_path / indicator).exists() for indicator in root_indicators):
            return current_path
        current_path = current_path.parent

    return None


PROJECT_ROOT = find_project_root(os.getcwd())

def relative_to_project(path: Path):
    if PROJECT_ROOT and path.is_relative_to(PROJECT_ROOT):
        return path.relative_to(PROJECT_ROOT)


def relative_to_venv(path: Path):
    if hasattr(sys, "prefix"):
        venv_path = Path(sys.prefix)
        if path.is_relative_to(venv_path):
            return path.relative_to(venv_path.parent)


def relative_to_site_packages(path: Path):
    best: Union[Path, None] = None

    for site_path in sys.path:
        if "site-packages" in site_path:
            site_path = Path(site_path)
            if path.is_relative_to(site_path):
                new = path.relative_to(site_path.parent)
                if not best or len(str(best)) > len(str(new)):
                    best = new

    return best


def condense_path(path):
    resolved = Path(path).resolve()
    best: Union[Path, None] = None

    for try_option in (
        relative_to_project,
        relative_to_venv,
        relative_to_site_packages,
    ):
        option = try_option(resolved)
        if not best:
            best = option
        elif option and len(str(option)) < len(str(best)):
            best = option

    if best:
        return str(best)
    else:
        return str(path)


################################################################################
# Pretty traceback
################################################################################

def condense_traceback(exception: Exception, filter_frame_patterns = ["site-packages/_pytest", "site-packages/pluggy"]):
    tb = traceback.extract_tb(exception.__traceback__)
    max_prefix_size = 0
    prefixes: list[str] = []
    linenos: list[int] = []
    messages: list[str] = []
    for filename, lineno, name, text in tb:
        prefix = f"{condense_path(filename)} in {name}"
        exclude = False
        for pattern in filter_frame_patterns:
            if re.search(pattern, prefix):
                exclude = True
        if exclude:
            continue

        if len(prefix) > max_prefix_size:
            max_prefix_size = len(prefix)
        prefixes.append(prefix)
        linenos.append(lineno)
        messages.append(text.strip())

    return "\n".join(
        [
            f"{Style.DIM}{prefix: <{max_prefix_size}} {lineno: >4} |{Style.RESET_ALL} {msg}"
            for prefix, lineno, msg in zip(prefixes, linenos, messages)
        ]
    )
