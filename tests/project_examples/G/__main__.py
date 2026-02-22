## @file __main__.py
# @brief Execute git-alias CLI when module is invoked with `python -m`.
# @details Imports the canonical `main` dispatcher and forwards process exit status.
from .core import main
import sys


## @brief Trigger CLI dispatcher for module-execution entrypoint.
# @details Invokes `main()` and propagates returned exit code via `sys.exit(...)`.
if __name__ == "__main__":
    sys.exit(main())
