from jcweaver.api.api import input_prepare, output_prepare
from jcweaver.api.decorators import lifecycle
from jcweaver.core.model import DATASET, PLATFORM_MODELARTS


@lifecycle(platform=PLATFORM_MODELARTS)
def my_io():
    dataset = input_prepare(DATASET, "bootfile.py")
    print("dataset path: ", dataset.path)
    output = output_prepare(DATASET, "output.pt")
    print("output file path: ", output.path)


def test_io():
    my_io()
