from typing import cast

from .schema import ThreadInfo
from langgraph.types import Checkpointer
from langgraph.checkpoint.base import BaseCheckpointSaver

class ThreadsCheckpointerUtil:
    @staticmethod
    async def get_thread_info(thread_id: str, checkpointer: Checkpointer) -> ThreadInfo | None:
        if not isinstance(checkpointer, BaseCheckpointSaver):
            raise Exception("checkpointer must be instance of BaseCheckpointSaver")

        chk_tuple = (await checkpointer.aget_tuple(config={
            "configurable": {"_has_threadinfo": True, "thread_id": thread_id}}))

        if chk_tuple is None:
            return None

        thread_metadata = chk_tuple.metadata
        return ThreadInfo(
            thread_id=thread_id,
        )

    @staticmethod
    async def list_threads(checkpointer: Checkpointer) -> list[ThreadInfo]:
        if not isinstance(checkpointer, BaseCheckpointSaver):
            raise Exception("checkpointer must be instance of BaseCheckpointSaver")

        init_step_checkpoints = checkpointer.alist(config=None, filter={ 'step': -1 }) # get initial steps only - this ensures we are only getting one thread_id from the checkpoints of a thread

        all_accessible_thread_ids: list[str] = []
        async for checkpoint in init_step_checkpoints:
            thread_id = cast(str | None, checkpoint.config.get("configurable", {"thread_id": None}).get("thread_id", None))
            if thread_id is not None: # and allow_access_thread(thread_id, request) ?
                all_accessible_thread_ids.append(cast(str, thread_id))

        all_thread_info: list[ThreadInfo] = []
        for thread_id in all_accessible_thread_ids:
            thread_info = await ThreadsCheckpointerUtil.get_thread_info(thread_id, checkpointer)
            if thread_info is not None:
                all_thread_info.append(thread_info)

        return all_thread_info
