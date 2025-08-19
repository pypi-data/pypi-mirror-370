import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, override


def myexcepthook(type: type[Exception], value: Exception, _):
    print(f"hdfq: {type.__name__}: {value}")


sys.excepthook = myexcepthook


@dataclass
class ContextInfo(ABC):
    @override
    @abstractmethod
    def __repr__(self) -> str:
        pass


@dataclass
class GetStatementContext(ContextInfo):
    second: str
    _first: str | None = None

    @override
    def __repr__(self) -> str:
        assert self.first is not None
        return f'"{self.second}" of attribute "{self.first}"'

    @property
    def first(self) -> str | None:
        return self._first

    @first.setter
    def first(self, value: str):
        self._first = value


@dataclass
class BinaryOpContext(ContextInfo):
    kind: Literal["assignment"]
    side: Literal["left", "right"]

    @override
    def __repr__(self) -> str:
        return f" while parsing {self.side} hand side of {self.kind}"


@dataclass
class FunctionCallContext(ContextInfo):
    kind: Literal["del"]

    @override
    def __repr__(self) -> str:
        return f" while parsing arguments of {self.kind} function"


@dataclass
class DatasetCreationContext(ContextInfo):
    @override
    def __repr__(self) -> str:
        return " while parsing arguments for dataset creation"


class ParseError(Exception):
    def __init__(self, msg: str = "", context: ContextInfo | None = None) -> None:
        super().__init__(msg)
        self.msg: str = msg
        self.context: ContextInfo | None = context

    def _str_context(self) -> str:
        return "" if self.context is None else repr(self.context)

    @override
    def __str__(self) -> str:
        return f"{self.msg}{self._str_context()}"


class EvalError(Exception):
    pass
