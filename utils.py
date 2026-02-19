import os


def resource_path(relative_path):
    """
    Get the absolute path to a resource. This works for development environments
    and for single-file executables created by PyInstaller.
    """
    try:
        # PyInstaller creates a temporary folder and stores the path in _MEIPASS.
        base_path = sys._MEIPASS  # type: ignore
    except Exception:
        # If not running in a PyInstaller bundle, use the default absolute path.
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
