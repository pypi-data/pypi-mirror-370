from typing import Protocol

from pydantic import JsonValue

type IdentityId = str
type LocationPath = list[IdentityId]
type EventId = str
type IdentityName = str


class RequestWithOffset(Protocol):
    def __call__(self, *, offset: int) -> JsonValue: ...  # pragma: no cover # this is a type definition
