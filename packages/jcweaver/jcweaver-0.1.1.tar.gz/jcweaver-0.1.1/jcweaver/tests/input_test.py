from jcweaver.api.api import input_prepare
from jcweaver.api.decorators import lifecycle
from jcweaver.core.model import DATASET, PLATFORM_MODELARTS


@lifecycle(platform=PLATFORM_MODELARTS)
def my_input():
    dataset = input_prepare(DATASET, "")
    print("file path: ", dataset.path)
    input2()


def input2():
    dataset = input_prepare(DATASET, "")
    print("file path2: ", dataset.path)


def test_input():
    my_input()

