import attr


class MessagePart:
    """
    Base class for all driver message parts.
    """

    type: str


@attr.s(auto_attribs=True, kw_only=True)
class TextMessagePart(MessagePart):
    content: str = ""


@attr.s(auto_attribs=True, kw_only=True)
class InlineDataMessagePart(MessagePart):
    content: bytes = b""


@attr.s(auto_attribs=True, kw_only=True)
class FileDataMessagePart(MessagePart):
    content: str = ""


@attr.s(auto_attribs=True, kw_only=True)
class VideoMetadataMessagePart(MessagePart):
    content: dict = attr.Factory(dict)


@attr.s(auto_attribs=True, kw_only=True)
class CodeExecutionResultMessagePart(MessagePart):
    content: str = ""
    stdout: str = ""
    stderr: str = ""


@attr.s(auto_attribs=True, kw_only=True)
class ExecutableCodeMessagePart(MessagePart):
    content: str = ""


@attr.s(auto_attribs=True, kw_only=True)
class FunctionCallMessagePart(MessagePart):
    tool_call_id: str = ""
    function: object = (
        None  # Should match OpenAI SDK structure (with arguments as JSON string)
    )


@attr.s(auto_attribs=True, kw_only=True)
class FunctionResponseMessagePart(MessagePart):
    name: str = ""
    content: dict = attr.Factory(dict)


@attr.s(auto_attribs=True, kw_only=True)
class ThoughtMessagePart(MessagePart):
    content: bool = False
