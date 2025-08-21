import os

if "NO_HMR_DAEMON" not in os.environ:
    if os.name == "nt":
        from . import windows
    else:
        from . import posix
