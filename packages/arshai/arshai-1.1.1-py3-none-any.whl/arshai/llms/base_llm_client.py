"""
Base LLM Client implementation - Version 2.

Provides a comprehensive framework-standardized base class that serves as the 
contributor's guide for implementing new LLM providers. Handles all framework 
requirements including dual interface support, function calling, background tasks,
structured output, and usage tracking.

This is the template that all LLM providers should inherit from.
"""

import asyncio
import logging
import traceback
import warnings
from abc import ABC, abstractmethod
from typing import Dict, Any, TypeVar, Union, AsyncGenerator, List, Type, Optional, Callable

from arshai.core.interfaces.illm import ILLM, ILLMConfig, ILLMInput
from arshai.llms.utils.function_execution import FunctionOrchestrator, FunctionExecutionInput, FunctionCall, StreamingExecutionState

# Type checking imports for observability
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from arshai.observability import ObservabilityManager

T = TypeVar("T")


class BaseLLMClient(ILLM, ABC):
    """
    Framework-standardized base class for all LLM clients.
    
    This class serves as the contributor's guide and template for implementing
    new LLM providers. It handles all framework requirements while requiring
    providers to implement only their specific API integration methods.
    
    Framework Features Handled by Base Class:
    - Dual interface support (old + new methods with deprecation)
    - Function calling orchestration (regular + background tasks)  
    - Structured output handling
    - Usage tracking standardization
    - Error handling and resilience
    - Routing logic between simple and complex cases
    
    What Contributors Need to Implement:
    - Provider-specific API client initialization
    - Provider-specific chat/stream methods
    - Provider-specific format conversions
    """

    def __init__(self, config: ILLMConfig, observability_manager: Optional['ObservabilityManager'] = None):
        """
        Initialize the base LLM client with framework infrastructure.
        
        Args:
            config: LLM configuration
            observability_manager: Optional observability manager for metrics collection
        """
        self.config = config
        self.observability_manager = observability_manager
        self.logger = logging.getLogger(self.__class__.__name__)

        # Framework infrastructure
        self._function_orchestrator = FunctionOrchestrator()

        self.logger.info(f"Initializing {self.__class__.__name__} with model: {self.config.model}")
        if observability_manager:
            self.logger.info(f"Observability enabled for {self._get_provider_name()}")

        # Initialize the provider-specific client
        self._client = self._initialize_client()

    # ========================================================================
    # ABSTRACT METHODS - What contributors must implement
    # ========================================================================

    @abstractmethod
    def _initialize_client(self) -> Any:
        """
        Initialize the LLM provider client.
        
        Returns:
            Provider-specific client instance
        """
        pass

    @abstractmethod
    def _convert_callables_to_provider_format(self, functions: Dict[str, Callable]) -> Any:
        """
        Convert python callables to provider-specific function declarations.
        Pure conversion without execution metadata.
        
        Each provider must implement this to convert callables to their
        specific format (OpenAI tools, Gemini FunctionDeclarations, etc.)
        
        Args:
            functions: Dictionary of callable functions to convert
            
        Returns:
            Provider-specific function declarations format
        """
        pass

    @abstractmethod
    async def _chat_simple(self, input: ILLMInput) -> Dict[str, Any]:
        """
        Handle simple chat without tools or background tasks.
        
        Args:
            input: LLM input with system_prompt, user_message, optional structure_type
            
        Returns:
            Dict with 'llm_response' and 'usage' keys
        """
        pass

    @abstractmethod
    async def _chat_with_functions(self, input: ILLMInput) -> Dict[str, Any]:
        """
        Handle complex chat with tools and/or background tasks.
        
        Args:
            input: LLM input with regular_functions, background_tasks
            
        Returns:
            Dict with 'llm_response' and 'usage' keys
        """
        pass

    @abstractmethod
    async def _stream_simple(self, input: ILLMInput) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Handle simple streaming without tools or background tasks.
        
        Args:
            input: LLM input with system_prompt, user_message, optional structure_type
            
        Yields:
            Dict with 'llm_response' and optional 'usage' keys
        """
        pass

    @abstractmethod
    async def _stream_with_functions(self, input: ILLMInput) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Handle complex streaming with tools and/or background tasks.
        
        Args:
            input: LLM input with regular_functions, background_tasks
            
        Yields:
            Dict with 'llm_response' and optional 'usage' keys
        """
        pass

    # ========================================================================
    # FRAMEWORK HELPER METHODS - Available to all providers
    # ========================================================================

    def _needs_function_calling(self, input: ILLMInput) -> bool:
        """
        Determine if function calling is needed based on input.
        
        Framework-standardized logic that all providers should use.
        
        Args:
            input: The LLM input to evaluate
            
        Returns:
            True if function calling (regular functions or background tasks) is needed
        """
        has_regular_functions = input.regular_functions and len(input.regular_functions) > 0
        has_background_tasks = input.background_tasks and len(input.background_tasks) > 0
        return has_regular_functions or has_background_tasks

    def _has_structured_output(self, input: ILLMInput) -> bool:
        """
        Check if structured output is requested.
        
        Args:
            input: The LLM input to evaluate
            
        Returns:
            True if structure_type is specified
        """
        return input.structure_type is not None

    async def _execute_functions_with_orchestrator(
        self,
        execution_input_or_legacy: Union[FunctionExecutionInput, Dict[str, Any]],
        regular_args: Dict[str, Dict[str, Any]] = None,
        background_tasks: Dict[str, Any] = None,
        background_args: Dict[str, Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute functions using the framework's standardized orchestrator.
        
        Supports both new object-based approach and legacy dictionary approach for backward compatibility.
        
        Args:
            execution_input_or_legacy: Either FunctionExecutionInput (new) or regular_functions dict (legacy)
            regular_args: Dict of arguments for regular functions (legacy only)
            background_tasks: Dict of background task functions (legacy only) 
            background_args: Dict of arguments for background tasks (legacy only)
            
        Returns:
            Orchestrator execution result in generic format
        """
        # Check if we're using the new object-based approach
        if isinstance(execution_input_or_legacy, FunctionExecutionInput):
            # New object-based approach
            execution_input = execution_input_or_legacy
        else:
            # Legacy dictionary approach - convert to new format
            regular_functions = execution_input_or_legacy
            execution_input = FunctionExecutionInput(
                function_calls=[],  # Will be populated below
                available_functions=regular_functions,
                available_background_tasks=background_tasks or {}
            )
            
            # Convert dictionaries to FunctionCall objects
            function_calls = []
            
            # Convert regular functions
            for name, func in regular_functions.items():
                args = regular_args.get(name, {}) if regular_args else {}
                function_calls.append(FunctionCall(
                    name=name,
                    args=args,
                    is_background=False
                ))
            
            # Convert background tasks
            if background_tasks:
                for name, func in background_tasks.items():
                    args = background_args.get(name, {}) if background_args else {}
                    function_calls.append(FunctionCall(
                        name=name,
                        args=args,
                        is_background=True
                    ))
            
            execution_input.function_calls = function_calls
        
        result = await self._function_orchestrator.execute_functions(execution_input)
        
        # Convert to dict format for easier handling by providers
        return {
            "regular_results": result.regular_results,
            "background_initiated": result.background_initiated,
            "failed_functions": result.failed_functions
        }

    def _standardize_usage_metadata(self, raw_usage: Any, provider: str, model: str, request_id: str = None) -> Dict[str, Any]:
        """
        Standardize usage metadata to framework format.
        
        Framework-standardized usage format that all providers should return.
        
        Args:
            raw_usage: Provider-specific usage metadata
            provider: Provider name (e.g., "openai", "gemini")
            model: Model name used
            request_id: Optional request ID from provider
            
        Returns:
            Standardized usage metadata dict
        """
        if not raw_usage:
            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "thinking_tokens": 0,
                "tool_calling_tokens": 0,
                "provider": provider,
                "model": model,
                "request_id": request_id
            }

        # Extract standard fields (providers should override this method if needed)
        input_tokens = getattr(raw_usage, 'prompt_tokens', 0) or getattr(raw_usage, 'input_tokens', 0)
        output_tokens = getattr(raw_usage, 'completion_tokens', 0) or getattr(raw_usage, 'output_tokens', 0)
        total_tokens = getattr(raw_usage, 'total_tokens', input_tokens + output_tokens)
        
        # Optional advanced fields
        thinking_tokens = getattr(raw_usage, 'reasoning_tokens', 0) or getattr(raw_usage, 'thinking_tokens', 0)
        tool_calling_tokens = getattr(raw_usage, 'tool_calling_tokens', 0) or getattr(raw_usage, 'function_call_tokens', 0)

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "thinking_tokens": thinking_tokens,
            "tool_calling_tokens": tool_calling_tokens,
            "provider": provider,
            "model": model,
            "request_id": request_id
        }

    def _get_provider_name(self) -> str:
        """Get the provider name for logging and usage tracking."""
        return self.__class__.__name__.replace("Client", "").lower()

    # ========================================================================
    # PUBLIC INTERFACE - NEW METHODS (Framework Standard)
    # ========================================================================

    async def chat(self, input: ILLMInput) -> Dict[str, Any]:
        """
        Process a chat message with optional tools, background tasks, and structured output.
        
        This is the main chat method that handles all cases. Framework handles
        routing to appropriate provider-specific methods and observability integration.

        Args:
            input: The LLM input containing system prompt, user message, tools, and options

        Returns:
            Dict containing 'llm_response' and 'usage' keys
        """
        if self.observability_manager:
            async with self.observability_manager.observe_llm_call(
                self._get_provider_name(),
                self.config.model,
                "chat"
            ) as timing_data:
                # Capture input content for Phoenix display (respecting privacy controls)
                if self.observability_manager.config.log_prompts:
                    prompt_content = f"System: {input.system_prompt}\nUser: {input.user_message}"
                    # Truncate if needed
                    if len(prompt_content) > self.observability_manager.config.max_prompt_length:
                        prompt_content = prompt_content[:self.observability_manager.config.max_prompt_length] + "..."
                    timing_data.input_value = prompt_content
                    timing_data.input_mime_type = "text/plain"
                    timing_data.input_messages = [
                        {"role": "system", "content": input.system_prompt},
                        {"role": "user", "content": input.user_message}
                    ]
                
                result = await self._execute_chat(input)
                
                # Capture output content for Phoenix display (respecting privacy controls)
                if 'llm_response' in result and self.observability_manager.config.log_responses:
                    response_content = result['llm_response']
                    # Truncate if needed
                    if len(response_content) > self.observability_manager.config.max_response_length:
                        response_content = response_content[:self.observability_manager.config.max_response_length] + "..."
                    timing_data.output_value = response_content
                    timing_data.output_mime_type = "text/plain"
                    timing_data.output_messages = [
                        {"role": "assistant", "content": response_content}
                    ]
                
                # Record token timing - for non-streaming, we record completion timing
                timing_data.record_token()
                
                # Record usage data if available
                if 'usage' in result:
                    self.logger.debug(f"Usage: {result['usage']}")
                    await self.observability_manager.record_usage_data(timing_data, result['usage'])
                    
                self.logger.debug(f"Timing Data: {timing_data}")
                return result
        else:
            return await self._execute_chat(input)

    async def _execute_chat(self, input: ILLMInput) -> Dict[str, Any]:
        """
        Execute chat logic without observability (current chat() implementation).
        
        Args:
            input: The LLM input containing system prompt, user message, tools, and options

        Returns:
            Dict containing 'llm_response' and 'usage' keys
        """
        try:
            self.logger.info(f"Processing chat request - Regular Functions: {bool(input.regular_functions)}, "
                           f"Background: {bool(input.background_tasks)}, "
                           f"Structured: {bool(input.structure_type)}")

            # Route to appropriate handler based on function calling needs
            if self._needs_function_calling(input):
                return await self._chat_with_functions(input)
            else:
                return await self._chat_simple(input)

        except Exception as e:
            self.logger.error(f"Error in {self.__class__.__name__} chat: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "llm_response": f"An error occurred: {str(e)}", 
                "usage": self._standardize_usage_metadata(None, self._get_provider_name(), self.config.model)
            }

    async def stream(self, input: ILLMInput) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a streaming chat message with optional tools, background tasks, and structured output.
        
        This is the main streaming method that handles all cases. Framework handles
        routing to appropriate provider-specific methods and observability integration.

        Args:
            input: The LLM input containing system prompt, user message, tools, and options

        Yields:
            Dict containing 'llm_response' and optional 'usage' keys
        """
        if self.observability_manager:
            async with self.observability_manager.observe_streaming_llm_call(
                self._get_provider_name(),
                self.config.model,
                "stream"
            ) as timing_data:
                # Capture input content for Phoenix display (respecting privacy controls)
                if self.observability_manager.config.log_prompts:
                    prompt_content = f"System: {input.system_prompt}\nUser: {input.user_message}"
                    # Truncate if needed
                    if len(prompt_content) > self.observability_manager.config.max_prompt_length:
                        prompt_content = prompt_content[:self.observability_manager.config.max_prompt_length] + "..."
                    timing_data.input_value = prompt_content
                    timing_data.input_mime_type = "text/plain"
                    timing_data.input_messages = [
                        {"role": "system", "content": input.system_prompt},
                        {"role": "user", "content": input.user_message}
                    ]
                
                first_token_recorded = False
                accumulated_response = ""
                
                async for chunk in self._execute_stream(input):
                    # Record first token timing - simple approach like decorators
                    if not first_token_recorded:
                        timing_data.record_first_token()
                        first_token_recorded = True
                    
                    # Record each token - every chunk represents token generation progress
                    timing_data.record_token()
                    
                    # Accumulate streaming response content for Phoenix display
                    if 'llm_response' in chunk and chunk['llm_response']:
                        accumulated_response += chunk['llm_response']
                    
                    # Extract usage data directly from chunk (we know our own structure)
                    if 'usage' in chunk and chunk['usage']:
                        await self.observability_manager.record_usage_data(timing_data, chunk['usage'])
                    
                    yield chunk
                
                # Capture final output content for Phoenix display (respecting privacy controls)
                if accumulated_response and self.observability_manager.config.log_responses:
                    response_content = accumulated_response
                    # Truncate if needed
                    if len(response_content) > self.observability_manager.config.max_response_length:
                        response_content = response_content[:self.observability_manager.config.max_response_length] + "..."
                    timing_data.output_value = response_content
                    timing_data.output_mime_type = "text/plain"
                    timing_data.output_messages = [
                        {"role": "assistant", "content": response_content}
                    ]
                    
                # Record final timing if we had tokens
                if first_token_recorded:
                    timing_data.record_token()
        else:
            async for chunk in self._execute_stream(input):
                yield chunk

    async def _execute_stream(self, input: ILLMInput) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute streaming logic without observability (current stream() implementation).
        
        Args:
            input: The LLM input containing system prompt, user message, tools, and options

        Yields:
            Dict containing 'llm_response' and optional 'usage' keys
        """
        try:
            self.logger.info(f"Processing stream request - Regular Functions: {bool(input.regular_functions)}, "
                           f"Background: {bool(input.background_tasks)}, "
                           f"Structured: {bool(input.structure_type)}")

            if self._needs_function_calling(input):
                async for chunk in self._stream_with_functions(input):
                    yield chunk
            else:
                async for chunk in self._stream_simple(input):
                    yield chunk

        except Exception as e:
            self.logger.error(f"Error in {self.__class__.__name__} stream: {str(e)}")
            self.logger.error(traceback.format_exc())
            yield {
                "llm_response": f"An error occurred: {str(e)}", 
                "usage": self._standardize_usage_metadata(None, self._get_provider_name(), self.config.model)
            }

    # ========================================================================
    # PUBLIC INTERFACE - DEPRECATED METHODS (Backward Compatibility)
    # ========================================================================

    async def chat_with_tools(self, input: ILLMInput) -> Union[Dict[str, Any], str]:
        """
        DEPRECATED: Use chat() instead.
        
        Process a chat message with tools. Maintained for backward compatibility.
        
        Args:
            input: The LLM input
            
        Returns:
            Chat response (same format as chat() method)
        """
        warnings.warn(
            "chat_with_tools() is deprecated and will be removed in 2026. Use chat() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        result = await self.chat(input)
        
        # For backward compatibility, some old code might expect string responses on error
        if isinstance(result.get("llm_response"), str) and "error occurred" in result.get("llm_response", "").lower():
            return result["llm_response"]
            
        return result

    async def stream_with_tools(self, input: ILLMInput) -> AsyncGenerator[Dict[str, Any], None]:
        """
        DEPRECATED: Use stream() instead.
        
        Process a streaming chat message with tools. Maintained for backward compatibility.
        
        Args:
            input: The LLM input
            
        Yields:
            Stream response (same format as stream() method)
        """
        warnings.warn(
            "stream_with_tools() is deprecated and will be removed in 2026. Use stream() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        async for chunk in self.stream(input):
            yield chunk

    async def chat_completion(self, input: ILLMInput) -> Union[Dict[str, Any], str]:
        """
        DEPRECATED: Use chat() instead.
        
        Chat completion method. Maintained for backward compatibility.
        
        Args:
            input: The LLM input
            
        Returns:
            Chat response (same format as chat() method)
        """
        warnings.warn(
            "chat_completion() is deprecated and will be removed in 2026. Use chat() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        result = await self.chat(input)
        
        # For backward compatibility, some old code might expect string responses on error
        if isinstance(result.get("llm_response"), str) and "error occurred" in result.get("llm_response", "").lower():
            return result["llm_response"]
            
        return result

    async def stream_completion(self, input: ILLMInput) -> AsyncGenerator[Dict[str, Any], None]:
        """
        DEPRECATED: Use stream() instead.
        
        Streaming completion method. Maintained for backward compatibility.
        
        Args:
            input: The LLM input
            
        Yields:
            Stream response (same format as stream() method)
        """
        warnings.warn(
            "stream_completion() is deprecated and will be removed in 2026. Use stream() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        async for chunk in self.stream(input):
            yield chunk

    # ========================================================================
    # UTILITY METHODS - Available to all providers
    # ========================================================================

    def _log_provider_info(self, message: str):
        """Log provider-specific information."""
        self.logger.info(f"[{self._get_provider_name()}] {message}")

    def _log_provider_debug(self, message: str):
        """Log provider-specific debug information."""
        self.logger.debug(f"[{self._get_provider_name()}] {message}")

    def _log_provider_error(self, message: str):
        """Log provider-specific error information."""
        self.logger.error(f"[{self._get_provider_name()}] {message}")

    def get_active_background_tasks_count(self) -> int:
        """
        Get the number of currently active background tasks.
        
        Returns:
            Number of active background tasks
        """
        return self._function_orchestrator.get_active_background_tasks_count()

    async def wait_for_background_tasks(self, timeout: float = None) -> None:
        """
        Wait for all background tasks to complete (useful for testing).
        
        Args:
            timeout: Maximum time to wait in seconds
        """
        await self._function_orchestrator.wait_for_background_tasks(timeout)

    # ========================================================================
    # PROGRESSIVE STREAMING METHODS (NEW) - Available to all providers  
    # ========================================================================
    
    def _is_function_complete(self, function_data: Dict[str, Any]) -> bool:
        """
        Check if function is complete and ready for execution during streaming.
        
        Uses JSON validation to determine if function arguments are complete.
        This approach is universal across all providers.
        
        Args:
            function_data: Function data with name and arguments
            
        Returns:
            True if function is complete and ready for execution
        """
        # Basic requirements check (minimum safety)
        if not (function_data.get("name") and "arguments" in function_data):
            return False
        
        try:
            import json
            if isinstance(function_data["arguments"], str):
                 json.loads(function_data["arguments"])  # Valid JSON = complete
                 return True
            elif isinstance(function_data["arguments"], dict):
                  return True  # Already parsed = complete
        except json.JSONDecodeError:
              return False  # Still streaming arguments
        return False
    
    async def _execute_function_progressively(
        self,
        function_call: FunctionCall,
        input: ILLMInput
    ) -> asyncio.Task:
        """
        Execute a single function progressively and return the task.
        
        This method enables real-time function execution during streaming,
        providing better user experience and resource utilization.
        
        Args:
            function_call: The function call to execute
            input: The LLM input containing available functions
            
        Returns:
            asyncio.Task that can be awaited later for the result
        """
        return await self._function_orchestrator.execute_function_progressively(
            function_call,
            input.regular_functions or {},
            input.background_tasks or {}
        )
    
    async def _gather_progressive_results(self, function_tasks: List[asyncio.Task]) -> Dict[str, Any]:
        """
        Gather results from progressively executed functions.
        
        Args:
            function_tasks: List of tasks from progressive execution
            
        Returns:
            Dict containing consolidated results in standardized format
        """
        try:
            result = await self._function_orchestrator.gather_progressive_results(function_tasks)
            
            # Convert to dict format for provider compatibility
            return {
                "regular_results": result.regular_results,
                "background_initiated": result.background_initiated,
                "failed_functions": result.failed_functions
            }
        except Exception as e:
            self.logger.error(f"Progressive function gathering failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "regular_results": [],
                "background_initiated": [],
                "failed_functions": [{
                    "name": "gather_error",
                    "args": {},
                    "error": str(e),
                    "call_id": None
                }]
            }
    
    def _add_failed_functions_to_context(self, failed_functions: List[Dict[str, Any]], contents: List[str]):
        """
        Add failed function context messages for the model with safeguards.
        
        This helps the model understand what went wrong and provide
        appropriate fallback responses or error handling.
        
        Includes safeguards for:
        - Duplicate message prevention
        - Context length limits
        - Message truncation for large arguments
        
        Args:
            failed_functions: List of failed function results
            contents: Contents list to add context messages to
        """
        if not failed_functions:
            return
        
        # Track added messages to prevent duplicates
        added_messages = set()
        max_context_messages = 10  # Limit context bloat
        max_arg_length = 200  # Truncate long arguments
        
        messages_added = 0
        for failed in failed_functions:
            if messages_added >= max_context_messages:
                self.logger.info(f"Reached maximum context messages limit ({max_context_messages}), skipping remaining failures")
                break
            
            # Create unique key for deduplication
            failure_key = f"{failed['name']}_{failed.get('call_id', 'no_id')}"
            if failure_key in added_messages:
                continue  # Skip duplicate
            
            # Truncate arguments if too long
            args_str = str(failed['args'])
            if len(args_str) > max_arg_length:
                args_str = args_str[:max_arg_length] + "... (truncated)"
            
            # Truncate error message if too long
            error_str = str(failed['error'])
            if len(error_str) > max_arg_length:
                error_str = error_str[:max_arg_length] + "... (truncated)"
            
            context_msg = (
                f"Function '{failed['name']}' called with arguments {args_str} "
                f"failed with error: {error_str}. Please handle this gracefully "
                f"and provide an appropriate response or fallback."
            )
            
            contents.append(context_msg)
            added_messages.add(failure_key)
            messages_added += 1
            
            self.logger.warning(f"Added failure context for {failed['name']}: {error_str[:100]}{'...' if len(str(failed['error'])) > 100 else ''}")
        
        if messages_added > 0:
            self.logger.info(f"Added {messages_added} failure context messages to conversation")