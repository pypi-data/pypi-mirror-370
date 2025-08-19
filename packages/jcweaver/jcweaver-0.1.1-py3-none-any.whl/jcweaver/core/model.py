from jcweaver.adapter.base.BaseAdapter import BaseAdapter

PLATFORM = "platform"
PLATFORM_OPENI = "openi"
PLATFORM_MODELARTS = "modelarts"

DATASET = "dataset"
MODEL = "model"
CODE = "code"


class InputContext:
    def __init__(self, adapter: BaseAdapter, path: str):
        self.adapter = adapter
        self.path = path


class OutputContext:
    def __init__(self, adapter: BaseAdapter, path: str):
        self.adapter = adapter
        self.path = path
