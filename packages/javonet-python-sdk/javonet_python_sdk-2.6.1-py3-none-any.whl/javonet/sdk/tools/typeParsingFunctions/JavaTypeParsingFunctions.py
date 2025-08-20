from datetime import datetime
from typing import Callable, Dict, Any
from javonet.sdk.InvocationContext import InvocationContext

def parse_datetime(ic: InvocationContext) -> datetime:
    try:
        timestamp_result = ic.invoke_instance_method("getEpochSecond").execute()
        if timestamp_result is None:
            raise ValueError("invoke_instance_method('getEpochSecond').execute() returned None")

        timestamp = timestamp_result.get_value()
        if timestamp is None:
            raise ValueError("getEpochSecond.get_value() returned None")
                
        return datetime.fromtimestamp(timestamp)
            
    except Exception as e:
        raise ValueError(f"Failed to parse datetime: {e}") from e

ParsingFunctions: Dict[str, Callable[[InvocationContext], Any]] = {
        'datetime.datetime':  parse_datetime,
    }