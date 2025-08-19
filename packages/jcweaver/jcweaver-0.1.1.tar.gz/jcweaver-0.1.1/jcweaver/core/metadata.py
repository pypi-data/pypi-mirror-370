
from jcweaver.core.registry import registry


def describe_task(name: str) -> dict:
    task = registry.get(name)
    if not task:
        raise ValueError(f"Task '{name}' not found")
    return {
        "name": task["name"],
        "tags": task["tags"],
        "input_schema": task["input_schema"],
        "output_format": task["output_format"]
    }


def list_all_tasks() -> list:
    return [t["name"] for t in registry.all()]
