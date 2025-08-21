from typing import Any, Dict, Literal
from dataclasses import dataclass

class History:
    
    def __init__(self) -> None:
        pass

type HistoryItem = ToolCallItem | UserMessageItem

@dataclass
class ToolCallItem:
    reasoning: str
    index: int
    tool: str
    finished_at: str
    params: Dict[str, Any]
    result_status: Literal["success", "error"]
    result_content: str


@dataclass
class UserMessageItem:
    message: str