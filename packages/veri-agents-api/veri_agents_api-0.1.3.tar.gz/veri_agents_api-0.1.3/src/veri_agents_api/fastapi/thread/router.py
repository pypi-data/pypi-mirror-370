import asyncio
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
import json
import logging
from typing import Annotated, Any, AsyncGenerator, Dict, List, Optional, Tuple, Callable
from uuid import uuid4

from fastapi import Depends, HTTPException, Request, APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.runnables import RunnableConfig
from langgraph.graph.graph import CompiledGraph

from .schema import (
    ChatMessage,
    StreamInput,
    InvokeInput,
)
from veri_agents_api.threads_util import ThreadInfo, ThreadsCheckpointerUtil
from veri_agents_api.util.awaitable import as_awaitable, MaybeAwaitable

log = logging.getLogger(__name__)

class TokenQueueStreamingHandler(AsyncCallbackHandler):
    """LangChain callback handler for streaming LLM tokens to an asyncio queue."""

    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        if token:
            await self.queue.put(token)

@dataclass
class ThreadContext:
    id: str
    graph: CompiledGraph
    config: Optional[RunnableConfig] = None

def create_thread_router(
    *,
    get_thread: Callable[..., AbstractAsyncContextManager[ThreadContext]],
    on_new_thread: Callable[[str, ThreadInfo | None, InvokeInput, Request], MaybeAwaitable[None]] = lambda thread_id, thread_info, invoke_input, request: None,
    # InvokeInputCls: Type[InvokeInput] = InvokeInput,
    **router_kwargs
):
    """
    POST /invoke
    POST /stream
    GET /history
    GET /feedback
    POST /feedback
    """

    router = APIRouter(**router_kwargs)

    def _parse_input(user_input: InvokeInput, thread_id: str, invoke_recvd_runnable_config: RunnableConfig | None) -> Tuple[Dict[str, Any], str]:
        run_id = uuid4()
        input_message = ChatMessage(type="human", content=user_input.message)

        runnable_config = invoke_recvd_runnable_config or RunnableConfig()

        runnable_config["configurable"] = {
            **{
                # used by checkpointer
                "thread_id": thread_id,

                "_has_threadinfo": True,

                # "args": user_input.args,
            }, 
            **(runnable_config.get("configurable", {}))
        }

        kwargs = dict(
            input={"messages": [input_message.to_langchain()]},
            config=runnable_config
        )
        return kwargs, str(run_id)

    @router.post("/invoke")
    async def invoke(invoke_input: InvokeInput, request: Request, thread_ctx_mngr: Annotated[AbstractAsyncContextManager[ThreadContext], Depends(get_thread)]) -> ChatMessage:
        """
        Invoke the agent with user input to retrieve a final response.

        Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
        is also attached to messages for recording feedback.
        """

        async with thread_ctx_mngr as thread_ctx:
            thread_info = await ThreadsCheckpointerUtil.get_thread_info(thread_ctx.id, thread_ctx.graph.checkpointer)
            kwargs, run_id = _parse_input(invoke_input, thread_ctx.id, thread_ctx.config)

            # # store this thread in the database if a new one
            # if user_input.thread_id not in router.state.threads:
            #     thread_info = ThreadInfo(
            #         thread_id=user_input.thread_id,
            #         user=principal,
            #         workflow_id=user_input.workflow,
            #         name=user_input.message[:50],
            #         metadata={"router": user_input.router},
            #     )
            #     router.state.threads[user_input.thread_id] = thread_info
            #     await graph.checkpointer.aput_thread(thread_info)

            await as_awaitable(on_new_thread(thread_ctx.id, thread_info, invoke_input, request))

            # langfuse_handler = CallbackHandler(
            #     public_key=router.state.cfg.logging.langfuse.public_key,
            #     secret_key=router.state.cfg.logging.langfuse.secret_key,
            #     host=router.state.cfg.logging.langfuse.host,
            #     # user_id=principal,
            #     session_id=user_input.thread_id,
            #     trace_name=user_input.message[:50],
            # )
            # kwargs["config"]["callbacks"] = [] # was [langfuse_handler]
            # kwargs["config"]["configurable"]["workflow_id"] = user_input.workflow
            try:
                response = await thread_ctx.graph.ainvoke(**kwargs)
                output = ChatMessage.from_langchain(response["messages"][-1])
                output.run_id = str(run_id)
                return output
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    @router.post("/stream")
    async def stream_agent(stream_input: StreamInput, request: Request, thread_ctx_mngr: Annotated[AbstractAsyncContextManager[ThreadContext], Depends(get_thread)]) -> StreamingResponse:
        """
        Stream the agent's response to a user input, including intermediate messages and tokens.

        Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
        is also attached to all messages for recording feedback.
        """


        async def message_generator() -> AsyncGenerator[str, None]:
            """
            Generate a stream of messages from the agent.

            This is the workhorse method for the /stream endpoint.
            """   
            async with thread_ctx_mngr as thread_ctx:

                thread_info = await ThreadsCheckpointerUtil.get_thread_info(thread_ctx.id, thread_ctx.graph.checkpointer)

                kwargs, run_id = _parse_input(stream_input, thread_ctx.id, thread_ctx.config)

                await as_awaitable(on_new_thread(thread_ctx.id, thread_info, stream_input, request))

                # # store this thread in the database if a new one
                # if user_input.thread_id not in router.state.threads:
                #     thread_info = ThreadInfo(
                #         thread_id=user_input.thread_id,
                #         user=principal,
                #         workflow_id=user_input.workflow,
                #         name=user_input.message[:50],
                #         metadata={"router": user_input.router},
                #     )
                #     router.state.threads[user_input.thread_id] = thread_info
                #     await graph.checkpointer.aput_thread(thread_info)

                # langfuse_handler = CallbackHandler(
                #     public_key=router.state.cfg.logging.langfuse.public_key,
                #     secret_key=router.state.cfg.logging.langfuse.secret_key,
                #     host=router.state.cfg.logging.langfuse.host,
                #     user_id=principal,
                #     session_id=user_input.thread_id,
                #     trace_name=user_input.message[:50],
                # )
                # kwargs["config"]["configurable"]["workflow_id"] = stream_input.workflow
                
                # Process the queue and yield messages over the SSE stream.
                async for s in thread_ctx.graph.astream(**kwargs, stream_mode="updates"):
                    log.info("Got from queue: %s: %s", type(s), s)
                    if isinstance(s, str):
                        # str is an LLM token
                        yield f"data: {json.dumps({'type': 'token', 'content': s})}\n\n"
                        continue

                    # Otherwise, s should be a dict of state updates for each node in the graph.
                    # s could have updates for multiple nodes, so check each for messages.
                    new_messages = []
                    for _, state in s.items():
                        new_messages.extend(state["messages"])
                    for message in new_messages:
                        try:
                            chat_message = ChatMessage.from_langchain(message)
                            chat_message.run_id = str(run_id)
                        except Exception as e:
                            yield f"data: {json.dumps({'type': 'error', 'content': f'Error parsing message: {e}'})}\n\n"
                            continue
                        # LangGraph re-sends the input message, which feels weird, so drop it
                        if (
                            chat_message.type == "human"
                            and chat_message.content == stream_input.message
                        ):
                            continue
                        yield f"data: {json.dumps({'type': 'message', 'content': chat_message.dict()})}\n\n"

                yield "data: [DONE]\n\n"

        return StreamingResponse(
            message_generator(),
            media_type="text/event-stream",
        )

    @router.get("/history")
    async def get_history(request: Request, thread_ctx_mngr: Annotated[AbstractAsyncContextManager[ThreadContext], Depends(get_thread)]) -> List[ChatMessage]:
        """
        Get the history of a thread.
        """

        async with thread_ctx_mngr as thread_ctx:

            # agent: CompiledGraph = router.state.workflows[workflow].get_graph()
            config = RunnableConfig(configurable={
                # used by checkpointer
                "thread_id": thread_ctx.id,
            })
            state = await thread_ctx.graph.aget_state(config)
            messages = state.values.get("messages", [])

            converted_messages: List[ChatMessage] = []
            for message in messages:
                try:
                    chat_message = ChatMessage.from_langchain(message)
                    converted_messages.append(chat_message)
                except Exception as e:
                    log.error(f"Error parsing message: {e}")
                    continue
            return converted_messages

    return router
