from typing import Dict


class State:
    def __init__(self, name: str = None):
        self.name = name or f"state_{id(self)}"

    def __eq__(self, other):
        if isinstance(other, State):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        return False


class StatsGroupMeta(type):
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        cls._states = {}

        for attr_name, attr_value in namespace.items():
            if not attr_name.startswith("_") and not callable(attr_value):
                state = State(name=f"{name}.{attr_name}")
                setattr(cls, attr_name, state)
                cls._states[attr_name] = state

        return cls


class StatsGroup(metaclass=StatsGroupMeta):
    @classmethod
    def get_states(cls) -> Dict[str, State]:
        return cls._states.copy()
