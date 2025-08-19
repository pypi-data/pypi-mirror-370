from jcweaver.api.decorators import register_task, input_data, output_data


@register_task(alias="add", tags=["math", "basic"])
@input_data({"a": int, "b": int})
@output_data("json")
def add_task(inputs):
    return {"result": inputs["a"] + inputs["b"]}


def test_decorator():
    result = add_task({"a": 1, "b": 2})
    print(result)
