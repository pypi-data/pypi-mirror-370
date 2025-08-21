from pydantic import BaseModel


class SystemEvent(BaseModel, frozen=True):
    """
    An system event used for tracing
    """

    event_type: str
    start_time: float
    thread_id: int = 0
    end_time: float = 0.0
