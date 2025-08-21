from __future__ import annotations
import time
from com_tools.base import RequestResponse, RequestResult


class DemoClient:

    def __enter__(self) -> DemoClient:
        return self

    def __exit__(self, *args) -> None:
        pass

    def __init__(self) -> None:
        pass

    def connect(self) -> None:
        time.sleep(1)

    
    def request(self) -> RequestResponse:

        return RequestResponse(
            status=RequestResult.SUCCESS,
            content=f"Successfull demo request !"
        )