from __future__ import annotations
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, Any

class RequestResult(Enum):
    SUCCESS = 1
    FAILED = 0


@dataclass
class RequestResponse:
    """ A wrapper around a client's request to indicate the cli
    how to display the result (as FAILED or SUCCEDD)
    """
    status: RequestResult
    content: Any



"""

I'm using Protocol instead of ABC because I only need uniform calling's behaviors and not structure.
By the way, it's usually better to make the request "functionnal" and not class related if there is no
real need for internal class storage or reusability which should be kept in profiles instead.
"""
class ProtocolClient(Protocol):

    def request(self, request: Any) -> RequestResponse:
        raise NotImplementedError

    def __enter__(self) -> ProtocolClient:
        pass

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass