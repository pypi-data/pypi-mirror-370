from jcweaver.api.api import output_prepare
from jcweaver.api.decorators import lifecycle
from jcweaver.core.model import PLATFORM_MODELARTS, DATASET


@lifecycle(platform=PLATFORM_MODELARTS)
def my_output():
    output_param = output_prepare(DATASET, "output111")
    return output_param


def test_output():
    my_output()
