from typing import Optional, Any
from dataclasses import dataclass

@dataclass
class BaseActionResult:
    finished: bool
    success: bool
    message: Optional[str] = None
