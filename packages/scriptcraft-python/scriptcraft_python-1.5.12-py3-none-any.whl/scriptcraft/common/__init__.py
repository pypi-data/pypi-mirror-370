"""
ScriptCraft Common Utilities Package

This package provides all shared utilities for ScriptCraft tools and pipelines.
Use wildcard imports for internal utilities: `import scriptcraft.common as cu`

For public APIs/distributables, use explicit imports for clear interfaces.
"""

# ===== CORE UTILITIES =====
from .core import *

# ===== REGISTRY SYSTEM =====
from .registry import *

# ===== LOGGING =====
from .logging import *

# ===== DATA PROCESSING =====
from .data import *

# ===== I/O OPERATIONS =====
from .io import *

# ===== CLI UTILITIES =====
from .cli import *

# ===== TIME UTILITIES =====
from .time import *

# ===== PIPELINE UTILITIES =====
from .pipeline import *

# ===== TOOLS UTILITIES =====
from .tools import *

# ===== PLUGINS SYSTEM =====
from .plugins import *

# ===== CONVENIENCE ALIAS =====
# Create cu alias for backward compatibility and convenience
import sys
cu = sys.modules[__name__]
