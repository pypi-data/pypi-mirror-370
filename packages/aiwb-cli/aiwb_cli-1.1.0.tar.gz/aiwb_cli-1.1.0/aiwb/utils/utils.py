import platform
import os

CACHE_DIR = os.path.expanduser(os.path.join("~", ".aiwb", "cache"))


def _get_platform_info():
    uname = platform.uname()
    return uname.system.lower(), uname.release.lower()


def can_launch_browser():
    import webbrowser

    platform_name, _ = _get_platform_info()

    if platform_name != "linux":
        # Only Linux may have no browser
        return True

    # Using webbrowser to launch a browser is the preferred way.
    try:
        webbrowser.get()
        return True
    except webbrowser.Error:
        # Don't worry. We may still try powershell.exe.
        pass

    return False


def is_windows():
    platform_name, _ = _get_platform_info()
    return platform_name == "windows"


def is_wsl():
    platform_name, release = _get_platform_info()
    # "Official" way of detecting WSL: https://github.com/Microsoft/WSL/issues/423#issuecomment-221627364
    # Run `uname -a` to get 'release' without python
    #   - WSL 1: '4.4.0-19041-Microsoft'
    #   - WSL 2: '4.19.128-microsoft-standard'
    return platform_name == "linux" and "microsoft" in release


def open_page_in_browser(url):
    import subprocess
    import webbrowser

    platform_name, _ = _get_platform_info()

    if is_wsl():  # windows 10 linux subsystem
        try:
            # https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe
            # Ampersand (&) should be quoted
            return subprocess.Popen(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-Command",
                    'Start-Process "{}"'.format(url),
                ]
            ).wait()
        except (
            OSError
        ):  # WSL might be too old  # FileNotFoundError introduced in Python 3
            pass
    elif platform_name == "darwin":
        # handle 2 things:
        # a. On OSX sierra, 'python -m webbrowser -t <url>' emits out "execution error: <url> doesn't
        #    understand the "open location" message"
        # b. Python 2.x can't sniff out the default browser
        return subprocess.Popen(["open", url])
    try:
        return webbrowser.open(url, new=2)  # 2 means: open in a new tab, if possible
    except TypeError:  # See https://bugs.python.org/msg322439
        return webbrowser.open(url, new=2)
