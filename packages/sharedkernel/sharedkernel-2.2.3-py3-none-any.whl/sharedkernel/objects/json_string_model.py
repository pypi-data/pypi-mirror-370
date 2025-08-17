import json
from typing import Any
from pydantic import BaseModel, model_validator


class JsonStringModel(BaseModel):
    """`BaseModel` subclass used to validate objects passed to API as JSON strings.

    The primary use case is treating one of the form fields as JSON payload. We need to do that
    in case of endpoints that accept both file and rich set of input parameters. We cannot receive
    both file and JSON body because they use conflicting Content-Type header. It is
    "multipart/form-data" for the former and "application/json" for the latter. If we require
    a client to send a file, we have to use the data sent in form for input parameters.

    Theoretically we could use several form fields to gather all the required input parameters.
    However, some of them are nested in their nature and forms don't support that. That's why we
    consider it better to just use one form field and process its content as JSON payload.

    If a form field model inherits from this class, we will get API documentation and input
    validation - just the way we get it for JSON body defined with `BaseModel`.
    """
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value: Any) -> Any:
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value