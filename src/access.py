from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from src.page import Page

@dataclass(frozen=True)
class Access:
    page: Page
    bit_r: int = 0
    bit_m: int = 0
    timestamp: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
