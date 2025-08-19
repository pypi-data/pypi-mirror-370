import functools
from typing import Callable

from jcweaver.adapter import get_adapter
from jcweaver.core.context import get_platform, set_forced_platform
from jcweaver.core.registry import TaskRegistry

registry = TaskRegistry()


def lifecycle(platform: str = None):
    """
    生命周期处理装饰器，执行适配器的before_task/after_task
    平台优先级：参数 > 函数_platform属性 > 环境变量
    """

    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            set_forced_platform(platform)
            platform_name = get_platform()
            adapter = get_adapter(platform_name)

            inputs = kwargs.get('inputs') or (args[0] if args else None)
            context = kwargs.get('context') or (args[1] if len(args) > 1 else None)

            context = context or {}
            context.setdefault('adapter', adapter)

            # 执行前置处理
            adapter.before_task(inputs, context)
            try:

                result = fn(*args, **kwargs)
                # 执行后置处理
                adapter.after_task(result, context)
                return result
            except Exception as e:
                # 异常处理中执行后置
                adapter.after_task({'error': str(e)}, context)
                raise

        # 继承平台属性
        if hasattr(fn, '_platform'):
            wrapper._platform = fn._platform
        return wrapper

    return decorator


def register_task(alias: str = None, tags: list = None):
    def decorator(fn: Callable):
        fn_name = alias or fn.__name__
        input_schema = getattr(fn, '_input_schema', {})
        output_format = getattr(fn, '_output_format', "json")

        registry.register({
            "name": fn_name,
            "input_schema": input_schema,
            "output_format": output_format,
            "tags": tags or [],
            "fn_ref": fn,
        })
        fn._registered_name = fn_name
        return fn

    return decorator

# def use_adapter(platform: str):
#     def decorator(fn: Callable):
#         @functools.wraps(fn)
#         def wrapper(inputs, context=None):
#             adapter = get_adapter(platform)
#             context = context or {}
#             context['adapter'] = adapter
#             return fn(inputs, context)
#
#         wrapper._platform = platform
#         return wrapper
#
#     return decorator


# def inject_context(resource_fn: Callable = None):
#     """
#     自动注入 context 参数，用于统一日志、模型路径、trace_id 等。
#     可选 resource_fn：返回资源上下文 dict
#     """
#
#     def decorator(fn: Callable):
#         @functools.wraps(fn)
#         def wrapper(inputs, context=None):
#             if context is None:
#                 context = {}
#             if resource_fn:
#                 context.update(resource_fn())
#             return fn(inputs, context)
#
#         return wrapper
#
#     return decorator


# def cloud_task(name: str, schema: Dict[str, Any], output: str = "json", tags=None):
#     return lambda fn: register_task(alias=name, tags=tags)(
#         input_data(schema)(
#             output_data(output)(fn)))
