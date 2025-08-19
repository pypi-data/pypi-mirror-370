import os
import json
import time
import uuid
import asyncio
import inspect
import logging
import traceback
from abc import abstractmethod
from enum import Enum
from typing import Any, Set, Union, Callable, Optional, Sequence, TypedDict
from datetime import datetime, timezone
from dataclasses import dataclass

import nest_asyncio  # type: ignore
from wrapt import ObjectProxy  # type: ignore

from payi import Payi, AsyncPayi, APIStatusError, APIConnectionError, __version__ as _payi_version
from payi.types import IngestUnitsParams
from payi.lib.helpers import PayiHeaderNames
from payi.types.shared import XproxyResult
from payi.types.ingest_response import IngestResponse
from payi.types.ingest_units_params import Units, ProviderResponseFunctionCall
from payi.types.shared.xproxy_error import XproxyError
from payi.types.pay_i_common_models_api_router_header_info_param import PayICommonModelsAPIRouterHeaderInfoParam

from .helpers import PayiCategories
from .Stopwatch import Stopwatch

global _g_logger
_g_logger: logging.Logger = logging.getLogger("payi.instrument")

@dataclass
class _ChunkResult:
    send_chunk_to_caller: bool
    ingest: bool = False
    
class _ProviderRequest:
    def __init__(
            self, 
            instrumentor: '_PayiInstrumentor',
            category: str,
            streaming_type: '_StreamingType',
            module_name: str,
            module_version: str,
            is_aws_client: Optional[bool] = None,
            is_google_vertex_or_genai_client: Optional[bool] = None,
            ) -> None:
        self._instrumentor: '_PayiInstrumentor' = instrumentor
        self._module_name: str = module_name
        self._module_version: str = module_version  
        self._estimated_prompt_tokens: Optional[int] = None
        self._category: str = category
        self._ingest: IngestUnitsParams = { "category": category, "units": {} } # type: ignore
        self._streaming_type: '_StreamingType' = streaming_type
        self._is_aws_client: Optional[bool] = is_aws_client
        self._is_google_vertex_or_genai_client: Optional[bool] = is_google_vertex_or_genai_client
        self._function_call_builder: Optional[dict[int, ProviderResponseFunctionCall]] = None
        self._building_function_response: bool = False
        self._function_calls: Optional[list[ProviderResponseFunctionCall]] = None
        self._is_large_context: bool = False

    def process_chunk(self, _chunk: Any) -> _ChunkResult:
        return _ChunkResult(send_chunk_to_caller=True)

    def process_synchronous_response(self, response: Any, log_prompt_and_response: bool, kwargs: Any) -> Optional[object]:  # noqa: ARG002
        return None
    
    @abstractmethod
    def process_request(self, instance: Any, extra_headers: 'dict[str, str]', args: Sequence[Any], kwargs: Any) -> bool:
        ...
    
    def process_request_prompt(self, prompt: 'dict[str, Any]', args: Sequence[Any], kwargs: 'dict[str, Any]') -> None:
        ...
    
    def process_initial_stream_response(self, response: Any) -> None:
        pass

    def remove_inline_data(self, prompt: 'dict[str, Any]') -> bool:# noqa: ARG002
        return False

    @property
    def is_aws_client(self) -> bool:
        return self._is_aws_client if self._is_aws_client is not None else False

    @property
    def is_google_vertex_or_genai_client(self) -> bool:
        return self._is_google_vertex_or_genai_client if self._is_google_vertex_or_genai_client is not None else False

    def process_exception(self, exception: Exception, kwargs: Any, ) -> bool: # noqa: ARG002
        self.exception_to_semantic_failure(exception)
        return True
    
    @property
    def supports_extra_headers(self) -> bool:
        return not self.is_aws_client and not self.is_google_vertex_or_genai_client
    
    @property
    def streaming_type(self) -> '_StreamingType':
        return self._streaming_type

    def exception_to_semantic_failure(self, e: Exception) -> None:
        exception_str = f"{type(e).__name__}"
    
        fields: list[str] = []
    
        for attr in dir(e):
            if not attr.startswith("__"):
                try:
                    value = getattr(e, attr)
                    if value and not inspect.ismethod(value) and not inspect.isfunction(value) and not callable(value):
                        fields.append(f"{attr}={value}")
                except Exception as _ex:
                    pass
 
        existing_properties = self._ingest.get("properties", None)
        if not existing_properties:
            existing_properties = {}

        existing_properties['system.failure'] = exception_str
        if fields:
            failure_description = ",".join(fields)
            existing_properties["system.failure.description"] = failure_description[:128]

        self._ingest["properties"] = existing_properties

        if "http_status_code" not in self._ingest:
            # use a non existent http status code so when presented to the user, the origin is clear
            self._ingest["http_status_code"] = 299

    def add_streaming_function_call(self, index: int, name: Optional[str], arguments: Optional[str]) -> None:
        if not self._function_call_builder:
            self._function_call_builder = {}

        if not index in self._function_call_builder:
            self._function_call_builder[index] = ProviderResponseFunctionCall(name=name or "", arguments=arguments or "")
        else:
            function = self._function_call_builder[index]
            if name:
                function["name"] = function["name"] + name
            if arguments:
                function["arguments"] = (function.get("arguments", "") or "") + arguments

    def add_synchronous_function_call(self, name: str, arguments: Optional[str]) -> None:
        if not self._function_calls:
            self._function_calls = []
            self._ingest["provider_response_function_calls"] = self._function_calls
        self._function_calls.append(ProviderResponseFunctionCall(name=name, arguments=arguments))

class PayiInstrumentConfig(TypedDict, total=False):
    proxy: bool
    global_instrumentation: bool
    instrument_inline_data: bool
    connection_error_logging_window: int
    limit_ids: Optional["list[str]"]
    use_case_name: Optional[str]
    use_case_id: Optional[str]
    use_case_version: Optional[int]
    use_case_properties: Optional["dict[str, str]"]
    user_id: Optional[str]
    account_name: Optional[str]
    request_tags: Optional["list[str]"]
    request_properties: Optional["dict[str, str]"]

class PayiContext(TypedDict, total=False):
    use_case_name: Optional[str]
    use_case_id: Optional[str]
    use_case_version: Optional[int]
    use_case_step: Optional[str]
    use_case_properties: Optional["dict[str, str]"]
    limit_ids: Optional['list[str]']
    user_id: Optional[str]
    account_name: Optional[str]
    request_tags: Optional["list[str]"]
    request_properties: Optional["dict[str, str]"]
    price_as_category: Optional[str]
    price_as_resource: Optional[str]
    resource_scope: Optional[str]
    last_result: Optional[Union[XproxyResult, XproxyError]]

class _Context(TypedDict, total=False):
    proxy: Optional[bool]
    use_case_name: Optional[str]
    use_case_id: Optional[str]
    use_case_version: Optional[int]
    use_case_step: Optional[str]
    use_case_properties: Optional["dict[str, str]"]
    limit_ids: Optional['list[str]']
    user_id: Optional[str]
    account_name: Optional[str]
    request_tags: Optional["list[str]"]
    request_properties: Optional["dict[str, str]"]
    price_as_category: Optional[str]
    price_as_resource: Optional[str]
    resource_scope: Optional[str]

class _IsStreaming(Enum):
    false = 0
    true = 1 
    kwargs = 2

class _StreamingType(Enum):
    generator = 0
    iterator = 1
    stream_manager = 2

class _InternalTrackContext:
    def __init__(
        self,
        context: _Context,
    ) -> None:
        self._context = context

    def __enter__(self) -> Any:
        if not _instrumentor:
            return self
        
        _instrumentor.__enter__()
        _instrumentor._init_current_context(**self._context)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if _instrumentor:
            _instrumentor.__exit__(exc_type, exc_val, exc_tb)

class _PayiInstrumentor:
    _not_instrumented: str = "<not_instrumented>"
    _instrumented_module_header_name: str = "xProxy-Instrumented-Module"

    def __init__(
        self,
        payi: Optional[Payi],
        apayi: Optional[AsyncPayi],
        instruments: Union[Set[str], None] = None,
        log_prompt_and_response: bool = True,
        logger: Optional[logging.Logger] = None,
        prompt_and_response_logger: Optional[
            Callable[[str, "dict[str, str]"], None]
        ] = None,  # (request id, dict of data to store) -> None
        global_config: PayiInstrumentConfig = {},
        caller_filename: str = ""
    ):
        global _g_logger
        self._logger: logging.Logger = logger if logger else _g_logger

        self._logger.info(f"Pay-i instrumentor version: {_payi_version}")

        self._payi: Optional[Payi] = payi
        self._apayi: Optional[AsyncPayi] = apayi

        if self._payi:
            _g_logger.debug(f"Pay-i instrumentor initialized with Payi instance: {self._payi}")
        if self._apayi:
            _g_logger.debug(f"Pay-i instrumentor initialized with AsyncPayi instance: {self._apayi}")            

        self._context_stack: list[_Context] = []  # Stack of context dictionaries
        self._log_prompt_and_response: bool = log_prompt_and_response
        self._prompt_and_response_logger: Optional[Callable[[str, dict[str, str]], None]] = prompt_and_response_logger

        self._blocked_limits: set[str] = set()
        self._exceeded_limits: set[str] = set()

        self._api_connection_error_last_log_time: float = time.time()
        self._api_connection_error_count: int = 0
        self._api_connection_error_window: int = global_config.get("connection_error_logging_window", 60)
        if self._api_connection_error_window < 0:
            raise ValueError("connection_error_logging_window must be a non-negative integer")

        # default is instrument and ingest metrics
        self._proxy_default: bool = global_config.get("proxy", False)

        self._instrument_inline_data: bool = global_config.get("instrument_inline_data", False)

        self._last_result: Optional[Union[XproxyResult, XproxyError]] = None

        global_instrumentation = global_config.pop("global_instrumentation", True)

        if instruments is None or "*" in instruments:
            self._instrument_all()
        else:
            self._instrument_specific(instruments)

        if global_instrumentation:
            if "proxy" not in global_config:
                global_config["proxy"] = self._proxy_default

            # Use default clients if not provided for global ingest instrumentation
            if not self._payi and not self._apayi:
                self._payi = Payi()
                self._apayi = AsyncPayi()

            if "use_case_name" not in global_config and caller_filename:
                description = f"Default use case for {caller_filename}.py"
                try:
                    if self._payi:
                        self._payi.use_cases.definitions.create(name=caller_filename, description=description)
                    elif self._apayi:
                        self._call_async_use_case_definition_create(use_case_name=caller_filename, use_case_description=description)
                    global_config["use_case_name"] = caller_filename
                except Exception as e:
                    self._logger.error(f"Error creating default use case definition based on file name {caller_filename}: {e}")

            self.__enter__()

            # _init_current_context will update the currrent context stack location
            context: _Context = {}
            # Copy allowed keys from global_config into context
            # Dynamically use keys from _Context TypedDict
            context_keys = list(_Context.__annotations__.keys()) if hasattr(_Context, '__annotations__') else []
            for key in context_keys:
                if key in global_config:
                    context[key] = global_config[key] # type: ignore

            self._init_current_context(**context) 

    def _instrument_all(self) -> None:
        self._instrument_openai()
        self._instrument_anthropic()
        self._instrument_aws_bedrock()
        self._instrument_google_vertex()
        self._instrument_google_genai()

    def _instrument_specific(self, instruments: Set[str]) -> None:
        if PayiCategories.openai in instruments or PayiCategories.azure_openai in instruments:
            self._instrument_openai()
        if PayiCategories.anthropic in instruments:
            self._instrument_anthropic()
        if PayiCategories.aws_bedrock in instruments:
            self._instrument_aws_bedrock()
        if PayiCategories.google_vertex in instruments:
            self._instrument_google_vertex()
            self._instrument_google_genai()

    def _instrument_openai(self) -> None:
        from .OpenAIInstrumentor import OpenAiInstrumentor

        try:
            OpenAiInstrumentor.instrument(self)

        except Exception as e:
            self._logger.error(f"Error instrumenting OpenAI: {e}")

    def _instrument_anthropic(self) -> None:
        from .AnthropicInstrumentor import AnthropicInstrumentor

        try:
            AnthropicInstrumentor.instrument(self)

        except Exception as e:
            self._logger.error(f"Error instrumenting Anthropic: {e}")

    def _instrument_aws_bedrock(self) -> None:
        from .BedrockInstrumentor import BedrockInstrumentor

        try:
            BedrockInstrumentor.instrument(self)

        except Exception as e:
            self._logger.error(f"Error instrumenting AWS bedrock: {e}")

    def _instrument_google_vertex(self) -> None:
        from .VertexInstrumentor import VertexInstrumentor

        try:
            VertexInstrumentor.instrument(self)

        except Exception as e:
            self._logger.error(f"Error instrumenting Google Vertex: {e}")

    def _instrument_google_genai(self) -> None:
        from .GoogleGenAiInstrumentor import GoogleGenAiInstrumentor

        try:
            GoogleGenAiInstrumentor.instrument(self)

        except Exception as e:
            self._logger.error(f"Error instrumenting Google GenAi: {e}")

    @staticmethod
    def _create_logged_ingest_units(
        ingest_units: IngestUnitsParams,
    ) -> IngestUnitsParams:
        # remove large and potentially sensitive data from the log
        log_ingest_units: IngestUnitsParams = ingest_units.copy()
        
        log_ingest_units.pop('provider_request_json', None)
        log_ingest_units.pop('provider_response_json', None)

        # Pop system.stack_trace from properties if it exists
        if 'properties' in log_ingest_units and isinstance(log_ingest_units['properties'], dict):
            log_ingest_units['properties'].pop('system.stack_trace', None)

        return log_ingest_units
        
    def _process_ingest_units(
            self,
            request: _ProviderRequest, log_data: 'dict[str, str]',
            extra_headers: 'dict[str, str]') -> None:
        ingest_units = request._ingest

        if request._module_version:
            extra_headers[_PayiInstrumentor._instrumented_module_header_name] = f'{request._module_name}/{request._module_version}'

        if request._function_call_builder:
            # convert the function call builder to a list of function calls
            ingest_units["provider_response_function_calls"] = list(request._function_call_builder.values())

        if 'resource' not in ingest_units or ingest_units['resource'] == '':
            ingest_units['resource'] = "system.unknown_model"

        request_json = ingest_units.get('provider_request_json', "")
        if request_json and self._instrument_inline_data is False:
            try:
                prompt_dict = json.loads(request_json)
                if request.remove_inline_data(prompt_dict):
                    self._logger.debug(f"Removed inline data from provider_request_json")
                    # store the modified dict back as JSON string
                    ingest_units['provider_request_json'] = json.dumps(prompt_dict)

            except Exception as e:
                self._logger.error(f"Error serializing provider_request_json: {e}")

        if int(ingest_units.get("http_status_code") or 0) < 400:
            units = ingest_units.get("units", {})
            if not units or all(unit.get("input", 0) == 0 and unit.get("output", 0) == 0 for unit in units.values()):
                self._logger.info('ingesting with no token counts')

        if self._log_prompt_and_response and self._prompt_and_response_logger:
            response_json = ingest_units.pop("provider_response_json", None)
            request_json = ingest_units.pop("provider_request_json", None)
            stack_trace = ingest_units.get("properties", {}).pop("system.stack_trace", None)  # type: ignore

            if response_json is not None:
                # response_json is a list of strings, convert a single json string
                log_data["provider_response_json"] = json.dumps(response_json)
            if request_json is not None:
                log_data["provider_request_json"] = request_json
            if stack_trace is not None:
                log_data["stack_trace"] = stack_trace

    def _process_ingest_units_response(self, ingest_response: IngestResponse) -> None:
        if ingest_response.xproxy_result.limits:
            for limit_id, state in ingest_response.xproxy_result.limits.items():
                removeBlockedId: bool = False

                if state.state == "blocked":
                    self._blocked_limits.add(limit_id)
                elif state.state == "exceeded":
                    self._exceeded_limits.add(limit_id)
                    removeBlockedId = True
                elif state.state == "ok":
                    removeBlockedId = True

                # opportunistically remove blocked limits
                if removeBlockedId:
                    self._blocked_limits.discard(limit_id)

    def _process_ingest_connection_error(self, e: APIConnectionError, ingest_units: IngestUnitsParams) -> XproxyError:
        now = time.time()

        if (now - self._api_connection_error_last_log_time) > self._api_connection_error_window:
            # If previous window had suppressed errors, log the count
            append = ""
            if self._api_connection_error_count > 0:
                append = f", {self._api_connection_error_count} APIConnectionError exceptions in the last {self._api_connection_error_window} seconds"

            # Log the current error
            self._logger.error(f"Error Pay-i ingesting: connection exception {e}, request {ingest_units}{append}")
            self._api_connection_error_last_log_time = now
            self._api_connection_error_count = 0
        else:
            # Suppress and count
            self._api_connection_error_count += 1

        return XproxyError(code="api_connection_error", message=str(e))

    async def _aingest_units_worker(self, request: _ProviderRequest) -> Optional[Union[XproxyResult, XproxyError]]:
        ingest_response: Optional[IngestResponse] = None
        ingest_units = request._ingest

        self._logger.debug(f"_aingest_units")

        # return early if there are no units to ingest and on a successul ingest request
        log_data: 'dict[str,str]' = {}
        extra_headers: 'dict[str, str]' = {}

        self._process_ingest_units(request, log_data=log_data, extra_headers=extra_headers)

        try:
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug(f"_aingest_units: sending ({self._create_logged_ingest_units(ingest_units)})")

            if self._apayi:    
                ingest_response = await self._apayi.ingest.units(**ingest_units, extra_headers=extra_headers)
            elif self._payi:
                ingest_response = self._payi.ingest.units(**ingest_units, extra_headers=extra_headers)
            else:
                self._logger.error("No payi instance to ingest units")
                return XproxyError(code="configuration_error", message="No Payi or AsyncPayi instance configured for ingesting units")

            self._logger.debug(f"_aingest_units: success ({ingest_response})")

            if ingest_response:
                self._process_ingest_units_response(ingest_response)

                if ingest_response and self._log_prompt_and_response and self._prompt_and_response_logger:
                    request_id = ingest_response.xproxy_result.request_id
                    self._prompt_and_response_logger(request_id, log_data)  # type: ignore

            return ingest_response.xproxy_result

        except APIConnectionError as api_ex:
            return self._process_ingest_connection_error(api_ex, ingest_units)

        except APIStatusError as api_status_ex:
            return self._process_api_status_error(api_status_ex)      

        except Exception as ex:
            self._logger.error(f"Error Pay-i async ingesting: exception {ex}, request {ingest_units}")
            return XproxyError(code="unknown_error", message=str(ex))
    
    async def _aingest_units(self, request: _ProviderRequest) -> Optional[Union[XproxyResult, XproxyError]]:
        return self.set_xproxy_result(await self._aingest_units_worker(request))

    def _call_async_use_case_definition_create(self, use_case_name: str, use_case_description: str) -> None:
        if not self._apayi:
            return

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        try:
            if loop and loop.is_running():
                nest_asyncio.apply(loop) # type: ignore
                asyncio.run(self._apayi.use_cases.definitions.create(name=use_case_name, description=use_case_description))                
            else:
                # When there's no running loop, create a new one
                asyncio.run(self._apayi.use_cases.definitions.create(name=use_case_name, description=use_case_description))
        except Exception as e:
            self._logger.error(f"Error calling async use_cases.definitions.create synchronously: {e}")

    def _call_aingest_sync(self, request: _ProviderRequest) -> Optional[Union[XproxyResult, XproxyError]]:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        try:
            if loop and loop.is_running():
                nest_asyncio.apply(loop) # type: ignore
                return asyncio.run(self._aingest_units(request))
            else:
                # When there's no running loop, create a new one
                return asyncio.run(self._aingest_units(request))
        except Exception as e:
            self._logger.error(f"Error calling aingest_units synchronously: {e}")
        return None
        
    def _process_api_status_error(self, e: APIStatusError) -> Optional[XproxyError]:
        try:
            body_dict: dict[str, Any] = {}

            # Try to get the response body as JSON
            body = e.body
            if body is None:
                self._logger.error("APIStatusError response has no body attribute")
                return XproxyError(code="unknown_error", message=str(e))

            # If body is bytes, decode to string
            if isinstance(body, bytes):
                body = body.decode("utf-8")
            if isinstance(body, dict):
                body_dict = body # type: ignore
            else:
                body = str(body)

            if not body_dict:
                try:
                    body_dict = json.loads(body)  # type: ignore
                except Exception as json_ex:
                    self._logger.error(f"Failed to parse response body as JSON: {json_ex}")
                    return XproxyError(code="invalid_json", message=str(e))

            xproxy_error = body_dict.get("xproxy_error", {})
            code = xproxy_error.get("code", "unknown_error")
            message = xproxy_error.get("message", str(e))
            return XproxyError(code=code, message=message)

        except Exception as ex:
            self._logger.error(f"Exception in _process_api_status_error: {ex}")
            return XproxyError(code="exception", message=str(ex))

    def _ingest_units_worker(self, request: _ProviderRequest) -> Optional[Union[XproxyResult, XproxyError]]:
        ingest_response: Optional[IngestResponse] = None
        ingest_units = request._ingest

        self._logger.debug(f"_ingest_units")

        # return early if there are no units to ingest and on a successul ingest request
        log_data: 'dict[str,str]' = {}
        extra_headers: 'dict[str, str]' = {}
        self._process_ingest_units(request, log_data=log_data, extra_headers=extra_headers)

        try:
            if self._payi:
                if self._logger.isEnabledFor(logging.DEBUG):
                    self._logger.debug(f"_ingest_units: sending ({self._create_logged_ingest_units(ingest_units)})")

                ingest_response = self._payi.ingest.units(**ingest_units, extra_headers=extra_headers)
                self._logger.debug(f"_ingest_units: success ({ingest_response})")

                self._process_ingest_units_response(ingest_response)

                if self._log_prompt_and_response and self._prompt_and_response_logger:
                    request_id = ingest_response.xproxy_result.request_id
                    self._prompt_and_response_logger(request_id, log_data)  # type: ignore

                return ingest_response.xproxy_result
            elif self._apayi:
                # task runs async. aingest_units will invoke the callback and post process
                sync_response = self._call_aingest_sync(request)
                self._logger.debug(f"_ingest_units: apayi success ({sync_response})")
                return sync_response
            else:
                self._logger.error("No payi instance to ingest units")
                return XproxyError(code="configuration_error", message="No Payi or AsyncPayi instance configured for ingesting units")

        except APIConnectionError as api_ex:
            return self._process_ingest_connection_error(api_ex, ingest_units)

        except APIStatusError as api_status_ex:
            return self._process_api_status_error(api_status_ex)      

        except Exception as ex:
            self._logger.error(f"Error Pay-i async ingesting: exception {ex}, request {ingest_units}")
            return XproxyError(code="unknown_error", message=str(ex))
        
    def _ingest_units(self, request: _ProviderRequest) -> Optional[Union[XproxyResult, XproxyError]]:
        return self.set_xproxy_result(self._ingest_units_worker(request))

    def _setup_call_func(
        self
        ) -> _Context:

        if len(self._context_stack) > 0:
            # copy current context into the upcoming context
            return self._context_stack[-1].copy()

        return {}

    def _init_current_context(
        self,
        proxy: Optional[bool] = None,
        limit_ids: Optional["list[str]"] = None,
        use_case_name: Optional[str]= None,
        use_case_id: Optional[str]= None,
        use_case_version: Optional[int]= None,
        use_case_step: Optional[str]= None,
        user_id: Optional[str]= None,
        account_name: Optional[str]= None,
        request_tags: Optional["list[str]"] = None,
        request_properties: Optional["dict[str, str]"] = None,
        use_case_properties: Optional["dict[str, str]"] = None,
        price_as_category: Optional[str] = None,
        price_as_resource: Optional[str] = None,
        resource_scope: Optional[str] = None,
        ) -> None:

        # there will always be a current context
        context: _Context = self.get_context() # type: ignore
        parent_context: _Context = self._context_stack[-2] if len(self._context_stack) > 1 else {}

        parent_proxy = parent_context.get("proxy", self._proxy_default)
        context["proxy"] = proxy if proxy else parent_proxy

        parent_use_case_name = parent_context.get("use_case_name", None)
        parent_use_case_id = parent_context.get("use_case_id", None)
        parent_use_case_version = parent_context.get("use_case_version", None)
        parent_use_case_step = parent_context.get("use_case_step", None)

        assign_use_case_values = False

        if use_case_name is None:
            if parent_use_case_name:
                # If no use_case_name specified, use previous values
                context["use_case_name"] = parent_use_case_name
                assign_use_case_values = True
        elif len(use_case_name) == 0:
            # Empty string explicitly blocks inheriting from the parent state
            context["use_case_name"] = None
            context["use_case_id"] = None
            context["use_case_version"] = None
            context["use_case_step"] = None
            context["use_case_properties"] = None
        else:
            if use_case_name == parent_use_case_name:
                # Same use case name, use previous ID unless new one specified
                context["use_case_name"] = use_case_name
            else:
                context["use_case_name"] = use_case_name

                # Different use case name, use specified ID or generate one. 
                # By assigning to a new value to parent_use_case_id we keep the assignment logic below simple and consistent with
                # assign the caller's use_case_id if specified or the newly generated one. 
                # The use case id stored in the parent context is not mutated.
                parent_use_case_id = str(uuid.uuid4())

            assign_use_case_values = True

        if assign_use_case_values:
            context["use_case_id"] = use_case_id if use_case_id else parent_use_case_id
            context["use_case_version"] = use_case_version if use_case_version else parent_use_case_version
            context["use_case_step"] = use_case_step if use_case_step else parent_use_case_step

            parent_use_case_properties = parent_context.get("use_case_properties", None)
            if use_case_properties is not None:
                if not use_case_properties:
                    # an empty dictionary explicitly blocks inheriting from the parent state
                    context["use_case_properties"] = None
                else:
                    if parent_use_case_properties:
                        # merge dictionaries, child overrides parent keys
                        merged = parent_use_case_properties.copy()
                        merged.update(use_case_properties)
                        context["use_case_properties"] = merged
                    else:
                        context["use_case_properties"] = use_case_properties.copy()
            elif parent_use_case_properties:
                # use the parent use_case_properties if it exists
                context["use_case_properties"] = parent_use_case_properties.copy()

        parent_limit_ids = parent_context.get("limit_ids", None)
        if limit_ids is None:
            # use the parent limit_ids if it exists
            context["limit_ids"] = parent_limit_ids
        elif len(limit_ids) == 0:
            # caller passing an empty array explicitly blocks inheriting from the parent state
            context["limit_ids"] = None
        else:
            # union of new and parent lists if the parent context contains limit ids
            context["limit_ids"] = list(set(limit_ids) | set(parent_limit_ids)) if parent_limit_ids else limit_ids.copy()

        parent_user_id = parent_context.get("user_id", None)
        if user_id is None:
            # use the parent user_id if it exists
            context["user_id"] = parent_user_id
        elif len(user_id) == 0:
            # caller passing an empty string explicitly blocks inheriting from the parent state
            context["user_id"] = None
        else:
            context["user_id"] = user_id

        parent_account_name = parent_context.get("account_name", None)
        if account_name is None:
            # use the parent account_name if it exists
            context["account_name"] = parent_account_name
        elif len(account_name) == 0:
            # caller passing an empty string explicitly blocks inheriting from the parent state
            context["account_name"] = None
        else:
            context["account_name"] = account_name

        parent_request_tags = parent_context.get("request_tags", None)
        if request_tags is not None:
            if len(request_tags) == 0:
                # caller passing an empty list explicitly blocks inheriting from the parent state
                context["request_tags"] = None
            else:
                if parent_request_tags:
                    # union of new and parent lists if the parent context contains request tags
                    context["request_tags"] = list(set(request_tags) | set(parent_request_tags))
                else:
                    context["request_tags"] = request_tags.copy()
        elif parent_request_tags:
            # use the parent request_tags if it exists
            context["request_tags"] = parent_request_tags.copy()

        parent_request_properties = parent_context.get("request_properties", None)
        if request_properties is not None:
            if not request_properties:
                # an empty dictionary explicitly blocks inheriting from the parent state
                context["request_properties"] = None
            else:
                if parent_request_properties:
                    # merge dictionaries, child overrides parent keys
                    merged = parent_request_properties.copy()
                    merged.update(request_properties)
                    context["request_properties"] = merged
                else:
                    context["request_properties"] = request_properties.copy()
        elif parent_request_properties:
            # use the parent request_properties if it exists
            context["request_properties"] = parent_request_properties.copy()

        if price_as_category:
            context["price_as_category"] = price_as_category
        if price_as_resource:
            context["price_as_resource"] = price_as_resource
        if resource_scope:
            context["resource_scope"] = resource_scope
        
    async def _acall_func(
        self,
        func: Any,
        proxy: Optional[bool],
        limit_ids: Optional["list[str]"],
        use_case_name: Optional[str],
        use_case_id: Optional[str],
        use_case_version: Optional[int],        
        user_id: Optional[str],
        account_name: Optional[str],
        request_tags: Optional["list[str]"] = None,
        request_properties: Optional["dict[str, str]"] = None,
        use_case_properties: Optional["dict[str, str]"] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        with self:
            self._init_current_context(
                proxy=proxy,
                limit_ids=limit_ids,
                use_case_name=use_case_name,
                use_case_id=use_case_id,
                use_case_version=use_case_version,
                user_id=user_id,
                account_name=account_name,
                request_tags=request_tags,
                request_properties=request_properties,
                use_case_properties=use_case_properties
            )
            return await func(*args, **kwargs)

    def _call_func(
        self,
        func: Any,
        proxy: Optional[bool],
        limit_ids: Optional["list[str]"],
        use_case_name: Optional[str],
        use_case_id: Optional[str],
        use_case_version: Optional[int],        
        user_id: Optional[str],
        account_name: Optional[str],
        request_tags: Optional["list[str]"] = None,
        request_properties: Optional["dict[str, str]"] = None,
        use_case_properties: Optional["dict[str, str]"] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        with self:
            self._init_current_context(
                proxy=proxy,
                limit_ids=limit_ids,
                use_case_name=use_case_name,
                use_case_id=use_case_id,
                use_case_version=use_case_version,
                user_id=user_id,
                account_name=account_name,
                request_tags=request_tags,
                request_properties=request_properties,
                use_case_properties=use_case_properties)
            return func(*args, **kwargs)

    def __enter__(self) -> Any:
        # Push a new context dictionary onto the stack
        self._context_stack.append({})
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        # Pop the current context off the stack
        if self._context_stack:
            self._context_stack.pop()

    def get_context(self) -> Optional[_Context]:
        # Return the current top of the stack
        return self._context_stack[-1] if self._context_stack else None

    def get_context_safe(self) -> _Context:
        # Return the current top of the stack
        return self.get_context() or {}

    def _prepare_ingest(
        self,
        request: _ProviderRequest,
        context: _Context,
        ingest_extra_headers: "dict[str, str]", # do not conflict with potential kwargs["extra_headers"]
        args: Sequence[Any],
        kwargs: 'dict[str, Any]',
    ) -> None:

        limit_ids = ingest_extra_headers.pop(PayiHeaderNames.limit_ids, None)
        request_tags = ingest_extra_headers.pop(PayiHeaderNames.request_tags, None)

        use_case_name = ingest_extra_headers.pop(PayiHeaderNames.use_case_name, None)
        use_case_id = ingest_extra_headers.pop(PayiHeaderNames.use_case_id, None)
        use_case_version = ingest_extra_headers.pop(PayiHeaderNames.use_case_version, None)
        use_case_step = ingest_extra_headers.pop(PayiHeaderNames.use_case_step, None)

        user_id = ingest_extra_headers.pop(PayiHeaderNames.user_id, None)
        account_name = ingest_extra_headers.pop(PayiHeaderNames.account_name, None)

        if limit_ids:
            request._ingest["limit_ids"] = limit_ids.split(",")
        if request_tags:
            request._ingest["request_tags"] = request_tags.split(",")
        if use_case_name:
            request._ingest["use_case_name"] = use_case_name
        if use_case_id:
            request._ingest["use_case_id"] = use_case_id
        if use_case_version:
            request._ingest["use_case_version"] = int(use_case_version)
        if use_case_step:
            request._ingest["use_case_step"] = use_case_step
        if user_id:
            request._ingest["user_id"] = user_id
        if account_name:
            request._ingest["account_name"] = account_name

        request_properties = context.get("request_properties", None)
        if request_properties:
            request._ingest["properties"] = request_properties

        use_case_properties = context.get("use_case_properties", None)
        if use_case_properties:
            request._ingest["use_case_properties"] = use_case_properties

        if len(ingest_extra_headers) > 0:
            request._ingest["provider_request_headers"] = [PayICommonModelsAPIRouterHeaderInfoParam(name=k, value=v) for k, v in ingest_extra_headers.items()]

        provider_prompt: "dict[str, Any]" = {}
        for k, v in kwargs.items():
            if k == "messages":
                provider_prompt[k] = [m.model_dump() if hasattr(m, "model_dump") else m for m in v]
            elif k in ["extra_headers", "extra_query"]:
                pass
            else:
                try:
                    if hasattr(v, "to_dict"):
                        provider_prompt[k] = v.to_dict()
                    else:
                        json.dumps(v)
                        provider_prompt[k] = v
                except Exception as _e:
                    pass

        request.process_request_prompt(provider_prompt, args, kwargs)

        if self._log_prompt_and_response:
            request._ingest["provider_request_json"] = json.dumps(provider_prompt)

        request._ingest["event_timestamp"] = datetime.now(timezone.utc)
        
    async def async_invoke_wrapper(
        self,
        request: _ProviderRequest,
        is_streaming: _IsStreaming,
        wrapped: Any,
        instance: Any,
        args: Sequence[Any],
        kwargs: 'dict[str, Any]',
    ) -> Any:
        self._logger.debug(f"async_invoke_wrapper: instance {instance}, category {request._category}")

        context = self.get_context()

        # Bedrock client does not have an async method

        if not context:   
            self._logger.debug(f"async_invoke_wrapper: no instrumentation context, exit early")

            # wrapped function invoked outside of decorator scope
            return await wrapped(*args, **kwargs)

        # after _udpate_headers, all metadata to add to ingest is in extra_headers, keyed by the xproxy-xxx header name
        extra_headers: Optional[dict[str, str]] = kwargs.get("extra_headers")
        if extra_headers is None:
            extra_headers = {}
        self._update_extra_headers(context, extra_headers)

        if context.get("proxy", self._proxy_default):
            if "extra_headers" not in kwargs and extra_headers:
                kwargs["extra_headers"] = extra_headers

            self._logger.debug(f"async_invoke_wrapper: sending proxy request")

            return await wrapped(*args, **kwargs)

        current_frame = inspect.currentframe()
        # f_back excludes the current frame, strip() cleans up whitespace and newlines
        stack = [frame.strip() for frame in traceback.format_stack(current_frame.f_back)]  # type: ignore

        request._ingest['properties'] = { 'system.stack_trace': json.dumps(stack) }

        if request.process_request(instance, extra_headers, args, kwargs) is False:
            self._logger.debug(f"async_invoke_wrapper: calling wrapped instance")
            return await wrapped(*args, **kwargs)

        sw = Stopwatch()
        stream: bool = False
        
        if is_streaming == _IsStreaming.kwargs:
            stream = kwargs.get("stream", False)
        elif is_streaming == _IsStreaming.true:
            stream = True
        else:
            stream = False

        try:
            self._prepare_ingest(request, context, extra_headers, args, kwargs)
            self._logger.debug(f"async_invoke_wrapper: calling wrapped instance (stream={stream})")

            sw.start()
            response = await wrapped(*args, **kwargs)

        except Exception as e:  # pylint: disable=broad-except
            sw.stop()
            duration = sw.elapsed_ms_int()

            self._logger.debug(f"invoke_wrapper: calling wrapped instance exception {e}")

            if request.process_exception(e, kwargs):
                request._ingest["end_to_end_latency_ms"] = duration
                await self._aingest_units(request)

            raise e

        if stream:
            if request.streaming_type == _StreamingType.generator:
                return _GeneratorWrapper(
                    generator=response,
                    instance=instance,
                    instrumentor=self,
                    stopwatch=sw,
                    request=request,
                    )
            elif request.streaming_type == _StreamingType.stream_manager:
                return _StreamManagerWrapper(
                    stream_manager=response,
                    instance=instance,
                    instrumentor=self,
                    stopwatch=sw,
                    request=request,
                )
            else:
                return _StreamIteratorWrapper(
                    response=response,
                    instance=instance,
                    instrumentor=self,
                    stopwatch=sw,
                    request=request,
                )

        sw.stop()
        duration = sw.elapsed_ms_int()
        request._ingest["end_to_end_latency_ms"] = duration
        request._ingest["http_status_code"] = 200

        return_result: Any = request.process_synchronous_response(
            response=response,
            log_prompt_and_response=self._log_prompt_and_response,
            kwargs=kwargs)

        if return_result:
            self._logger.debug(f"async_invoke_wrapper: process sync response return")
            return return_result

        await self._aingest_units(request)

        self._logger.debug(f"async_invoke_wrapper: finished")
        return response

    def invoke_wrapper(
        self,
        request: _ProviderRequest,
        is_streaming: _IsStreaming,
        wrapped: Any,
        instance: Any,
        args: Sequence[Any],
        kwargs: 'dict[str, Any]',
    ) -> Any:
        self._logger.debug(f"invoke_wrapper: instance {instance}, category {request._category}")

        context = self.get_context()

        if not context:
            if not request.supports_extra_headers:
                kwargs.pop("extra_headers", None)

            self._logger.debug(f"invoke_wrapper: no instrumentation context, exit early")

            # wrapped function invoked outside of decorator scope
            return wrapped(*args, **kwargs)

        # after _udpate_headers, all metadata to add to ingest is in extra_headers, keyed by the xproxy-xxx header name
        extra_headers: Optional[dict[str, str]] = kwargs.get("extra_headers")
        if extra_headers is None:
            extra_headers = {}
        self._update_extra_headers(context, extra_headers)

        if context.get("proxy", self._proxy_default):
            if not request.supports_extra_headers:
                kwargs.pop("extra_headers", None)
            elif "extra_headers" not in kwargs and extra_headers:
                # assumes anthropic and openai clients
                kwargs["extra_headers"] = extra_headers

            self._logger.debug(f"invoke_wrapper: sending proxy request")

            return wrapped(*args, **kwargs)
        
        current_frame = inspect.currentframe()
        # f_back excludes the current frame, strip() cleans up whitespace and newlines
        stack = [frame.strip() for frame in traceback.format_stack(current_frame.f_back)]  # type: ignore

        request._ingest['properties'] = { 'system.stack_trace': json.dumps(stack) }

        if request.process_request(instance, extra_headers, args, kwargs) is False:
            self._logger.debug(f"invoke_wrapper: calling wrapped instance")
            return wrapped(*args, **kwargs)

        sw = Stopwatch()
        stream: bool = False
        
        if is_streaming == _IsStreaming.kwargs:
            stream = kwargs.get("stream", False)
        elif is_streaming == _IsStreaming.true:
            stream = True
        else:
            stream = False

        try:
            self._prepare_ingest(request, context, extra_headers, args, kwargs)
            self._logger.debug(f"invoke_wrapper: calling wrapped instance (stream={stream})")

            sw.start()
            response = wrapped(*args, **kwargs)
            
        except Exception as e:  # pylint: disable=broad-except
            sw.stop()
            duration = sw.elapsed_ms_int()

            self._logger.debug(f"invoke_wrapper: calling wrapped instance exception {e}")

            if request.process_exception(e, kwargs):
                request._ingest["end_to_end_latency_ms"] = duration
                self._ingest_units(request)

            raise e

        if stream:
            if request.streaming_type == _StreamingType.generator:
                return _GeneratorWrapper(
                    generator=response,
                    instance=instance,
                    instrumentor=self,
                    stopwatch=sw,
                    request=request,
                )
            elif request.streaming_type == _StreamingType.stream_manager:
                return _StreamManagerWrapper(
                    stream_manager=response,
                    instance=instance,
                    instrumentor=self,
                    stopwatch=sw,
                    request=request,
                )
            else:
                # request.streaming_type == _StreamingType.iterator
                stream_result = _StreamIteratorWrapper(
                    response=response,
                    instance=instance,
                    instrumentor=self,
                    stopwatch=sw,
                    request=request,
                )

                if request.is_aws_client:
                    if "body" in response:
                        response["body"] = stream_result
                    else:
                        response["stream"] = stream_result
                    return response
                
                return stream_result

        sw.stop()
        duration = sw.elapsed_ms_int()
        request._ingest["end_to_end_latency_ms"] = duration
        request._ingest["http_status_code"] = 200

        return_result: Any = request.process_synchronous_response(
            response=response,
            log_prompt_and_response=self._log_prompt_and_response,
            kwargs=kwargs)
        if return_result:
            self._logger.debug(f"invoke_wrapper: process sync response return")
            return return_result

        self._ingest_units(request)

        self._logger.debug(f"invoke_wrapper: finished")
        return response

    def _create_extra_headers(
        self
    ) -> 'dict[str, str]':
        extra_headers: dict[str, str] = {}
        context = self.get_context()
        if context:
            self._update_extra_headers(context, extra_headers)

        return extra_headers

    def set_xproxy_result(self, response: Optional[Union[XproxyResult, XproxyError]]) -> Optional[Union[XproxyResult, XproxyError]]:
        self._last_result = response
        return response

    @staticmethod
    def _update_extra_headers(
        context: _Context,
        extra_headers: "dict[str, str]",
    ) -> None:
        context_limit_ids: Optional[list[str]] = context.get("limit_ids")

        context_use_case_name: Optional[str] = context.get("use_case_name")
        context_use_case_id: Optional[str] = context.get("use_case_id")
        context_use_case_version: Optional[int] = context.get("use_case_version")
        context_use_case_step: Optional[str] = context.get("use_case_step")

        context_user_id: Optional[str] = context.get("user_id")
        context_account_name: Optional[str] = context.get("account_name")
        context_request_tags: Optional[list[str]] = context.get("request_tags")

        context_price_as_category: Optional[str] = context.get("price_as_category")
        context_price_as_resource: Optional[str] = context.get("price_as_resource")
        context_resource_scope: Optional[str] = context.get("resource_scope")

        # headers_limit_ids = extra_headers.get(PayiHeaderNames.limit_ids, None)
    
        # If the caller specifies limit_ids in extra_headers, it takes precedence over the decorator
        if PayiHeaderNames.limit_ids in extra_headers:
            headers_limit_ids = extra_headers.get(PayiHeaderNames.limit_ids)

            if headers_limit_ids is None or len(headers_limit_ids) == 0:
                # headers_limit_ids is empty, remove it from extra_headers
                extra_headers.pop(PayiHeaderNames.limit_ids, None)
            else:   
                # leave the value in extra_headers
                ...
        elif context_limit_ids:
            extra_headers[PayiHeaderNames.limit_ids] = ",".join(context_limit_ids)

        if PayiHeaderNames.user_id in extra_headers:
            headers_user_id = extra_headers.get(PayiHeaderNames.user_id, None)
            if headers_user_id is None or len(headers_user_id) == 0:
                # headers_user_id is empty, remove it from extra_headers
                extra_headers.pop(PayiHeaderNames.user_id, None)
            else:
                # leave the value in extra_headers
                ...
        elif context_user_id:
            extra_headers[PayiHeaderNames.user_id] = context_user_id

        if PayiHeaderNames.account_name in extra_headers:
            headers_account_name = extra_headers.get(PayiHeaderNames.account_name, None)
            if headers_account_name is None or len(headers_account_name) == 0:
                # headers_account_name is empty, remove it from extra_headers
                extra_headers.pop(PayiHeaderNames.account_name, None)
            else:
                # leave the value in extra_headers
                ...
        elif context_account_name:
            extra_headers[PayiHeaderNames.account_name] = context_account_name

        if PayiHeaderNames.use_case_name in extra_headers:
            headers_use_case_name = extra_headers.get(PayiHeaderNames.use_case_name, None)
            if headers_use_case_name is None or len(headers_use_case_name) == 0:
                # headers_use_case_name is empty, remove all use case related headers
                extra_headers.pop(PayiHeaderNames.use_case_name, None)
                extra_headers.pop(PayiHeaderNames.use_case_id, None)
                extra_headers.pop(PayiHeaderNames.use_case_version, None)
                extra_headers.pop(PayiHeaderNames.use_case_step, None)
            else:
                # leave the value in extra_headers
                ...
        elif context_use_case_name:
            extra_headers[PayiHeaderNames.use_case_name] = context_use_case_name
            if context_use_case_id is not None:
                extra_headers[PayiHeaderNames.use_case_id] = context_use_case_id
            if context_use_case_version is not None:
                extra_headers[PayiHeaderNames.use_case_version] = str(context_use_case_version)
            if context_use_case_step is not None:
                extra_headers[PayiHeaderNames.use_case_step] = str(context_use_case_step)

        if PayiHeaderNames.request_tags not in extra_headers and context_request_tags:
            extra_headers[PayiHeaderNames.request_tags] = ",".join(context_request_tags)

        if PayiHeaderNames.price_as_category not in extra_headers and context_price_as_category:
            extra_headers[PayiHeaderNames.price_as_category] = context_price_as_category

        if PayiHeaderNames.price_as_resource not in extra_headers and context_price_as_resource:
            extra_headers[PayiHeaderNames.price_as_resource] = context_price_as_resource

        if PayiHeaderNames.resource_scope not in extra_headers and context_resource_scope:
            extra_headers[PayiHeaderNames.resource_scope] = context_resource_scope

    @staticmethod
    def update_for_vision(input: int, units: 'dict[str, Units]', estimated_prompt_tokens: Optional[int], is_large_context: bool = False) -> int:
        if estimated_prompt_tokens:
            vision = input - estimated_prompt_tokens
            if (vision > 0):
                key = "vision_large_context" if is_large_context else "vision"
                units[key] = Units(input=vision, output=0)
                input = estimated_prompt_tokens
        
        return input

    @staticmethod
    def payi_wrapper(func: Any) -> Any:
        def _payi_wrapper(o: Any) -> Any:
            def wrapper(wrapped: Any, instance: Any, args: Any, kwargs: Any) -> Any:
                return func(
                    o,
                    wrapped,
                    instance,
                    *args,
                    **kwargs,
                )

            return wrapper

        return _payi_wrapper

    @staticmethod
    def payi_awrapper(func: Any) -> Any:
        def _payi_awrapper(o: Any) -> Any:
            async def wrapper(wrapped: Any, instance: Any, args: Any, kwargs: Any) -> Any:
                return await func(
                    o,
                    wrapped,
                    instance,
                    *args,
                    **kwargs,
                )

            return wrapper

        return _payi_awrapper

class _StreamIteratorWrapper(ObjectProxy):  # type: ignore
    def __init__(
        self,
        response: Any,
        instance: Any,
        instrumentor: _PayiInstrumentor,
        stopwatch: Stopwatch,
        request: _ProviderRequest,
    ) -> None:

        instrumentor._logger.debug(f"StreamIteratorWrapper: instance {instance}, category {request._category}")

        request.process_initial_stream_response(response)

        bedrock_from_stream: bool = False
        if request.is_aws_client:
            stream = response.get("stream", None)

            if stream:
                response = stream
                bedrock_from_stream = True
            else:
                response = response.get("body")
                bedrock_from_stream = False

        super().__init__(response)  # type: ignore

        self._response = response
        self._instance = instance

        self._instrumentor = instrumentor
        self._stopwatch: Stopwatch = stopwatch
        self._responses: list[str] = []

        self._request: _ProviderRequest = request

        self._first_token: bool = True
        self._bedrock_from_stream: bool = bedrock_from_stream
        self._ingested: bool = False
        self._iter_started: bool = False

    def __enter__(self) -> Any:
        self._instrumentor._logger.debug(f"StreamIteratorWrapper: __enter__")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: 
        self._instrumentor._logger.debug(f"StreamIteratorWrapper: __exit__")
        self.__wrapped__.__exit__(exc_type, exc_val, exc_tb)  # type: ignore

    async def __aenter__(self) -> Any:
        self._instrumentor._logger.debug(f"StreamIteratorWrapper: __aenter__")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._instrumentor._logger.debug(f"StreamIteratorWrapper: __aexit__")
        await self.__wrapped__.__aexit__(exc_type, exc_val, exc_tb)  # type: ignore

    def __iter__(self) -> Any:  
        self._iter_started = True
        if self._request.is_aws_client:
            # MUST reside in a separate function so that the yield statement (e.g. the generator) doesn't implicitly return its own iterator and overriding self
            self._instrumentor._logger.debug(f"StreamIteratorWrapper: bedrock __iter__")
            return self._iter_bedrock()

        self._instrumentor._logger.debug(f"StreamIteratorWrapper: __iter__")
        return self

    def _iter_bedrock(self) -> Any:
        # botocore EventStream doesn't have a __next__ method so iterate over the wrapped object in place
        for event in self.__wrapped__: # type: ignore
            result: Optional[_ChunkResult] = None

            if (self._bedrock_from_stream):
                result = self._evaluate_chunk(event)
            else:
                chunk = event.get('chunk') # type: ignore
                if chunk:
                    decode = chunk.get('bytes').decode() # type: ignore
                    result = self._evaluate_chunk(decode)

            if result and result.ingest:
                self._stop_iteration()

            yield event

        self._instrumentor._logger.debug(f"StreamIteratorWrapper: bedrock iter finished")

        self._stop_iteration()

    def __aiter__(self) -> Any:
        self._iter_started = True
        self._instrumentor._logger.debug(f"StreamIteratorWrapper: __aiter__")
        return self

    def __next__(self) -> object:
        try:
            chunk: object = self.__wrapped__.__next__()  # type: ignore

            if self._ingested:
                self._instrumentor._logger.debug(f"StreamIteratorWrapper: __next__ already ingested, not processing chunk {chunk}")
                return chunk # type: ignore

            result = self._evaluate_chunk(chunk)

            if result.ingest:
                self._stop_iteration()

            if result.send_chunk_to_caller:
                return chunk # type: ignore
            else:
                return self.__next__()
        except Exception as e:
            if isinstance(e, StopIteration):
                self._stop_iteration()
            else:
                self._instrumentor._logger.debug(f"StreamIteratorWrapper: __next__ exception {e}")
            raise e

    async def __anext__(self) -> object:
        try:
            chunk: object = await self.__wrapped__.__anext__()  # type: ignore

            if self._ingested:
                self._instrumentor._logger.debug(f"StreamIteratorWrapper: __next__ already ingested, not processing chunk {chunk}")
                return chunk # type: ignore

            result = self._evaluate_chunk(chunk)

            if result.ingest:
                await self._astop_iteration()

            if  result.send_chunk_to_caller:
                return chunk # type: ignore
            else:
                return await self.__anext__()

        except Exception as e:
            if isinstance(e, StopAsyncIteration):
                await self._astop_iteration()
            else:
                self._instrumentor._logger.debug(f"StreamIteratorWrapper: __anext__ exception {e}")
            raise e

    def _evaluate_chunk(self, chunk: Any) -> _ChunkResult:
        if self._first_token:
            self._request._ingest["time_to_first_token_ms"] = self._stopwatch.elapsed_ms_int()
            self._first_token = False

        if self._instrumentor._log_prompt_and_response:
            self._responses.append(self.chunk_to_json(chunk))

        return self._request.process_chunk(chunk)

    def _process_stop_iteration(self) -> None:
        self._instrumentor._logger.debug(f"StreamIteratorWrapper: process stop iteration")

        self._stopwatch.stop()
        self._request._ingest["end_to_end_latency_ms"] = self._stopwatch.elapsed_ms_int()
        self._request._ingest["http_status_code"] = 200

        if self._instrumentor._log_prompt_and_response:
            self._request._ingest["provider_response_json"] = self._responses

    async def _astop_iteration(self) -> None:
        if self._ingested:
            self._instrumentor._logger.debug(f"StreamIteratorWrapper: astop iteration already ingested, skipping")
            return

        self._process_stop_iteration()

        await self._instrumentor._aingest_units(self._request)
        self._ingested = True

    def _stop_iteration(self) -> None:
        if self._ingested:
            self._instrumentor._logger.debug(f"StreamIteratorWrapper: stop iteration already ingested, skipping")
            return

        self._process_stop_iteration()
        self._instrumentor._ingest_units(self._request)
        self._ingested = True

    @staticmethod
    def chunk_to_json(chunk: Any) -> str:
        if hasattr(chunk, "to_json"):
            return str(chunk.to_json())
        elif isinstance(chunk, bytes):
            return chunk.decode()
        elif isinstance(chunk, str):
            return chunk
        else:
            # assume dict
            return json.dumps(chunk)

class _StreamManagerWrapper(ObjectProxy):  # type: ignore
    def __init__(
        self,
        stream_manager: Any,  # type: ignore
        instance: Any,
        instrumentor: _PayiInstrumentor, 
        stopwatch: Stopwatch,
        request: _ProviderRequest,
    ) -> None:
        instrumentor._logger.debug(f"StreamManagerWrapper: instance {instance}, category {request._category}")

        super().__init__(stream_manager)  # type: ignore

        self._stream_manager = stream_manager  
        self._instance = instance
        self._instrumentor = instrumentor
        self._stopwatch: Stopwatch = stopwatch
        self._responses: list[str] = []
        self._request: _ProviderRequest = request
        self._first_token: bool = True

    def __enter__(self) -> _StreamIteratorWrapper:
        self._instrumentor._logger.debug(f"_StreamManagerWrapper: __enter__")

        return _StreamIteratorWrapper(
            response=self.__wrapped__.__enter__(),  # type: ignore
            instance=self._instance,
            instrumentor=self._instrumentor,
            stopwatch=self._stopwatch,
            request=self._request,
        )

class _GeneratorWrapper:  # type: ignore
    def __init__(
        self,
        generator: Any,
        instance: Any,
        instrumentor: _PayiInstrumentor, 
        stopwatch: Stopwatch,
        request: _ProviderRequest,
    ) -> None:
        instrumentor._logger.debug(f"GeneratorWrapper: instance {instance}, category {request._category}")

        super().__init__()  # type: ignore
        
        self._generator = generator
        self._instance = instance
        self._instrumentor = instrumentor
        self._stopwatch: Stopwatch = stopwatch
        self._log_prompt_and_response: bool = instrumentor._log_prompt_and_response
        self._responses: list[str] = []
        self._request: _ProviderRequest = request
        self._first_token: bool = True
        self._ingested: bool = False
        self._iter_started: bool = False

    def __iter__(self) -> Any:
        self._iter_started = True
        self._instrumentor._logger.debug(f"GeneratorWrapper: __iter__")
        return self
        
    def __aiter__(self) -> Any:
        self._instrumentor._logger.debug(f"GeneratorWrapper: __aiter__")
        return self

    def _process_chunk(self, chunk: Any) -> _ChunkResult:
        if self._first_token:
            self._request._ingest["time_to_first_token_ms"] = self._stopwatch.elapsed_ms_int()
            self._first_token = False
            
        if self._log_prompt_and_response:
            dict = self._chunk_to_dict(chunk) 
            self._responses.append(json.dumps(dict))
                
        return self._request.process_chunk(chunk)
    
    def __next__(self) -> Any:
        try:
            chunk = next(self._generator)
            result = self._process_chunk(chunk)

            if result.ingest:
                self._stop_iteration()

            # ignore result.send_chunk_to_caller:
            return chunk

        except Exception as e:
            if isinstance(e, StopIteration):
                self._stop_iteration()
            else:
                self._instrumentor._logger.debug(f"GeneratorWrapper: __next__ exception {e}")            
            raise e

    async def __anext__(self) -> Any:
        try:
            chunk = await anext(self._generator) # type: ignore
            result = self._process_chunk(chunk)

            if result.ingest:
                await self._astop_iteration()

            # ignore result.send_chunk_to_caller:
            return chunk # type: ignore

        except Exception as e:
            if isinstance(e, StopAsyncIteration):
                await self._astop_iteration()
            else:
                self._instrumentor._logger.debug(f"GeneratorWrapper: __anext__ exception {e}")
            raise e

    @staticmethod
    def _chunk_to_dict(chunk: Any) -> 'dict[str, object]':
        if hasattr(chunk, "to_dict"):
            return chunk.to_dict() # type: ignore
        elif hasattr(chunk, "to_json_dict"):  
            return chunk.to_json_dict() # type: ignore
        else:
            return {}

    def _stop_iteration(self) -> None:
        if self._ingested:
            self._instrumentor._logger.debug(f"GeneratorWrapper: stop iteration already ingested, skipping")
            return

        self._process_stop_iteration()

        self._instrumentor._ingest_units(self._request)
        self._ingested = True

    async def _astop_iteration(self) -> None:
        if self._ingested:
            self._instrumentor._logger.debug(f"GeneratorWrapper: astop iteration already ingested, skipping")
            return

        self._process_stop_iteration()
        
        await self._instrumentor._aingest_units(self._request)
        self._ingested = True

    def _process_stop_iteration(self) -> None:
        self._instrumentor._logger.debug(f"GeneratorWrapper: stop iteration")

        self._stopwatch.stop()
        self._request._ingest["end_to_end_latency_ms"] = self._stopwatch.elapsed_ms_int()
        self._request._ingest["http_status_code"] = 200
            
        if self._log_prompt_and_response:
            self._request._ingest["provider_response_json"] = self._responses

global _instrumentor
_instrumentor: Optional[_PayiInstrumentor] = None

def payi_instrument(
    *,
    payi: Optional[Union[Payi, AsyncPayi, 'list[Union[Payi, AsyncPayi]]']] = None,
    instruments: Optional[Set[str]] = None,
    log_prompt_and_response: bool = True,
    prompt_and_response_logger: Optional[Callable[[str, "dict[str, str]"], None]] = None,
    config: Optional[PayiInstrumentConfig] = None,
    logger: Optional[logging.Logger] = None,
) -> None:
    global _instrumentor
    if (_instrumentor):
        return
    
    payi_param: Optional[Payi] = None
    apayi_param: Optional[AsyncPayi] = None

    if isinstance(payi, Payi):
        payi_param = payi
    elif isinstance(payi, AsyncPayi):
        apayi_param = payi
    elif isinstance(payi, list):
        for p in payi:
            if isinstance(p, Payi):
                payi_param = p
            elif isinstance(p, AsyncPayi): # type: ignore
                apayi_param = p
    frameinfo = inspect.stack()[1]
    caller_filename = os.path.basename(frameinfo.filename).replace(' ', '_').lower()
    if caller_filename.endswith('.py'):
        caller_filename = caller_filename[:-3]

    # allow for both payi and apayi to be None for the @proxy case
    _instrumentor = _PayiInstrumentor(
        payi=payi_param,
        apayi=apayi_param,
        instruments=instruments,
        log_prompt_and_response=log_prompt_and_response,
        logger=logger,
        prompt_and_response_logger=prompt_and_response_logger,
        global_config=config if config else PayiInstrumentConfig(),
        caller_filename=caller_filename
    )

def track(
    *,
    limit_ids: Optional["list[str]"] = None,
    use_case_name: Optional[str] = None,
    use_case_id: Optional[str] = None,
    use_case_version: Optional[int] = None,
    user_id: Optional[str] = None,
    account_name: Optional[str] = None,
    request_tags: Optional["list[str]"] = None,
    request_properties: Optional["dict[str, str]"] = None,
    use_case_properties: Optional["dict[str, str]"] = None,
    proxy: Optional[bool] = None,
) -> Any:

    def _track(func: Any) -> Any:
        import asyncio
        if asyncio.iscoroutinefunction(func):
            async def awrapper(*args: Any, **kwargs: Any) -> Any:
                if not _instrumentor:
                    _g_logger.debug(f"track: no instrumentor!")
                    return await func(*args, **kwargs)

                _instrumentor._logger.debug(f"track: call async function (proxy={proxy}, limit_ids={limit_ids}, use_case_name={use_case_name}, use_case_id={use_case_id}, use_case_version={use_case_version}, user_id={user_id})")
                # Call the instrumentor's _call_func for async functions
                return await _instrumentor._acall_func(
                    func,
                    proxy,
                    limit_ids,
                    use_case_name,
                    use_case_id,
                    use_case_version,
                    user_id,
                    account_name,
                    request_tags,
                    request_properties,
                    use_case_properties,
                    *args,
                    **kwargs,
                )
            return awrapper
        else:
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                if not _instrumentor:
                    _g_logger.debug(f"track: no instrumentor!")
                    return func(*args, **kwargs)

                _instrumentor._logger.debug(f"track: call sync function (proxy={proxy}, limit_ids={limit_ids}, use_case_name={use_case_name}, use_case_id={use_case_id}, use_case_version={use_case_version}, user_id={user_id}, account_name={account_name})")

                return _instrumentor._call_func(
                    func,
                    proxy,
                    limit_ids,
                    use_case_name,
                    use_case_id,
                    use_case_version,
                    user_id,
                    account_name,
                    request_tags,
                    request_properties,
                    use_case_properties,
                    *args,
                    **kwargs,
                )
            return wrapper
    return _track

def track_context(
    *,
    limit_ids: Optional["list[str]"] = None,
    use_case_name: Optional[str] = None,
    use_case_id: Optional[str] = None,
    use_case_version: Optional[int] = None,
    use_case_step: Optional[str] = None,
    user_id: Optional[str] = None,
    account_name: Optional[str] = None,
    request_tags: Optional["list[str]"] = None,
    request_properties: Optional["dict[str, str]"] = None,
    use_case_properties: Optional["dict[str, str]"] = None,
    price_as_category: Optional[str] = None,
    price_as_resource: Optional[str] = None,
    resource_scope: Optional[str] = None,
    proxy: Optional[bool] = None,
) -> _InternalTrackContext:
    # Create a new context for tracking
    context: _Context = {}

    context["proxy"] = proxy

    context["limit_ids"] = limit_ids

    context["use_case_name"] = use_case_name
    context["use_case_id"] = use_case_id
    context["use_case_version"] = use_case_version
    context["use_case_step"] = use_case_step

    context["user_id"] = user_id
    context["account_name"] = account_name
    context["request_tags"] = request_tags

    context["price_as_category"] = price_as_category
    context["price_as_resource"] = price_as_resource
    context["resource_scope"] = resource_scope

    context["request_properties"] = request_properties
    context["use_case_properties"] = use_case_properties

    return _InternalTrackContext(context)

def get_context() -> PayiContext:
    """
    Returns the current tracking context from calls to @track and with track_context().
    If no context is active, returns an empty context.
    """
    if not _instrumentor:
        return PayiContext()
    internal_context = _instrumentor.get_context() or {}

    context_dict = {
        key: value
        for key, value in internal_context.items()
        if key in PayiContext.__annotations__ and value is not None
    }
    if _instrumentor._last_result:
        context_dict["last_result"] = _instrumentor._last_result
    return PayiContext(**dict(context_dict))  # type: ignore