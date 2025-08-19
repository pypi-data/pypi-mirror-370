import json
from typing import Any, Union, Optional, Sequence
from typing_extensions import override
from importlib.metadata import version

import tiktoken  # type: ignore
from wrapt import wrap_function_wrapper  # type: ignore

from payi.lib.helpers import PayiCategories, PayiHeaderNames
from payi.types.ingest_units_params import Units

from .instrument import _ChunkResult, _IsStreaming, _StreamingType, _ProviderRequest, _PayiInstrumentor
from .version_helper import get_version_helper


class OpenAiInstrumentor:
    _module_name: str = "openai"
    _module_version: str = ""

    @staticmethod
    def is_azure(instance: Any) -> bool:
        from openai import AzureOpenAI, AsyncAzureOpenAI # type: ignore # noqa: I001

        return isinstance(instance._client, (AsyncAzureOpenAI, AzureOpenAI))

    @staticmethod
    def instrument(instrumentor: _PayiInstrumentor) -> None:
        try:
            OpenAiInstrumentor._module_version = get_version_helper(OpenAiInstrumentor._module_name)

            wrap_function_wrapper(
                "openai.resources.chat.completions",
                "Completions.create",
                chat_wrapper(instrumentor),
            )

            wrap_function_wrapper(
                "openai.resources.chat.completions",
                "AsyncCompletions.create",
                achat_wrapper(instrumentor),
            )

            wrap_function_wrapper(
                "openai.resources.embeddings",
                "Embeddings.create",
                embeddings_wrapper(instrumentor),
            )

            wrap_function_wrapper(
                "openai.resources.embeddings",
                 "AsyncEmbeddings.create",
                aembeddings_wrapper(instrumentor),
            )
        except Exception as e:
            instrumentor._logger.debug(f"Error instrumenting openai: {e}")

        # responses separately as they are relatively new and the client may not be using the latest openai module
        try:            
            wrap_function_wrapper(
                "openai.resources.responses",
                "Responses.create",
                responses_wrapper(instrumentor),
            )

            wrap_function_wrapper(
                "openai.resources.responses",
                "AsyncResponses.create",
                aresponses_wrapper(instrumentor),
            )

        except Exception as e:
            instrumentor._logger.debug(f"Error instrumenting openai: {e}")

@_PayiInstrumentor.payi_wrapper
def embeddings_wrapper(
    instrumentor: _PayiInstrumentor,
    wrapped: Any,
    instance: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    instrumentor._logger.debug("OpenAI Embeddings wrapper")
    return instrumentor.invoke_wrapper(
        _OpenAiEmbeddingsProviderRequest(instrumentor),
        _IsStreaming.false,
        wrapped,
        instance,
        args,
        kwargs,
    )

@_PayiInstrumentor.payi_wrapper
async def aembeddings_wrapper(
    instrumentor: _PayiInstrumentor,
    wrapped: Any,
    instance: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    instrumentor._logger.debug("async OpenAI Embeddings wrapper")
    return await instrumentor.async_invoke_wrapper(
        _OpenAiEmbeddingsProviderRequest(instrumentor),
        _IsStreaming.false,
        wrapped,
        instance,
        args,
        kwargs,
    )

@_PayiInstrumentor.payi_wrapper
def chat_wrapper(
    instrumentor: _PayiInstrumentor,
    wrapped: Any,
    instance: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    instrumentor._logger.debug("OpenAI completions wrapper")
    return instrumentor.invoke_wrapper(
        _OpenAiChatProviderRequest(instrumentor),
        _IsStreaming.kwargs,
        wrapped,
        instance,
        args,
        kwargs,
    )

@_PayiInstrumentor.payi_awrapper
async def achat_wrapper(
    instrumentor: _PayiInstrumentor,
    wrapped: Any,
    instance: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    instrumentor._logger.debug("async OpenAI completions wrapper")
    return await instrumentor.async_invoke_wrapper(
        _OpenAiChatProviderRequest(instrumentor),
        _IsStreaming.kwargs,
        wrapped,
        instance,
        args,
        kwargs,
    )
    
@_PayiInstrumentor.payi_wrapper
def responses_wrapper(
    instrumentor: _PayiInstrumentor,
    wrapped: Any,
    instance: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    instrumentor._logger.debug("OpenAI responses wrapper")
    return instrumentor.invoke_wrapper(
        _OpenAiResponsesProviderRequest(instrumentor),
        _IsStreaming.kwargs,
        wrapped,
        instance,
        args,
        kwargs,
    )

@_PayiInstrumentor.payi_awrapper
async def aresponses_wrapper(
    instrumentor: _PayiInstrumentor,
    wrapped: Any,
    instance: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    instrumentor._logger.debug("async OpenAI responses wrapper")
    return await instrumentor.async_invoke_wrapper(
        _OpenAiResponsesProviderRequest(instrumentor),
        _IsStreaming.kwargs,
        wrapped,
        instance,
        args,
        kwargs,
    )

class _OpenAiProviderRequest(_ProviderRequest):
    chat_input_tokens_key: str = "prompt_tokens"
    chat_output_tokens_key: str = "completion_tokens"
    chat_input_tokens_details_key: str = "prompt_tokens_details"

    responses_input_tokens_key: str = "input_tokens"
    responses_output_tokens_key: str = "output_tokens"
    responses_input_tokens_details_key: str = "input_tokens_details"

    def __init__(self, instrumentor: _PayiInstrumentor, input_tokens_key: str, output_tokens_key: str, input_tokens_details_key: str) -> None:
        super().__init__(
            instrumentor=instrumentor,
            category=PayiCategories.openai,
            streaming_type=_StreamingType.iterator,
            module_name=OpenAiInstrumentor._module_name,
            module_version=OpenAiInstrumentor._module_version,
            )
        self._input_tokens_key = input_tokens_key
        self._output_tokens_key = output_tokens_key
        self._input_tokens_details_key = input_tokens_details_key

    @override
    def process_request(self, instance: Any, extra_headers: 'dict[str, str]', args: Sequence[Any], kwargs: Any) -> bool: # type: ignore
        self._ingest["resource"] = kwargs.get("model", "")

        if not (instance and hasattr(instance, "_client")) or OpenAiInstrumentor.is_azure(instance) is False:
            return True

        context = self._instrumentor.get_context_safe()
        price_as_category = extra_headers.get(PayiHeaderNames.price_as_category) or context.get("price_as_category")
        price_as_resource = extra_headers.get(PayiHeaderNames.price_as_resource) or context.get("price_as_resource")
        resource_scope = extra_headers.get(PayiHeaderNames.resource_scope) or context.get("resource_scope")

        if PayiHeaderNames.price_as_category in extra_headers:
            del extra_headers[PayiHeaderNames.price_as_category]
        if PayiHeaderNames.price_as_resource in extra_headers:
            del extra_headers[PayiHeaderNames.price_as_resource]
        if PayiHeaderNames.resource_scope in extra_headers:
            del extra_headers[PayiHeaderNames.resource_scope]
            
        if not price_as_resource and not price_as_category:
            self._instrumentor._logger.error("Azure OpenAI requires price as resource and/or category to be specified, not ingesting")
            return False

        if resource_scope:
            if not(resource_scope in ["global", "datazone"] or resource_scope.startswith("region")):
                self._instrumentor._logger.error("Azure OpenAI invalid resource scope, not ingesting")
                return False

            self._ingest["resource_scope"] = resource_scope

        self._category = PayiCategories.azure_openai

        self._ingest["category"] = self._category

        if price_as_category:
            # price as category overrides default
            self._ingest["category"] = price_as_category
        if price_as_resource:
            self._ingest["resource"] = price_as_resource

        return True

    @override
    def process_exception(self, exception: Exception, kwargs: Any, ) -> bool:
        try:
            status_code: Optional[int] = None

            if hasattr(exception, "status_code"):
                status_code = getattr(exception, "status_code", None)
                if isinstance(status_code, int):
                    self._ingest["http_status_code"] = status_code

            if not status_code:
                self.exception_to_semantic_failure(exception,)
                return True

            if hasattr(exception, "request_id"):
                request_id = getattr(exception, "request_id", None)
                if isinstance(request_id, str):
                    self._ingest["provider_response_id"] = request_id

            if hasattr(exception, "response"):
                response = getattr(exception, "response", None)
                if hasattr(response, "text"):
                    text = getattr(response, "text", None)
                    if isinstance(text, str):
                        self._ingest["provider_response_json"] = text

        except Exception as e:
            self._instrumentor._logger.debug(f"Error processing exception: {e}")
            return False

        return True

    def process_synchronous_response_worker(
        self,
        response: str,
        log_prompt_and_response: bool,
        ) -> Any:
        response_dict = model_to_dict(response)

        self.add_usage_units(response_dict.get("usage", {}))

        if log_prompt_and_response:
            self._ingest["provider_response_json"] = [json.dumps(response_dict)]

        if "id" in response_dict:
            self._ingest["provider_response_id"] = response_dict["id"]

        return None

    def add_usage_units(self, usage: "dict[str, Any]",) -> None:
        units = self._ingest["units"]

        input = usage[self._input_tokens_key] if self._input_tokens_key in usage else 0
        output = usage[self._output_tokens_key] if self._output_tokens_key in usage else 0
        input_cache = 0

        prompt_tokens_details = usage.get(self._input_tokens_details_key)
        if prompt_tokens_details:
            input_cache = prompt_tokens_details.get("cached_tokens", 0)
            if input_cache != 0:
                units["text_cache_read"] = Units(input=input_cache, output=0)

        input = _PayiInstrumentor.update_for_vision(input - input_cache, units, self._estimated_prompt_tokens)

        units["text"] = Units(input=input, output=output)

    @staticmethod
    def has_image_and_get_texts(encoding: tiktoken.Encoding, content: Union[str, 'list[Any]'], image_type: str, text_type: str) -> 'tuple[bool, int]':
        if isinstance(content, list): # type: ignore
            has_image = any(item.get("type", "") == image_type for item in content)
            if has_image is False:
                return has_image, 0
            
            token_count = sum(len(encoding.encode(item.get("text", ""))) for item in content if item.get("type") == text_type)
            return has_image, token_count
        return False, 0

    @staticmethod
    def post_process_request_prompt(content: Union[str, 'list[Any]'], image_type: str, url_subkey: bool) -> bool:
        modified = False
        if isinstance(content, list): # type: ignore
            for item in content:
                type = item.get("type", "")
                if type != image_type:
                    continue

                if url_subkey:
                    url = item.get("image_url", {}).get("url", "")
                    if url.startswith("data:"):
                        item["image_url"]["url"] = _PayiInstrumentor._not_instrumented
                        modified = True
                else:
                    url = item.get("image_url", "")
                    if url.startswith("data:"):
                        item["image_url"] = _PayiInstrumentor._not_instrumented
                        modified = True

        return modified

class _OpenAiEmbeddingsProviderRequest(_OpenAiProviderRequest):
    def __init__(self, instrumentor: _PayiInstrumentor):
        super().__init__(
            instrumentor=instrumentor,
            input_tokens_key=_OpenAiProviderRequest.chat_input_tokens_key,
            output_tokens_key=_OpenAiProviderRequest.chat_output_tokens_key,
            input_tokens_details_key=_OpenAiProviderRequest.chat_input_tokens_details_key)

    @override
    def process_synchronous_response(
        self,
        response: Any,
        log_prompt_and_response: bool,
        kwargs: Any) -> Any:
        return self.process_synchronous_response_worker(response, log_prompt_and_response)

class _OpenAiChatProviderRequest(_OpenAiProviderRequest):
    def __init__(self, instrumentor: _PayiInstrumentor):
        super().__init__(
            instrumentor=instrumentor,
            input_tokens_key=_OpenAiProviderRequest.chat_input_tokens_key,
            output_tokens_key=_OpenAiProviderRequest.chat_output_tokens_key,
            input_tokens_details_key=_OpenAiProviderRequest.chat_input_tokens_details_key)

        self._include_usage_added = False

    @override
    def process_chunk(self, chunk: Any) -> _ChunkResult:
        ingest = False
        model = model_to_dict(chunk)
        
        if "provider_response_id" not in self._ingest:
            response_id = model.get("id", None)
            if response_id:
                self._ingest["provider_response_id"] = response_id

        send_chunk_to_client = True

        choices = model.get("choices", [])
        if choices:
            for choice in choices:
                function = choice.get("delta", {}).get("function_call", {})
                index = choice.get("index", None)

                if function and index is not None:
                    name = function.get("name", None)
                    arguments = function.get("arguments", None)

                    if name or arguments:
                        self.add_streaming_function_call(index=index, name=name, arguments=arguments)

        usage = model.get("usage")
        if usage:
            self.add_usage_units(usage)

            # If we added "include_usage" in the request on behalf of the client, do not return the extra 
            # packet which contains the usage to the client as they are not expecting the data
            if self._include_usage_added:
                send_chunk_to_client = False
            ingest = True

        return _ChunkResult(send_chunk_to_caller=send_chunk_to_client, ingest=ingest)

    @override
    def process_request(self, instance: Any, extra_headers: 'dict[str, str]', args: Sequence[Any], kwargs: Any) -> bool:
        result = super().process_request(instance, extra_headers, args, kwargs)
        if result is False:
            return result
        
        messages = kwargs.get("messages", None)
        if messages:
            estimated_token_count = 0 
            has_image = False
            enc: Optional[tiktoken.Encoding] = None

            try: 
                enc = tiktoken.encoding_for_model(kwargs.get("model")) # type: ignore
            except Exception:
                try:
                    enc = tiktoken.get_encoding("o200k_base") # type: ignore
                except Exception:
                    self._instrumentor._logger.info("OpenAI skipping vision token calc, could not load o200k_base")
                    enc = None
            
            if enc:
                for message in messages:
                    msg_has_image, msg_prompt_tokens = self.has_image_and_get_texts(enc, message.get('content', ''), image_type="image_url", text_type="text")
                    if msg_has_image:
                        has_image = True
                        estimated_token_count += msg_prompt_tokens
            
                if has_image and estimated_token_count > 0:
                    self._estimated_prompt_tokens = estimated_token_count

            stream: bool = kwargs.get("stream", False)
            if stream:
                add_include_usage = True

                stream_options: dict[str, Any] = kwargs.get("stream_options", None)
                if stream_options and "include_usage" in stream_options:
                    add_include_usage = stream_options["include_usage"] == False

                if add_include_usage:
                    kwargs['stream_options'] = {"include_usage": True}
                    self._include_usage_added = True
        return True

    @override
    def remove_inline_data(self, prompt: 'dict[str, Any]') -> bool:
        messages = prompt.get("messages", None)
        if not messages:
            return False
        return self.post_process_request_prompt(messages, image_type="image_url", url_subkey=True)

    @override
    def process_synchronous_response(
        self,
        response: Any,
        log_prompt_and_response: bool,
        kwargs: Any) -> Any:

        response_dict = model_to_dict(response)
        choices = response_dict.get("choices", [])
        if choices:
            for choice in choices:
                function = choice.get("message", {}).get("function_call", {})

                if not function:
                    continue

                name = function.get("name", None)
                arguments = function.get("arguments", None)

                if name:
                    self.add_synchronous_function_call(name=name, arguments=arguments)

        return self.process_synchronous_response_worker(response, log_prompt_and_response)

class _OpenAiResponsesProviderRequest(_OpenAiProviderRequest):
    def __init__(self, instrumentor: _PayiInstrumentor):
        super().__init__(
            instrumentor=instrumentor,
            input_tokens_key=_OpenAiProviderRequest.responses_input_tokens_key,
            output_tokens_key=_OpenAiProviderRequest.responses_output_tokens_key,
            input_tokens_details_key=_OpenAiProviderRequest.responses_input_tokens_details_key)

    @override
    def process_chunk(self, chunk: Any) -> _ChunkResult:
        ingest = False
        model = model_to_dict(chunk)
        response: dict[str, Any] = model.get("response", {})

        if "provider_response_id" not in self._ingest:
            response_id = response.get("id", None)
            if response_id:
                self._ingest["provider_response_id"] = response_id

        type = model.get("type", "")
        if type and type == "response.output_item.done":
            item = model.get("item", {})
            if item and item.get("type", "") == "function_call":
                name = item.get("name", None)
                arguments = item.get("arguments", None)

                if name:
                    self.add_synchronous_function_call(name=name, arguments=arguments)

        usage = response.get("usage")
        if usage:
            self.add_usage_units(usage)
            ingest = True

        return _ChunkResult(send_chunk_to_caller=True, ingest=ingest)

    @override
    def process_request(self, instance: Any, extra_headers: 'dict[str, str]', args: Sequence[Any], kwargs: Any) -> bool:
        result = super().process_request(instance, extra_headers, args, kwargs)
        if result is False:
            return result
        
        input: ResponseInputParam  = kwargs.get("input", None) # type: ignore
        if not input or isinstance(input, str) or not isinstance(input, list):
            return True
        
        estimated_token_count = 0 
        has_image = False
        enc: Optional[tiktoken.Encoding] = None

        try: 
            enc = tiktoken.encoding_for_model(kwargs.get("model")) # type: ignore
        except Exception:
            try:
                enc = tiktoken.get_encoding("o200k_base") # type: ignore
            except Exception:
                self._instrumentor._logger.info("OpenAI skipping vision token calc, could not load o200k_base")
                enc = None
        
        # find each content..type="input_text" and count tokens
        # input=[{
        #     "role": "user",
        #     "content": [
        #         {
        #             "type": "input_text",
        #             "text": "what's in this image?"
        #         },
        #         {
        #             "type": "input_image",
        #             "image_url": ... 
        #         },
        #     ],
        # }]
        if enc:
            for item in input: # type: ignore
                if isinstance(item, dict):
                    for key, value in item.items(): # type: ignore
                        if key == "content":
                            if isinstance(value, list):
                                msg_has_image, msg_prompt_tokens = self.has_image_and_get_texts(enc, value, image_type="input_image", text_type="input_text") # type: ignore 
                                if msg_has_image:
                                    has_image = True
                                    estimated_token_count += msg_prompt_tokens

            if has_image and estimated_token_count > 0:
                self._estimated_prompt_tokens = estimated_token_count

        return True

    @override
    def remove_inline_data(self, prompt: 'dict[str, Any]') -> bool:
        modified = False
        input = prompt.get("input", [])
        for item in input:
            if not isinstance(item, dict):
                continue

            for key, value in item.items(): # type: ignore
                if key == "content":
                    if isinstance(value, list):
                        modified = self.post_process_request_prompt(value, image_type="input_image", url_subkey=False) | modified # type: ignore

        return modified

    @override
    def process_synchronous_response(
        self,
        response: Any,
        log_prompt_and_response: bool,
        kwargs: Any) -> Any:

        response_dict = model_to_dict(response)
        output = response_dict.get("output", [])
        if output:
            for o in output:
                type = o.get("type", "")
                if type != "function_call":
                    continue

                name = o.get("name", None)
                arguments = o.get("arguments", None)

                if name:
                    self.add_synchronous_function_call(name=name, arguments=arguments)

        return self.process_synchronous_response_worker(response, log_prompt_and_response)

def model_to_dict(model: Any) -> Any:
    if version("pydantic") < "2.0.0":
        return model.dict()
    if hasattr(model, "model_dump"):
        return model.model_dump()
    elif hasattr(model, "parse"):  # Raw API response
        return model_to_dict(model.parse())
    else:
        return model        