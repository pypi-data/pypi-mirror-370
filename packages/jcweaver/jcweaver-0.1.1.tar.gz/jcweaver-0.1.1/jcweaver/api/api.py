from jcweaver.adapter import get_adapter
from jcweaver.core.context import get_platform
from jcweaver.core.logger import logger
from jcweaver.core.model import InputContext, OutputContext


def input_prepare(data_type: str, file_path: str):
    platform = get_platform()
    adapter = get_adapter(platform)
    if not adapter:
        logger.error("No adapter found for platform: {}".format(platform))
        raise Exception("No adapter found for platform: {}".format(platform))

    try:
        path = adapter.input_prepare(data_type, file_path)
    except Exception as e:
        logger.error("Error in before_task: {}".format(e))
        raise

    context = InputContext(adapter, path)

    return context


def output_prepare(data_type: str, file_path: str):
    platform = get_platform()
    adapter = get_adapter(platform)
    if not adapter:
        logger.error("No adapter found for platform: {}".format(platform))
        raise Exception("No adapter found for platform: {}".format(platform))

    try:
        path = adapter.output_prepare(data_type, file_path)
    except Exception as e:
        logger.error("Error in before_task: {}".format(e))
        raise
    context = OutputContext(adapter, path)
    logger.info("Output path: {}".format(context.path))
    return context
