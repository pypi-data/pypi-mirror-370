from abc import ABC
from functools import total_ordering

from chordist.modifier import Modifier
from chordist.note import Note


@total_ordering
class AbstractChord(ABC):
    base: Note
    modifier: Modifier | None

    def __eq__(self, value: object) -> bool:
        if isinstance(value, str):
            for idx in range(len(value), 0, -1):
                if self.base == value[:idx]:
                    if idx < len(value):
                        if self.modifier == value[idx:]:
                            return True
                    elif self.modifier is None:
                        return True
            return False
        return isinstance(value, AbstractChord) and value.base == self.base and value.modifier == self.modifier

    def __lt__(self, other: "AbstractChord"):
        if self.base.name != other.base.name:
            return self.base.name < other.base.name
        if not other.modifier:
            return False
        if not self.modifier:
            return True
        return self.modifier.name < other.modifier.name
