"""
This script configures the Python environment by modifying `sys.path` to include the
project's `src/` directory.

By adding the `src/` folder to the system path, it enables absolute imports of internal
modules from the `src` directory, allowing modules to be imported using
`import module_name` instead of relative paths.

Useful when running scripts or tests located outside the `src/` directory
(e.g., in `tests/` or `scripts/` folders).
"""

import os
import sys

# Add the src/ directory to sys.path for module resolution
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
