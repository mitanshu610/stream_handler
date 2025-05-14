from abc import ABC, abstractmethod
import json
from typing import Union, Dict, Any
from src.stream_handler.constants import streaming_token


class StreamStrategyType:
    STRING = "string"
    OBJECT = "object"

class StreamStrategy(ABC):
    @abstractmethod
    def format_output(self, content: str, msg_type: str = "data") -> str:
        """Format the output according to the strategy"""
        pass

class StringStreamStrategy(StreamStrategy):
    def format_output(self, content: str, msg_type: str = "data") -> str:
        """Format output as a string with type prefix"""
        return f"{msg_type}: {content}"

class ObjectStreamStrategy(StreamStrategy):
    def format_output(self, content: Union[str, Dict], msg_type: str = "data") -> str:
        """Format output as a JSON string containing type and content"""
        if isinstance(content, str):
            content = {"content": content}
        output_obj = {"type": msg_type, "payload": content}
        return f"{streaming_token}: {json.dumps(output_obj)}"

class StreamStrategyFactory:
    @staticmethod
    def create_strategy(strategy_type: StreamStrategyType = StreamStrategyType.STRING) -> StreamStrategy:
        """Create and return the appropriate stream strategy"""
        strategies = {
            StreamStrategyType.STRING: StringStreamStrategy(),
            StreamStrategyType.OBJECT: ObjectStreamStrategy()
        }
        return strategies.get(strategy_type, StringStreamStrategy())
