import importlib
import sys


def check_dependencies(
    dependencies: list[str],
    *,
    required: bool,
    group_name: str = None,
    package_name: str = "lambda_happy",
) -> bool:
    """_summary_

    Args:
        dependencies (list[str]): _description_
        required (bool): _description_
        group_name (str, optional): _description_. Defaults to None.
        package_name (str, optional): _description_. Defaults to "lambda_happy".

    Returns:
        bool: _description_
    """
    missing = [pkg for pkg in dependencies if not _is_importable(pkg)]

    if missing:
        if required:
            sys.exit(
                f"Error: Missing required dependencies: {', '.join(missing)}.\n"
                f"Please install them with:\n"
                f"    pip install {package_name}\n"
            )
        else:
            group_str = f" for optional group '{group_name}'" if group_name else ""
            print(
                f"Warning: Missing optional dependencies{group_str}: {', '.join(missing)}.\n"
                f"To install them, run:\n"
                f"    pip install {package_name}[{group_name}]\n",
                file=sys.stderr,
            )
            return False
    return True


def _is_importable(package: str) -> bool:
    try:
        importlib.import_module(package)
        return True
    except ImportError:
        return False
