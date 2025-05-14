from typing import AsyncGenerator
from abc import ABC, abstractmethod

from src.stream_handler.constants import MessageType, StreamConfig
from src.stream_handler.strategies import StreamStrategyFactory, StreamStrategyType


class StreamHandler(ABC):
    def __init__(self, config: StreamConfig, strategy_type: StreamStrategyType = StreamStrategyType.STRING):
        self.config = config
        self.strategy = StreamStrategyFactory.create_strategy(strategy_type)

    @abstractmethod
    async def handle_stream(self, response, **kwargs) -> AsyncGenerator[str, None]:
        pass

    def format_output(self, content: str, msg_type: str = MessageType.DATA) -> str:
        """Format the output using the selected strategy"""
        return self.strategy.format_output(content, msg_type)


class DefaultStreamHandler(StreamHandler):
    def __init__(self, config: StreamConfig, strategy_type: StreamStrategyType = StreamStrategyType.STRING):
        super().__init__(config, strategy_type)

    async def handle_stream(self, response, **kwargs) -> AsyncGenerator[str, None]:
        try:
            formatted_response = self.format_output(response, msg_type=MessageType.DATA)
            yield formatted_response
        except Exception as e:
            error_msg = f"Error in default stream handler: {str(e)}"
            yield self.format_output(error_msg, msg_type=MessageType.ERROR)


class StreamHandlerFactory:
    @staticmethod
    def create_handler(handler_type: str, config: StreamConfig,
                       strategy_type: StreamStrategyType = StreamStrategyType.STRING, **kwargs) -> StreamHandler:
        handlers = {
            'default': DefaultStreamHandler,
            'combined': CombinedStreamHandler  # New combined handler for multiple markers
        }
        handler_class = handlers.get(handler_type, DefaultStreamHandler)
        return handler_class(config, strategy_type, **kwargs)


# Optional: Create a combined handler that can handle both tags and summaries
class CombinedStreamHandler(StreamHandler):
    def __init__(self, config: StreamConfig, strategy_type: StreamStrategyType = StreamStrategyType.STRING, **kwargs):
        super().__init__(config, strategy_type)
        self.result = {
            'response_text': ''
        }

    async def handle_stream(self, response, **kwargs):
        model = kwargs['model']
        output_text = ""
        response_text = ""
        full_response = ""
        yield_substr = ""

        if isinstance(response, str):
            self.result['response_text'] = response
            yield self.format_output(response, msg_type=MessageType.DATA)
            return

        try:
            async for output in ModelResponseHandler.stream_model_response(model, response):
                if output is None:
                    continue
                full_response += output

                if yield_substr:
                    output_text += yield_substr
                    yield_substr = ""

                if output_text:
                    yield self.format_output(output_text, msg_type=MessageType.DATA)
                    output_text = ""

            if output_text:
                yield self.format_output(output_text, msg_type=MessageType.DATA)

            self.result['response_text'] = full_response
        except Exception as e:
            error_msg = f"Error processing stream: {str(e)}"
            yield self.format_output(error_msg, msg_type=MessageType.ERROR)

    def get_result(self):
        return self.result
