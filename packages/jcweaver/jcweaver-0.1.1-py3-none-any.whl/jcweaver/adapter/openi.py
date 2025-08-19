import os

from jcweaver.adapter.base.BaseAdapter import BaseAdapter
from jcweaver.core.logger import logger
from jcweaver.core.model import DATASET, MODEL, CODE


class OpenIAdapter(BaseAdapter):
    def __init__(self):
        from c2net.context import prepare, upload_output
        self._prepare = prepare
        self._upload_output = upload_output
        self.output = ""

    def before_task(self, inputs, context: dict):
        # 可添加日志、预处理等 Hook
        pass

    def after_task(self, outputs, context: dict):
        self._upload_output()

    def input_prepare(self, data_type: str, file_path: str):
        if data_type == DATASET:
            return os.path.join(self._prepare.dataset_path, file_path)
        if data_type == MODEL:
            return os.path.join(self._prepare.pretrain_model_path, file_path)
        if data_type == CODE:
            return os.path.join(self._prepare.code_path, file_path)
        logger.error(f"Unknown data type for input: {data_type}")
        return ""

    def output_prepare(self, data_type: str, file_path: str):
        self.output = os.path.join(self._prepare.output_path, file_path)
        return self.output
