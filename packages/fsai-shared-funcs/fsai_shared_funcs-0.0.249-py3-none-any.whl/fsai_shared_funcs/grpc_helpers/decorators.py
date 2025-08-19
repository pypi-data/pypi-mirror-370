import grpc
from loguru import logger
from marshmallow import EXCLUDE
from pydash import get


class CheckUserIdentity(object):
    def __init__(
        self,
        empty_response_cls,
        grpc_details="Missing or invalid user identity metadata.",
        grpc_status_code=grpc.StatusCode.UNAUTHENTICATED,
    ):
        self._empty_rsp_cls = empty_response_cls
        self._status = grpc_status_code
        self._details = grpc_details

    def __call__(self, f):
        async def wrapped_function(slf, request, context):
            meta = context.invocation_metadata()
            for item in meta:
                if item[0] == "x-user-identity" and item[1].isnumeric():
                    user = {"id": int(item[1])}
                    try:
                        return await f(slf, request, context, user)
                    except TypeError as e:
                        logger.error(e)
                        context.set_code(grpc.StatusCode.INTERNAL)
                        context.set_details(
                            f"Error: The GRPC api function {f.__name__} requires the third parameter 'user'"
                        )
                        return self._empty_rsp_cls()
                    except Exception as e:
                        raise e
            context.set_code(self._status)
            context.set_details(self._details)
            return self._empty_rsp_cls()

        return wrapped_function


# Create a class that will be used to wrap the request_dict using lodash's get function to access the field values easier
# TODO: Move this to fsai_shared_funcs
class DictGetter:
    def __init__(self, request_dict):
        self.request_dict = request_dict

    def get(self, accessor, default=None):
        return get(self.request_dict, accessor, default)

    # Create a function that plucks keys from the request_dict and rekeys them
    def pluck(self, obj_mapping):
        new_obj = {}

        for key_name, accessor in obj_mapping.items():
            # Id accessor is a list then use the first element as the accessor and the second element as the default value
            if isinstance(accessor, list):
                new_obj[key_name] = get(self.request_dict, accessor[0], accessor[1])
            else:
                new_obj[key_name] = get(self.request_dict, accessor)
        return new_obj


class ValidateRequestSchema:
    def __init__(self, schema_cls, field_name=None):
        self.schema_cls = schema_cls
        self.field_name = field_name

    def __call__(self, f):
        async def wrapped_function(slf, request_dict, context):
            if self.field_name is not None:
                # Access the field value from the request dictionary
                field_value = get(request_dict, self.field_name)

                # If field_value is None then raise an exception
                if field_value is None:
                    raise ValueError(
                        f"Field '{self.field_name}' is required in the request"
                    )

                # If field_value is not a dict then raise an exception
                if not isinstance(field_value, dict):
                    raise ValueError(
                        f"Field '{self.field_name}' must be a dict. Ensure you call ProtoToDict decorator."
                    )
            else:
                field_value = request_dict

            # Load and validate the field using the schema
            data = self.schema_cls().load(field_value, unknown=EXCLUDE)

            if self.field_name is not None:
                # Update the field value with the validated data
                request_dict[self.field_name] = data
            else:
                # Update the field value with the validated data
                request_dict = data

            # Call the original function with the modified request
            result = f(slf, DictGetter(request_dict), context)

            return await result

        return wrapped_function


class ValidateRequestSchemaGenerator:
    def __init__(self, schema_cls, field_name=None):
        self.schema_cls = schema_cls
        self.field_name = field_name

    def __call__(self, f):
        async def wrapped_function(slf, request_dict, context):
            if self.field_name is not None:
                # Access the field value from the request dictionary
                field_value = get(request_dict, self.field_name)

                # If field_value is None then raise an exception
                if field_value is None:
                    raise ValueError(
                        f"Field '{self.field_name}' is required in the request"
                    )

                # If field_value is not a dict then raise an exception
                if not isinstance(field_value, dict):
                    raise ValueError(
                        f"Field '{self.field_name}' must be a dict. Ensure you call ProtoToDict decorator."
                    )
            else:
                field_value = request_dict

            # Load and validate the field using the schema
            data = self.schema_cls().load(field_value, unknown=EXCLUDE)

            if self.field_name is not None:
                # Update the field value with the validated data
                request_dict[self.field_name] = data
            else:
                # Update the field value with the validated data
                request_dict = data

            # Call the original function with the modified request
            result = f(slf, DictGetter(request_dict), context)

            if hasattr(
                result, "__aiter__"
            ):  # Check if result is an async iterator (yields)
                async for item in result:
                    yield item
            else:  # Result is not an async iterator, assumes it returns a value
                raise Exception(
                    "ValidateRequestSchemaGenerator should only be used on functions that return an async iterator"
                )

        return wrapped_function
