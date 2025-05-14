from pydantic import BaseModel

#TODO: Change it according to your convenience
streaming_token = "x-streaming-response"


class MessageType:
    ERROR = "error"
    DATA = "data"
    PROGRESS = "progress"
    STREAM_START = "stream_start"
    STREAM_END = "stream_end"


class StreamConfig(BaseModel):
    rand_min: int
    rand_max: int