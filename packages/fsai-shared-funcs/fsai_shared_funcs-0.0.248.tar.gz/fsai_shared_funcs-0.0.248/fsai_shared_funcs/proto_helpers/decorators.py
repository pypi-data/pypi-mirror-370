from fsai_shared_funcs.proto_helpers.json_format import MessageToDict


class ProtoToDict(object):
    def __init__(
        self,
    ):
        pass

    def __call__(self, f):
        async def wrapped_function(slf, request, context):
            request_as_dict = MessageToDict(
                request,
                including_default_value_fields=True,
                preserving_proto_field_name=True,
                float_precision=14,
            )

            result = f(slf, request_as_dict, context)  # Invoke the decorated function

            return await result

        return wrapped_function


class ProtoToDictAsyncGenerator(object):
    def __init__(
        self,
    ):
        pass

    def __call__(self, f):
        async def wrapped_function(slf, request, context):
            request_as_dict = MessageToDict(
                request,
                including_default_value_fields=True,
                preserving_proto_field_name=True,
                float_precision=14,
            )

            # return await f(slf, request_as_dict, context)
            result = f(slf, request_as_dict, context)  # Invoke the decorated function

            if hasattr(
                result, "__aiter__"
            ):  # Check if result is an async iterator (yields)
                async for item in result:
                    yield item
            else:  # Result is not an async iterator, assumes it returns a value
                raise Exception(
                    "ProtoToDictAsyncGenerator should only be used on functions that return an async iterator"
                )

        return wrapped_function
