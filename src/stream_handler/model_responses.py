class   ModelResponseHandler:
    @staticmethod
    async def stream_model_response(model_name, stream):
        try:
            if any(model_type in model_name for model_type in ["openai", "gpt", "o1", "deepseek"]):
                async for message in stream:
                    if hasattr(message, 'choices') and message.choices and message.choices[0].delta:
                        yield message.choices[0].delta.content

            elif "claude" in model_name:
                async for event in stream:
                    if event.type == "text":
                        yield event.text
            else:
                raise Exception(f"Unsupported model or no output available. {model_name} {stream}")
        except Exception:
            yield ""