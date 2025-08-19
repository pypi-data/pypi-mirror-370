from enum import Enum
from dataclasses import dataclass
from collections import defaultdict
from typing import Callable, List, Optional, Tuple, Union

from ._base import ApiComponent
from dooit.ui.api.events import ModeType

KeyBindType = defaultdict[str, defaultdict[str, Optional["DooitFunction"]]]
KeyType = Union[str, List[str]]


@dataclass
class DooitFunction:
    callback: Callable
    description: str = ""
    group: str = ""

    def __post_init__(self):
        self.description = self.description.strip("\n")


class KeyMatchType(Enum):
    NoMatchFound = "NoMatchFound"
    MultipleMatchFound = "MultipleMatchFound"
    MatchFound = "MatchFound"


@dataclass
class KeyMatch:
    match_type: KeyMatchType
    function: Optional[DooitFunction] = None

    @staticmethod
    def no_match():
        return KeyMatch(match_type=KeyMatchType.NoMatchFound)

    @staticmethod
    def multiple_match():
        return KeyMatch(match_type=KeyMatchType.MultipleMatchFound)

    @staticmethod
    def match_found(func: DooitFunction):
        return KeyMatch(match_type=KeyMatchType.MatchFound, function=func)


class KeyManager(ApiComponent):
    def __init__(self, get_mode: Callable) -> None:
        self.keybinds: KeyBindType = defaultdict(lambda: defaultdict(lambda: None))
        self._inputs: List[str] = []
        self.get_mode = get_mode

    @property
    def groups(self) -> List[str]:
        return list(
            sorted(set(func.group for func in self.keybinds["NORMAL"].values() if func))
        )

    def get_keybinds_by_group(self, group: str) -> List[Tuple[str, DooitFunction]]:
        return [
            (key, func)
            for key, func in self.keybinds["NORMAL"].items()
            if func and func.group == group
        ]

    def __set_key(
        self,
        mode: ModeType,
        key: str,
        callback: Callable,
        description: Optional[str],
        group: str,
    ) -> None:
        self.keybinds[mode][key] = DooitFunction(
            callback, description or callback.__doc__ or "", group
        )

    def set(
        self,
        keys: KeyType,
        callback: Callable,
        description: Optional[str] = None,
        group: str = "",
    ) -> None:
        if isinstance(keys, str):
            keys = [keys]

        for key in keys:
            self.__set_key("NORMAL", key, callback, description, group)

    @property
    def input(self) -> str:
        formatted = ""
        for i in self._inputs:
            if len(i) > 1:
                formatted += f"<{i}>"
            else:
                formatted += i

        return formatted

    def clear_input(self):
        self._inputs.clear()

    def _find_matched_functions(self) -> List[DooitFunction]:
        keybinds = self.keybinds[self.get_mode()].items()
        return [func for key, func in keybinds if key.startswith(self.input) and func]

    def search_for_key(self) -> KeyMatch:
        matched = self._find_matched_functions()
        if not matched:
            self.clear_input()
            return KeyMatch.no_match()

        if len(matched) > 1 or self.input not in self.keybinds[self.get_mode()]:
            return KeyMatch.multiple_match()

        self.clear_input()
        return KeyMatch.match_found(matched[0])

    def register_key(self, key: str) -> KeyMatch:
        if key == "escape":
            self.clear_input()
            return KeyMatch.no_match()

        self._inputs.append(key)
        return self.search_for_key()
