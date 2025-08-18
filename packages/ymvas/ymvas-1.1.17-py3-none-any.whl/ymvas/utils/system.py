import json, os, platform
from functools import lru_cache


@lru_cache(maxsize=None)
def sys_platform():
    system  = platform.system()
    shell   = os.environ.get("SHELL", "")
    msystem = os.environ.get("MSYSTEM", "")
    
    # Detect Git Bash on Windows
    is_windows_git_bash = (system == "Windows") and (
        "bash" in shell or msystem.startswith("MINGW")
    )

    if is_windows_git_bash:
        return "git-bash"
    elif system == "Windows":
        return "widnows"
    elif system == "Darwin":
        return "mac"
    return 'unix'


@lru_cache(maxsize=None)
def global_config_dir():
    return os.path.join({
        "git-bash" : os.path.expanduser("~/.config"),
        "widnows"  : os.environ.get("APPDATA", os.path.expanduser(
            "~\\AppData\\Roaming"
        )),
        "mac"      : os.path.expanduser("~/Library/Application Support"),
        'unix'     : os.environ.get("XDG_CONFIG_HOME", os.path.expanduser(
            "~/.config"
        ))
    }.get(sys_platform(), '~/.config'), 'ymvas')


@lru_cache(maxsize=None)
def global_config_file():
    return os.path.join(global_config_dir(),'config.json')


@lru_cache(maxsize=None)
def get_global_config():
    f = global_config_file()
    if not os.path.exists(f):
        return {}
    try:
        with open(f) as fs:
            return json.loads(fs.read())
    except Exception:
        return {}
    return {}


