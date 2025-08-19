
class TaskRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, task_info: dict):
        name = task_info["name"]
        if name in self._registry:
            raise ValueError(f"Task '{name}' already registered.")
        self._registry[name] = task_info

    def get(self, name: str):
        return self._registry.get(name)

    def all(self):
        return list(self._registry.values())

    def clear(self):
        self._registry.clear()


registry = TaskRegistry()
