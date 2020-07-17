from abc import abstractmethod, ABCMeta


class ItemAttributes:
    def __init__(self, name: str = None, ignore: bool = False):
        self.name = name
        self.ignore = ignore

    def is_named(self) -> bool:
        return self.name is not None

    def is_ignored(self) -> bool:
        return self.ignore

    def __repr__(self):
        return f"ItemAttributes(name={self.name!r}, ignore={self.ignore!r})"


class AbstractItem(metaclass=ABCMeta):
    @abstractmethod
    def generate_condition(self) -> str:
        pass

    @staticmethod
    def is_nested() -> bool:
        return False


class NestedItemMixin:
    @staticmethod
    def is_nested() -> bool:
        return True
