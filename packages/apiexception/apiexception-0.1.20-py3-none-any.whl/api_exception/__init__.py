from typing import Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from .rfc7807_model import RFC7807ResponseModel
from .enums import ExceptionCode, ExceptionStatus, BaseExceptionCode, ResponseFormat
from .response_model import ResponseModel
from .logger import logger, add_file_handler
from .exception import (
    APIException,
    set_default_http_codes,
    DEFAULT_HTTP_CODES,
    set_global_log,
)
from .response_utils import APIResponse

__all__ = [
    "DEFAULT_HTTP_CODES",
    "APIException",
    "ExceptionCode",
    "BaseExceptionCode",
    "ExceptionStatus",
    "ResponseModel",
    "ResponseFormat",
    "RFC7807ResponseModel",
    "register_exception_handlers",  # bu fonksiyon aşağıda tanımlı kalıyor
    "set_default_http_codes",
    "logger",
    "add_file_handler",
    "APIResponse",
    "set_global_log",
]


def register_exception_handlers(app: FastAPI,
                                response_format: ResponseFormat = ResponseFormat.RESPONSE_MODEL,
                                use_fallback_middleware: bool = True,
                                log: bool = True,
                                log_traceback: bool = True,
                                log_traceback_unhandled_exception: bool = True,
                                include_null_data_field_in_openapi: bool = True):
    """
    Attach APIException and fallback handlers to a FastAPI app.

    This ensures that any raised APIException will return a standardized response.
    Optionally, a fallback middleware can catch unhandled exceptions and return
    a consistent error structure.

    Also, it can log the exception details, including the traceback,
    request path, method, and client IP address, exception, exception args and so on.
    This is useful for debugging and monitoring purposes.
    By default, it automatically logs everything related to the exception described above.


    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance.
    response_format : ResponseFormat, default=ResponseFormat.RESPONSE_MODEL
        If ResponseFormat.RESPONSE_MODEL, Return error responses using the standard internal response model.
        If ResponseFormat.RFC7807, Return error responses using the RFC 7807 (Problem Details for HTTP APIs) format.
        If ResponseFormat.RESPONSE_DICTIONARY, returns plain dictionaries.
    use_fallback_middleware : bool, default=True
        If True, catches ALL unhandled exceptions (runtime errors, etc.) and logs them.
    log : bool, default=True
        If False, disables **all logging** (including APIException logs and unhandled exceptions).
        Overrides `log_exception` flags inside APIException. Useful for production environments
        where you want standardized responses but no logging output.
    log_traceback : bool, default=True
        If True, logs traceback for APIException errors.
    log_traceback_unhandled_exception : bool, default=True
        If True, logs traceback for unhandled runtime exceptions.
    include_null_data_field_in_openapi : bool, default=True
        If True, this flag ensures that OpenAPI (Swagger) documentation includes `null` as a valid value for nullable fields in response schemas.
    Examples
    --------
    **1️⃣ Basic usage (default setup):**
    ```python
    from fastapi import FastAPI
    from api_exception import register_exception_handlers

    app = FastAPI()
    register_exception_handlers(app)
    ```

    **2️⃣ Production setup – log to file, disable traceback for handled exceptions (but keep for crashes):**
    ```python
    from fastapi import FastAPI
    from api_exception import register_exception_handlers, add_file_handler, logger

    app = FastAPI()

    # Log to a file for production monitoring
    add_file_handler("prod_errors.log")

    # Only log tracebacks for unhandled runtime errors (not for expected APIExceptions)
    register_exception_handlers(
        app,
        log_traceback=False,
        log_traceback_unhandled_exception=True
    )

    # Increase verbosity for debugging
    logger.setLevel("DEBUG")
    ```

    **3️⃣ Lightweight setup for development – skip fallback middleware and return raw dicts (not ResponseModel):**
    ```python
    from fastapi import FastAPI
    from api_exception import register_exception_handlers

    app = FastAPI()

    register_exception_handlers(
        app,
        use_fallback_middleware=False,   # Let FastAPI's default error pages handle unhandled exceptions
        log=False,
        response_format=ResponseFormat.RESPONSE_DICTIONARY         # Return plain dict responses for speed
    )
    ```

    **4️⃣ Full control setup – log to both console and file, tweak everything:**
    ```python
    from fastapi import FastAPI
    from api_exception import register_exception_handlers, add_file_handler, logger

    app = FastAPI()

    # Log to console (default) and also to file
    add_file_handler("detailed_logs.log")

    # Register with all customizations
    register_exception_handlers(
        app,
        response_format=ResponseFormat.RESPONSE_MODEL,
        use_fallback_middleware=True,
        log=True,
        log_traceback=True,
        log_traceback_unhandled_exception=False,  # Don't log tracebacks for runtime errors and/or
                                                 #  any uncaught errors(db error, 3rd party etc.) (just the message)
        include_null_data_field_in_openapi=False, # Don't show null variables in OpenAPI(Swagger)
    )

    # Set logger level to WARNING for cleaner production logs
    logger.setLevel("WARNING")

    ...

    # Example usage
	@app.get(
    "/example",
    response_model=ResponseModel[UserResponse],
    responses=APIResponse.custom(
        (401, CustomExceptionCode.INVALID_API_KEY),
        (403, CustomExceptionCode.PERMISSION_DENIED),
        (422, CustomExceptionCode.VALIDATION_ERROR)
    ),
)
async def user_basic():
    is_not_allowed = True
    if is_not_allowed:
        raise APIException(
            error_code=CustomExceptionCode.PERMISSION_DENIED,
            http_status_code=403,
        )
    data = UserResponse(id=1, username="Kutay")
    return ResponseModel[UserResponse](
        data=data,
        description="User retrieved successfully."
    )
    ```

    **5️⃣  RFC7807 setup – enable RFC7807-compliant error responses :**
    ```python
    from fastapi import FastAPI
    from api_exception import register_exception_handlers, add_file_handler, logger

    app = FastAPI()

    # Log to console (default) and also to file
    add_file_handler("detailed_logs.log")

    # Register with all customizations
    register_exception_handlers(
        app,
        response_format=ResponseFormat.RFC7807,
        use_fallback_middleware=True,
        log_traceback=True,
        log_traceback_unhandled_exception=False,  # Don't log tracebacks for runtime errors and/or
                                                 #  any uncaught errors(db error, 3rd party etc.) (just the message)
        include_null_data_field_in_openapi=False, # Don't show null variables in OpenAPI(Swagger)
    )

    # Set logger level to WARNING for cleaner production logs
    logger.setLevel("WARNING")

    ...

    # Example usage
    @app.get(
    "/rfc7807",
    response_model=ResponseModel[UserResponse],
    responses=APIResponse.rfc7807(
        (401, CustomExceptionCode.INVALID_API_KEY, "https://example.com/errors/unauthorized", "/account/info"),
        (403, CustomExceptionCode.PERMISSION_DENIED, "https://example.com/errors/forbidden", "/admin/panel"),
        (422, CustomExceptionCode.VALIDATION_ERROR, "https://example.com/errors/unprocessable-entity", "/users/create")
    ))
def rfc7807():
    raise APIException(
        error_code=CustomExceptionCode.PERMISSION_DENIED,
        http_status_code=403,
    )
    ```
    """
    set_global_log(log)

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        if log:
            logger.error(f"Exception handled for path: {request.url.path}")
            logger.error(f"Method: {request.method}")
            logger.error(f"Client IP: {request.client.host if request.client else 'unknown'}")
            if log_traceback:
                tb = traceback.format_exc()
                logger.error(f"Traceback:\n{tb}")

        if response_format == ResponseFormat.RESPONSE_MODEL:
            content = exc.to_response_model().model_dump(exclude_none=False)
            media_type = "application/json"
        elif response_format == ResponseFormat.RFC7807:
            content = exc.to_rfc7807_response().model_dump(exclude_none=False)
            media_type = "application/problem+json"
        else:
            content = exc.to_response()
            media_type = "application/json"

        return JSONResponse(
            status_code=exc.http_status_code,
            content=content,
            media_type=media_type
        )

    if use_fallback_middleware:

        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            try:
                first_err = exc.errors()[0]
                msg = first_err.get("msg", "Validation error")
            except Exception:
                msg = "Validation error"

            # Mesajı enum'un description'ına gömelim ama "first error message" bilgisini de koruyalım
            err = ExceptionCode.VALIDATION_ERROR
            description = msg if msg else err.description

            if response_format == ResponseFormat.RFC7807:
                content = RFC7807ResponseModel(
                    title=err.message,
                    status=HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=description,
                    type=err.rfc7807_type,
                    instance=err.rfc7807_instance,
                ).model_dump(exclude_none=False)
                media_type = "application/problem+json"
            elif response_format == ResponseFormat.RESPONSE_MODEL:
                content = ResponseModel(
                    data=None,
                    status=ExceptionStatus.FAIL,
                    message=err.message,
                    error_code=err.error_code,
                    description=description,
                ).model_dump(exclude_none=False)
                media_type = "application/json"
            else:
                content = {
                    "data": None,
                    "status": ExceptionStatus.FAIL.value,
                    "message": err.message,
                    "error_code": err.error_code,
                    "description": description,
                }
                media_type = "application/json"

            return JSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content=content,
                media_type=media_type,
            )

        @app.middleware("http")
        async def fallback_exception_middleware(request: Request, call_next: Callable):
            try:
                return await call_next(request)
            except Exception as e:
                if log:
                    tb = traceback.format_exc()
                    logger.error("⚡ Unhandled Exception Fallback ⚡")
                    logger.error(f"📌 Path: {request.url.path}")
                    logger.error(f"📌 Method: {request.method}")
                    logger.error(f"📌 Client IP: {request.client.host if request.client else 'unknown'}")
                    logger.error(f"📌 Exception Args: {e.args}")
                    logger.error(f"📌 Exception: {str(e)}")
                    if log_traceback_unhandled_exception:
                        logger.error(f"📌 Traceback:\n{tb}")

                err = ExceptionCode.INTERNAL_SERVER_ERROR

                if response_format == ResponseFormat.RFC7807:
                    content = RFC7807ResponseModel(
                        title=err.message,
                        status=500,
                        detail=err.description,
                        type=err.rfc7807_type,
                        instance=err.rfc7807_instance,
                    ).model_dump(exclude_none=False)
                    media_type = "application/problem+json"
                elif response_format == ResponseFormat.RESPONSE_MODEL:
                    content = ResponseModel(
                        data=None,
                        status=ExceptionStatus.FAIL,
                        message=err.message,
                        error_code=err.error_code,
                        description=err.description,
                    ).model_dump(exclude_none=False)
                    media_type = "application/json"
                else:
                    content = {
                        "data": None,
                        "status": ExceptionStatus.FAIL.value,
                        "message": err.message,
                        "error_code": err.error_code,
                        "description": err.description,
                    }
                    media_type = "application/json"

                return JSONResponse(status_code=500, content=content, media_type=media_type)


    if include_null_data_field_in_openapi:
        """
        Custom OpenAPI schema generator that injects `data: null` into example error responses
        to ensure consistent response shape across all status codes.

        When `openapi_show_null_in_responses` is enabled, this function checks all non-200 
        responses in the OpenAPI schema. If the example response includes the standard 
        error fields (`status`, `message`, `description`, `error_code`) but lacks `data`,
        it injects `"data": null` into the example.

        This helps maintain compatibility with clients that expect a fixed response schema,
        especially when using typed SDKs or schema validators.

        The modified schema is cached in `app.openapi_schema` to prevent regeneration.
        """

        def openapi():
            # If the OpenAPI schema has not yet been generated
            if not app.openapi_schema:
                # Call the original OpenAPI generator
                schema = app.openapi_super()
                paths = schema.get("paths")
                # Iterate through all defined paths in the schema
                for path_k, path_v in paths.items():
                    # Iterate through all HTTP methods (get, post, etc.) for each path
                    for method_k, method_v in path_v.items():
                        if "responses" in method_v:
                            # Iterate through all response codes for this method
                            for response_k, response_v in method_v['responses'].items():
                                if response_k == '200':
                                    # Skip 200 OK responses — we only care about errors
                                    continue
                                if 'content' in response_v:
                                    # Iterate through different media types (e.g., application/json)
                                    for content_k, content_v in response_v['content'].items():
                                        if 'example' in content_v:
                                            example = content_v['example']
                                            # If this is an error response missing the 'data' field,
                                            # inject `"data": null` to ensure schema consistency
                                            if 'status' in example and 'message' in example and 'description' in example and 'error_code' in example and 'data' not in example:
                                                example['data'] = None
                # Cache the modified schema
                app.openapi_schema = schema
            return app.openapi_schema

        # Save the original OpenAPI generator
        app.openapi_super = app.openapi

        # Override FastAPI’s OpenAPI generator with the patched version
        app.openapi = openapi
