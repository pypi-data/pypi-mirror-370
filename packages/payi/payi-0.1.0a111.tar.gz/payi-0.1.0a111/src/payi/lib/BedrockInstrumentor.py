import os
import json
from typing import Any, Optional, Sequence
from functools import wraps
from typing_extensions import override

from wrapt import ObjectProxy, wrap_function_wrapper  # type: ignore
from tokenizers import Tokenizer  # type: ignore

from payi.lib.helpers import PayiCategories, PayiHeaderNames, payi_aws_bedrock_url
from payi.types.ingest_units_params import Units
from payi.types.pay_i_common_models_api_router_header_info_param import PayICommonModelsAPIRouterHeaderInfoParam

from .instrument import _ChunkResult, _IsStreaming, _StreamingType, _ProviderRequest, _PayiInstrumentor
from .version_helper import get_version_helper


class BedrockInstrumentor:
    _module_name: str = "boto3"
    _module_version: str = ""

    _instrumentor: _PayiInstrumentor

    @staticmethod
    def instrument(instrumentor: _PayiInstrumentor) -> None:
        BedrockInstrumentor._instrumentor = instrumentor

        BedrockInstrumentor._module_version = get_version_helper(BedrockInstrumentor._module_name)

        try:
            wrap_function_wrapper(
                "botocore.client",
                "ClientCreator.create_client",
                create_client_wrapper(instrumentor),
            )

            wrap_function_wrapper(
                "botocore.session",
                "Session.create_client",
                create_client_wrapper(instrumentor),
            )

        except Exception as e:
            instrumentor._logger.debug(f"Error instrumenting bedrock: {e}")
            return

@_PayiInstrumentor.payi_wrapper
def create_client_wrapper(instrumentor: _PayiInstrumentor, wrapped: Any, instance: Any, *args: Any, **kwargs: Any) -> Any: #  noqa: ARG001
    if kwargs.get("service_name") != "bedrock-runtime":
        # instrumentor._logger.debug(f"skipping client wrapper creation for {kwargs.get('service_name', '')} service")
        return wrapped(*args, **kwargs)

    try:
        client: Any = wrapped(*args, **kwargs)
        client.invoke_model = wrap_invoke(instrumentor, client.invoke_model)
        client.invoke_model_with_response_stream = wrap_invoke_stream(instrumentor, client.invoke_model_with_response_stream)
        client.converse = wrap_converse(instrumentor, client.converse)
        client.converse_stream = wrap_converse_stream(instrumentor, client.converse_stream)

        instrumentor._logger.debug(f"Instrumented bedrock client")

        if BedrockInstrumentor._instrumentor._proxy_default:
            # Register client callbacks to handle the Pay-i extra_headers parameter in the inference calls and redirect the request to the Pay-i endpoint
            _register_bedrock_client_callbacks(client)
            instrumentor._logger.debug(f"Registered bedrock client callbaks for proxy")

        return client
    except Exception as e:
        instrumentor._logger.debug(f"Error instrumenting bedrock client: {e}")
    
    return wrapped(*args, **kwargs)

BEDROCK_REQUEST_NAMES = [
    'request-created.bedrock-runtime.Converse',
    'request-created.bedrock-runtime.ConverseStream',
    'request-created.bedrock-runtime.InvokeModel',
    'request-created.bedrock-runtime.InvokeModelWithResponseStream',
]

def _register_bedrock_client_callbacks(client: Any) -> None:
    # Pass a unqiue_id to avoid registering the same callback multiple times in case this cell executed more than once
    # Redirect the request to the Pay-i endpoint after the request has been signed. 
    client.meta.events.register_last('request-created', _redirect_to_payi, unique_id=_redirect_to_payi)

def _redirect_to_payi(request: Any, event_name: str, **_: 'dict[str, Any]') -> None:
    from urllib3.util import parse_url
    from urllib3.util.url import Url

    if not event_name in BEDROCK_REQUEST_NAMES:
        return
    
    parsed_url: Url = parse_url(request.url)
    route_path = parsed_url.path
    request.url = f"{payi_aws_bedrock_url()}{route_path}"

    request.headers[PayiHeaderNames.api_key] = os.environ.get("PAYI_API_KEY", "")
    request.headers[PayiHeaderNames.provider_base_uri] = parsed_url.scheme + "://" + parsed_url.host # type: ignore
    
    extra_headers = BedrockInstrumentor._instrumentor._create_extra_headers()

    for key, value in extra_headers.items():
        request.headers[key] = value


class InvokeResponseWrapper(ObjectProxy): # type: ignore
    _cohere_embed_english_v3_tokenizer: Optional[Tokenizer] = None

    def __init__(
        self,
        response: Any,
        request: '_BedrockInvokeProviderRequest',
        log_prompt_and_response: bool
        ) -> None:

        super().__init__(response) # type: ignore
        self._response = response
        self._request = request
        self._log_prompt_and_response = log_prompt_and_response

    def read(self, amt: Any =None) -> Any: # type: ignore
        # data is array of bytes
        data: bytes = self.__wrapped__.read(amt) # type: ignore
        response = json.loads(data) # type: ignore

        ingest = self._request._ingest

        # resource = ingest["resource"]
        # if not resource:
        #     return
        
        input: int = 0
        output: int = 0
        units: dict[str, Units] = ingest["units"]

        if self._request._is_anthropic:
            from .AnthropicInstrumentor import anthropic_process_synchronous_response

            anthropic_process_synchronous_response(
                request=self._request, 
                response=response,
                log_prompt_and_response=False, # will evaluate logging later
                assign_id=False)

        elif self._request._is_meta:
            input = response.get('prompt_token_count', 0)
            output = response.get('generation_token_count', 0)
            units["text"] = Units(input=input, output=output)

        elif self._request._is_nova:
            usage = response.get("usage", {})

            input = usage.get("inputTokens", 0)
            output = usage.get("outputTokens", 0)
            units["text"] = Units(input=input, output=output)

            text_cache_read = usage.get("cacheReadInputTokenCount", None)
            if text_cache_read:
                units["text_cache_read"] = text_cache_read

            text_cache_write = usage.get("cacheWriteInputTokenCount", None)
            if text_cache_write:
                units["text_cache_write"] = text_cache_write

            bedrock_converse_process_synchronous_function_call(self._request, response)

        elif self._request._is_amazon_titan_embed_text_v1:
            input = response.get('inputTextTokenCount', 0)
            units["text"] = Units(input=input, output=0)

        elif self._request._is_cohere_embed_english_v3:
            texts: list[str] = response.get("texts", [])
            if texts and len(texts) > 0:
                text = " ".join(texts)

                if self._cohere_embed_english_v3_tokenizer is None:
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    tokenizer_path = os.path.join(current_dir, "data", "cohere_embed_english_v3.json")
                    self._cohere_embed_english_v3_tokenizer = Tokenizer.from_file(tokenizer_path) # type: ignore

                tokens: list = self._cohere_embed_english_v3_tokenizer.encode(text, add_special_tokens=False).tokens # type: ignore

                if tokens and isinstance(tokens, list):
                    units["text"] = Units(input=len(tokens), output=0) # type: ignore

        if self._log_prompt_and_response:
            ingest["provider_response_json"] = data.decode('utf-8') # type: ignore
            
        self._request._instrumentor._ingest_units(self._request)

        return data # type: ignore

def wrap_invoke(instrumentor: _PayiInstrumentor, wrapped: Any) -> Any:
    @wraps(wrapped)
    def invoke_wrapper(*args: Any, **kwargs: 'dict[str, Any]') -> Any:
        modelId:str = kwargs.get("modelId", "") # type: ignore

        return instrumentor.invoke_wrapper(
            _BedrockInvokeProviderRequest(instrumentor=instrumentor, model_id=modelId),
            _IsStreaming.false,
            wrapped,
            None,
            args,
            kwargs,
        )   
    
    return invoke_wrapper

def wrap_invoke_stream(instrumentor: _PayiInstrumentor, wrapped: Any) -> Any:
    @wraps(wrapped)
    def invoke_wrapper(*args: Any, **kwargs: Any) -> Any:
        modelId: str = kwargs.get("modelId", "") # type: ignore

        instrumentor._logger.debug(f"bedrock invoke stream wrapper, modelId: {modelId}")
        return instrumentor.invoke_wrapper(
            _BedrockInvokeProviderRequest(instrumentor=instrumentor, model_id=modelId),
            _IsStreaming.true,
            wrapped,
            None,
            args,
            kwargs,
        )

    return invoke_wrapper

def wrap_converse(instrumentor: _PayiInstrumentor, wrapped: Any) -> Any:
    @wraps(wrapped)
    def invoke_wrapper(*args: Any, **kwargs: 'dict[str, Any]') -> Any:
        modelId:str = kwargs.get("modelId", "") # type: ignore

        instrumentor._logger.debug(f"bedrock converse wrapper, modelId: {modelId}")
        return instrumentor.invoke_wrapper(
            _BedrockConverseProviderRequest(instrumentor=instrumentor),
            _IsStreaming.false,
            wrapped,
            None,
            args,
            kwargs,
        )
    
    return invoke_wrapper

def wrap_converse_stream(instrumentor: _PayiInstrumentor, wrapped: Any) -> Any:
    @wraps(wrapped)
    def invoke_wrapper(*args: Any, **kwargs: Any) -> Any:
        modelId: str = kwargs.get("modelId", "") # type: ignore

        instrumentor._logger.debug(f"bedrock converse stream wrapper, modelId: {modelId}")
        return instrumentor.invoke_wrapper(
            _BedrockConverseProviderRequest(instrumentor=instrumentor),
            _IsStreaming.true,
            wrapped,
            None,
            args,
            kwargs,
        )

    return invoke_wrapper

class _BedrockProviderRequest(_ProviderRequest):
    def __init__(self, instrumentor: _PayiInstrumentor):
        super().__init__(
            instrumentor=instrumentor,
            category=PayiCategories.aws_bedrock,
            streaming_type=_StreamingType.iterator,
            module_name=BedrockInstrumentor._module_name,
            module_version=BedrockInstrumentor._module_version,
            is_aws_client=True,
            )

    @override
    def process_request(self, instance: Any, extra_headers: 'dict[str, str]', args: Sequence[Any], kwargs: Any) -> bool:
        # boto3 doesn't allow extra_headers
        kwargs.pop("extra_headers", None)
        self._ingest["resource"] = kwargs.get("modelId", "")
        return True

    @override
    def process_initial_stream_response(self, response: Any) -> None:
        self._ingest["provider_response_id"] = response.get("ResponseMetadata", {}).get("RequestId", None)

    @override
    def process_exception(self, exception: Exception, kwargs: Any, ) -> bool:
        try:
            if hasattr(exception, "response"):
                response: dict[str, Any] = getattr(exception, "response", {})
                status_code: int = response.get('ResponseMetadata', {}).get('HTTPStatusCode', 0)
                if status_code == 0:
                    return False

                self._ingest["http_status_code"] = status_code
                
                request_id = response.get('ResponseMetadata', {}).get('RequestId', "")
                if request_id:
                    self._ingest["provider_response_id"] = request_id

                error = response.get('Error', "")
                if error:
                    self._ingest["provider_response_json"] = json.dumps(error)

            return True

        except Exception as e:
            self._instrumentor._logger.debug(f"Error processing exception: {e}")
            return False

class _BedrockInvokeProviderRequest(_BedrockProviderRequest):
    def __init__(self, instrumentor: _PayiInstrumentor, model_id: str):
        super().__init__(instrumentor=instrumentor)
        self._is_anthropic: bool = 'anthropic' in model_id
        self._is_nova: bool = 'nova' in model_id
        self._is_meta: bool = 'meta' in model_id
        self._is_amazon_titan_embed_text_v1: bool = 'amazon.titan-embed-text-v1' == model_id
        self._is_cohere_embed_english_v3: bool = 'cohere.embed-english-v3' == model_id

    @override
    def process_request(self, instance: Any, extra_headers: 'dict[str, str]', args: Sequence[Any], kwargs: Any) -> bool:
        from .AnthropicInstrumentor import anthropic_has_image_and_get_texts

        super().process_request(instance, extra_headers, args, kwargs)
    
        if self._is_anthropic:
            try:
                body = json.loads( kwargs.get("body", ""))
                messages = body.get("messages", {})
                if messages:
                    anthropic_has_image_and_get_texts(self, messages)
            except Exception as e:
                self._instrumentor._logger.debug(f"Bedrock invoke error processing request body: {e}")
        elif self._is_cohere_embed_english_v3:
            try:
                body = json.loads( kwargs.get("body", ""))
                input_type = body.get("input_type", "")
                if input_type == 'image':
                    images = body.get("images", [])
                    if (len(images) > 0):
                        # only supports one image according to docs
                        self._ingest["units"]["vision"] = Units(input=1, output=0)
            except Exception as e:
                self._instrumentor._logger.debug(f"Bedrock invoke error processing request body: {e}")
        return True

    @override
    def process_chunk(self, chunk: Any) -> _ChunkResult:
        chunk_dict = json.loads(chunk)

        if self._is_anthropic:
            from .AnthropicInstrumentor import anthropic_process_chunk
            return anthropic_process_chunk(self, chunk_dict, assign_id=False)
        
        if self._is_nova:
            bedrock_converse_process_streaming_for_function_call(self, chunk_dict)

        # meta and nova
        return self.process_invoke_other_provider_chunk(chunk_dict)

    def process_invoke_other_provider_chunk(self, chunk_dict: 'dict[str, Any]') -> _ChunkResult:
        ingest = False

        metrics = chunk_dict.get("amazon-bedrock-invocationMetrics", {})
        if metrics:
            input = metrics.get("inputTokenCount", 0)
            output = metrics.get("outputTokenCount", 0)
            self._ingest["units"]["text"] = Units(input=input, output=output)

            text_cache_read = metrics.get("cacheReadInputTokenCount", None)
            if text_cache_read:
                self._ingest["units"]["text_cache_read"] = text_cache_read

            text_cache_write = metrics.get("cacheWriteInputTokenCount", None)
            if text_cache_write:
                self._ingest["units"]["text_cache_write"] = text_cache_write

            ingest = True

        return _ChunkResult(send_chunk_to_caller=True, ingest=ingest)    

    @override
    def process_synchronous_response(
        self,
        response: Any,
        log_prompt_and_response: bool,
        kwargs: Any) -> Any:

        metadata = response.get("ResponseMetadata", {})

        request_id = metadata.get("RequestId", "")
        if request_id:
            self._ingest["provider_response_id"] = request_id

        response_headers = metadata.get("HTTPHeaders", {}).copy()
        if response_headers:
            self._ingest["provider_response_headers"] = [PayICommonModelsAPIRouterHeaderInfoParam(name=k, value=v) for k, v in response_headers.items()]

        response["body"] = InvokeResponseWrapper(
            response=response["body"],
            request=self,
            log_prompt_and_response=log_prompt_and_response)

        return response

    @override
    def remove_inline_data(self, prompt: 'dict[str, Any]') -> bool:# noqa: ARG002
        if not self._is_anthropic:
            return False

        from .AnthropicInstrumentor import anthropic_remove_inline_data
        body = prompt.get("body", "")
        if not body:
            return False
        
        body_json = json.loads(body)
        
        if anthropic_remove_inline_data(body_json):
            prompt["body"] = json.dumps(body_json)
            return True

        return False

class _BedrockConverseProviderRequest(_BedrockProviderRequest):
    @override
    def process_synchronous_response(
        self,
        response: 'dict[str, Any]',
        log_prompt_and_response: bool,
        kwargs: Any) -> Any:

        usage = response["usage"]
        input = usage["inputTokens"]
        output = usage["outputTokens"]
        
        units: dict[str, Units] = self._ingest["units"]
        units["text"] = Units(input=input, output=output)

        metadata = response.get("ResponseMetadata", {})

        request_id = metadata.get("RequestId", "")
        if request_id:
            self._ingest["provider_response_id"] = request_id

        response_headers = metadata.get("HTTPHeaders", {})
        if response_headers:
            self._ingest["provider_response_headers"] = [PayICommonModelsAPIRouterHeaderInfoParam(name=k, value=v) for k, v in response_headers.items()]

        if log_prompt_and_response:
            response_without_metadata = response.copy()
            response_without_metadata.pop("ResponseMetadata", None)
            self._ingest["provider_response_json"] = json.dumps(response_without_metadata)

        bedrock_converse_process_synchronous_function_call(self, response)

        return None

    @override
    def process_chunk(self, chunk: 'dict[str, Any]') -> _ChunkResult:
        ingest = False
        metadata = chunk.get("metadata", {})

        if metadata:
            usage = metadata['usage']
            input = usage["inputTokens"]
            output = usage["outputTokens"]
            self._ingest["units"]["text"] = Units(input=input, output=output)

            ingest = True

        bedrock_converse_process_streaming_for_function_call(self, chunk)

        return _ChunkResult(send_chunk_to_caller=True, ingest=ingest)

def bedrock_converse_process_streaming_for_function_call(request: _ProviderRequest, chunk: 'dict[str, Any]') -> None:  
    contentBlockStart = chunk.get("contentBlockStart", {})
    tool_use = contentBlockStart.get("start", {}).get("toolUse", {})
    if tool_use:
        index = contentBlockStart.get("contentBlockIndex", None)
        name = tool_use.get("name", "")

        if name and index is not None:
            request.add_streaming_function_call(index=index, name=name, arguments=None)
        
        return

    contentBlockDelta = chunk.get("contentBlockDelta", {})
    tool_use = contentBlockDelta.get("delta", {}).get("toolUse", {})
    if tool_use:
        index = contentBlockDelta.get("contentBlockIndex", None)
        input = tool_use.get("input", "")

        if input and index is not None:
            request.add_streaming_function_call(index=index, name=None, arguments=input)

        return

def bedrock_converse_process_synchronous_function_call(request: _ProviderRequest, response: 'dict[str, Any]') -> None:
    content = response.get("output", {}).get("message", {}).get("content", [])
    if content:
        for item in content:
            tool_use = item.get("toolUse", {})
            if tool_use:
                name = tool_use.get("name", "")
                input = tool_use.get("input", {})
                arguments: Optional[str] = None

                if input and isinstance(input, dict):
                    arguments = json.dumps(input)
                
                if name:
                    request.add_synchronous_function_call(name=name, arguments=arguments)

