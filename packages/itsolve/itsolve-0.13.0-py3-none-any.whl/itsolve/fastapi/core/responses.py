from itsolve.fastapi.core.exceptions import GlobalAppError


def generate_error_response(
    exception_class: type[GlobalAppError],
) -> dict:
    """
    Generates standard error format for OpenAPI (FastAPI responses).
    :param exception_class: Exception class
    :param status_code: HTTP error code (404, 409, etc.)
    :param ctx: Additional error context (e.g. email, phone_number)
    :return: Dictionary with error descriptions
    """

    error_response = {
        exception_class.STATUS_CODE: {
            "description": exception_class.DESCRIPTION or "Unknown error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": exception_class(
                            ctx=exception_class.CTX_EXAMPLE_STRUCTURE
                        ).detail
                    }
                }
            },
        }
    }

    return error_response
