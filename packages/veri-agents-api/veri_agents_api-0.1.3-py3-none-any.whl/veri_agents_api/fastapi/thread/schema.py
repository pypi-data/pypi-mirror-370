import re
from datetime import datetime
from typing import Dict, Any, List, Literal, Optional, Union
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
    ToolCall,
    message_to_dict,
    messages_from_dict,
)
from pydantic import BaseModel, Field


class InvokeInput(BaseModel):
    """Basic user input for the agent."""

    message: str = Field(
        description="User input to the agent.",
        examples=["What is the weather in Tokyo?"],
    )
    # args: Dict[str, Any] = Field(
    #     description="Arguments to pass to the workflow.",
    #     default={},
    #     examples=[{"kb": "veritone_support"}],
    # )
    # user: Optional[str] = Field(
    #     description="A user identifier to validate the user in knowledge bases and other tools.",
    #     default=None,
    #     examples=["jjohnson", "ccarlson"],
    # )
    # thread_id: str = Field(
    #     description="Thread ID to persist and continue a multi-turn conversation.",
    #     examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    # )


class StreamInput(InvokeInput):
    """User input for streaming the agent's response."""

    stream_tokens: bool = Field(
        description="Whether to stream LLM tokens to the client.",
        default=True,
    )


class AgentResponse(BaseModel):
    """Response from the agent when called via /invoke."""

    message: Dict[str, Any] = Field(
        description="Final response from the agent, as a serialized LangChain message.",
        examples=[
            {
                "message": {
                    "type": "ai",
                    "data": {
                        "content": "The weather in Tokyo is 70 degrees.",
                        "type": "ai",
                    },
                }
            }
        ],
    )


class ChatMessage(BaseModel):
    """Message in a chat."""

    type: Literal["human", "ai", "tool", "system"] = Field(
        description="Role of the message.",
        examples=["human", "ai", "tool"],
    )
    content: Union[str, list[Union[str, dict]]] = Field(
        description="Content of the message.",
        examples=["Hello, world!"],
    )
    tool_calls: List[ToolCall] = Field(
        description="Tool calls in the message.",
        default=[],
    )
    tool_call_id: str | None = Field(
        description="Tool call that this message is responding to.",
        default=None,
        examples=["call_Jja7J89XsjrOLA5r!MEOW!SL"],
    )
    run_id: str | None = Field(
        description="Run ID of the message.",
        default=None,
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    original: Dict[str, Any] = Field(
        description="Original LangChain message in serialized form.",
        default={},
    )

    @classmethod
    def from_langchain(cls, message: BaseMessage) -> "ChatMessage":
        """Create a ChatMessage from a LangChain message."""
        original = message_to_dict(message)
        match message:
            case HumanMessage():
                human_message = cls(
                    type="human", content=message.content, original=original
                )
                return human_message
            case AIMessage():
                ai_message = cls(type="ai", content=message.content, original=original)
                if message.tool_calls:
                    ai_message.tool_calls = message.tool_calls
                return ai_message
            case ToolMessage():
                tool_message = cls(
                    type="tool",
                    content=message.content,
                    tool_call_id=message.tool_call_id,
                    original=original,
                )
                return tool_message
            case SystemMessage():
                # System messages are not typically used in chat, but we can handle them
                # by converting them to a human message with the content.
                system_message = cls(
                    type="system", content=message.content, original=original
                )
                return system_message
            case _:
                raise ValueError(
                    f"Unsupported message type: {message.__class__.__name__}"
                )

    def to_langchain(self) -> BaseMessage:
        """Convert the ChatMessage to a LangChain message."""
        if self.original:
            return messages_from_dict([self.original])[0]
        match self.type:
            case "human":
                return HumanMessage(content=self.content)
            case _:
                raise NotImplementedError(f"Unsupported message type: {self.type}")

    def pretty_print(self) -> None:
        """Pretty print the ChatMessage."""
        lc_msg = self.to_langchain()
        lc_msg.pretty_print()

    def get_artifact(self) -> Optional[Dict[str, Any]]:
        """Get the artifact from the message if there is one."""
        if (
            self.original.get("data")
            and self.original["data"].get("artifact")
            and self.original["data"]["artifact"]
        ):
            return self.original["data"]["artifact"]
        return None

    def get_text(self, thinking: bool = True) -> str:
        """Get all texts from a message, this might merge multiple content parts into one.

        Args:
            thinking (bool): If True, include thinking messages. Defaults to True.
        """
        if not self.content:
            return ""
        if isinstance(self.content, str):
            text = self.content
        elif isinstance(self.content, list):
            text = ""
            for t in self.content:
                if isinstance(t, str):
                    text += t
                elif isinstance(t, dict):
                    if t.get("type", "") == "text":
                        text += t.get("text", "")
        else:
            text = ""
        # remove any text between thinking tags
        if not thinking:
            text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL)
        return text


class Feedback(BaseModel):
    """Feedback for a run."""

    message_id: str = Field(
        description="Message ID to record feedback for.",
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    # thread_id: str = Field(
    #     description="Thread ID to record feedback for.",
    #     examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    # )
    score: float = Field(
        description="Feedback score.",
        examples=[0.8],
    )
    kwargs: Dict[str, Any] = Field(
        description="Additional feedback kwargs, passed to LangSmith.",
        default={},
        examples=[{"comment": "In-line human feedback"}],
    )
    creation: datetime = Field(default_factory=datetime.now)
