import importlib
import sys


def check_dependencies(
    dependencies: list[str],
    *,
    required: bool,
    group_name: str = None,
    package_name: str = "lambda_happy",
) -> bool:
    """Check if the specified Python packages are installed and handle missing dependencies.

    Args:
        dependencies (list[str]): List of package names to check for importability.
        required (bool): Whether the dependencies are required. If True, the program exits
                         when dependencies are missing. If False, a warning is printed.
        group_name (str, optional): Name of the optional dependency group (used in messages). Defaults to None.
        package_name (str, optional): Name of the main package used for installation instructions. Defaults to "lambda_happy".

    Returns:
        bool: True if all dependencies are installed, False if optional dependencies are missing.
              If required dependencies are missing, the function exits the program.
    """
    missing = [pkg for pkg in dependencies if not _is_importable(pkg)]

    if missing:
        if required:
            sys.exit(
                f"Error: Missing required dependencies: {', '.join(missing)}.\n"
                f"Please install them with:\n"
                f"    pip install {package_name}[{group_name}]\n",
            )
        else:
            group_str = f"for optional group '{group_name}'" if group_name else ""
            print(
                f"Warning: Missing optional dependencies {group_str}: {', '.join(missing)}.\n"
                f"To install them, run:\n"
                f"    pip install {package_name}[{group_name}]\n",
                file=sys.stderr,
            )
            return False
    return True


def _is_importable(package: str) -> bool:
    """Check if a Python package can be imported.

    Args:
        package (str): Name of the package to check.

    Returns:
        bool: True if the package can be imported, False if an ImportError occurs.
    """
    try:
        importlib.import_module(package)
        return True
    except ImportError:
        return False
