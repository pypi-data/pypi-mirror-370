## `src/moskit_cli/__init__.py`
```python
from .client import MoskitClient
from .enums import Direction, SpeedLevel

__all__ = ["MoskitClient", "Direction", "SpeedLevel"]
__version__ = "0.1.0"