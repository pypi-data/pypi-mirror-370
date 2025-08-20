"""A class representing a chunk of control.in file."""

from collections.abc import Sequence
from dataclasses import dataclass
from inspect import isclass

from monty.json import MSONable


@dataclass(kw_only=True)
class AimsControlChunk(MSONable):
    """Get the Aims Control Chunk."""

    keywords: tuple[str] = ()

    def __init_subclass__(cls, **kwargs):
        """Initialize the subclass."""
        super().__init_subclass__(**kwargs)
        keywords = []
        if not cls.keywords:
            for field in cls.__annotations__.values():
                if isclass(field) and issubclass(field, AimsControlChunk):
                    keywords += list(field.keywords)
            cls.keywords = tuple(keywords)

    @classmethod
    def from_strings(cls, config_str: Sequence[str]) -> "AimsControlChunk":
        """Get the Chunk from a string."""
        raise NotImplementedError

    def to_string(self) -> str:
        """Get the string of the chunk."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Get the ControlChunk as a string."""
        return self.to_string()
