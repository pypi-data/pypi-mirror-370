import argparse
from pathlib import Path

from jcweaver.adapter.base.BaseAdapter import BaseAdapter
from jcweaver.core.logger import logger
from jcweaver.core.model import DATASET, MODEL, CODE


class ModelArtsAdapter(BaseAdapter):
    def __init__(self):
        import moxing as mox
        self.mox = mox
        self.parser = argparse.ArgumentParser(description='Model Training with input parameter')
        self.output = ""

    def before_task(self, inputs, context: dict):
        print("modelarts before task")

    def after_task(self, outputs, context: dict):
        print("modelarts after task, output", self.output)
        if self.output != "":
            self.mox.file.copy('/cache/model.pth', self.output + 'three_cnn_model.pth')

    def input_prepare(self, data_type: str, file_path: str):
        if data_type == DATASET:
            if not any(a.dest == 'dataset_input' for a in self.parser._actions):
                self.parser.add_argument('--dataset_input', default='./data', type=str,
                                         help='dataset_input (default: %(default)s)')
        elif data_type == MODEL:
            if not any(a.dest == 'model_input' for a in self.parser._actions):
                self.parser.add_argument('--model_input', default='./models', type=str,
                                         help='model_input (default: %(default)s)')
        elif data_type == CODE:
            if not any(a.dest == 'code_input' for a in self.parser._actions):
                self.parser.add_argument('--code_input', default='./src', type=str,
                                         help='code_input (default: %(default)s)')
        else:
            logger.error(f"Unknown data type for input: {data_type}")
            return ""

        args, _ = self.parser.parse_known_args()

        base_path = ""
        if data_type == DATASET:
            base_path = args.dataset_input
        elif data_type == MODEL:
            base_path = args.model_input
        elif data_type == CODE:
            base_path = args.code_input

        path = Path(base_path) / file_path
        # 从path中去除OBS路径前缀：obs://
        local_dir = path.as_posix()[5:]
        # 从OBS拷贝到本地，使用本地路径访问
        self.mox.file.copy_parallel(path.as_posix(), local_dir)
        return local_dir

    def output_prepare(self, data_type: str, file_path: str):
        if not any(a.dest == 'output' for a in self.parser._actions):
            self.parser.add_argument('--output', default='/output', type=str,
                                     help='output (default: %(default)s)')
        args, _ = self.parser.parse_known_args()
        path = Path(args.output) / file_path
        return path.as_posix()
