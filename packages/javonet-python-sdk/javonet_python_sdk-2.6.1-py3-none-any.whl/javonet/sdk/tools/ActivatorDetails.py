from typing import Any, Optional, Type

class ActivatorDetails:
    def __init__(self, type_: Type, arguments: Optional[list[Any]] = None):
        self.type = type_
        self.arguments = arguments or []