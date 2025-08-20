from typing import Annotated

from langchain_aws import ChatBedrock
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from fastapi import FastAPI
import uvicorn

from veri_agents_api.fastapi.thread import create_thread_router

if __name__ == "__main__":
    class State(TypedDict):
        messages: Annotated[list, add_messages]

    graph_builder = StateGraph(State)

    llm = ChatBedrock(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0") # pyright: ignore[reportCallIssue]

    def chatbot(state: State):
        return {"messages": [llm.invoke(state["messages"])]}

    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.set_entry_point("chatbot")
    graph_builder.set_finish_point("chatbot")




    # in-memory persistence
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)

    # veri-agents convenience router
    thread_router = create_thread_router(
        # same graph for every request
        get_graph=lambda req: graph,
        # same thread for every request
        get_thread_id=lambda req: "inmem"
    )

    # root fastapi app
    app = FastAPI()
    app.include_router(thread_router)

    uvicorn.run(app, port=5000, log_level="info")
    # you can now access:
    #   GET  /openapi.json
    #   POST /invoke
    #   POST /stream
    #   GET  /history
    #   GET  /feedback
    #   POST /feedback
