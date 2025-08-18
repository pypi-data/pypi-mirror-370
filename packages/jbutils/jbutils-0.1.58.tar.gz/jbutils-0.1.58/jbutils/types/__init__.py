"""Common types for the jbutils package"""

import argparse
import re

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar, Optional, Pattern, Sequence, Literal, Iterable

from ruamel.yaml.comments import CommentedMap, CommentedSeq, Comment

# General Typing
T = TypeVar("T")
OptStr = Optional[str]
OptInt = Optional[int]
OptFloat = Optional[float]
OptDict = Optional[dict]
OptList = Optional[list]
Opt = Optional[T]

# Function Types
Predicate = Callable[[T], bool]
Function = Callable[..., None]
TFunction = Callable[..., T]

# Other
Patterns = Sequence[str | Pattern[str]]
DataPathList = list[str] | list[str | int] | list[int]
DataPath = DataPathList | str | int

SubReturn = Literal["out", "err", "both"]
""" String literal type representing the output choices for cmdx """


@dataclass
class CommandArg:
    name: str = ""
    flag: str = ""
    action: str = ""
    nargs: str | int | None = None
    const: Any = None
    default: Any = None
    arg_type: type | None = None
    choices: Iterable | None = None
    required: bool = False
    help: str | None = None
    metavar: str | tuple[str, ...] | None = None
    dest: str | None = None
    version: str | None = None

    name_or_flags: list[str] = field(default_factory=list)
    arg_name: str = ""

    def __post_init__(self) -> None:
        ws_re = re.compile(r"\s+")
        self.name = ws_re.sub("-", self.name.strip())
        self.name_or_flags.append(self.name)
        if self.flag:
            self.name_or_flags.append(self.flag)

        prefix_re = re.compile(r"^-+")
        space_re = re.compile(r"[-_ ]+")
        self.arg_name = prefix_re.sub("", self.name)
        self.arg_name = space_re.sub("_", self.arg_name)


__all__ = [
    "CommandArg",
    "Comment",
    "CommentedMap",
    "CommentedSeq",
    "OptStr",
    "OptInt",
    "OptFloat",
    "OptDict",
    "OptList",
    "Opt",
    "Patterns",
    "Predicate",
    "Function",
    "SubReturn",
    "TFunction",
    "T",
]
