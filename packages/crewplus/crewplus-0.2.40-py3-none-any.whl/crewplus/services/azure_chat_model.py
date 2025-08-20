import os
import logging
from typing import Any, Optional

from langchain_openai.chat_models.azure import AzureChatOpenAI
from pydantic import Field
from .tracing_manager import TracingManager, TracingContext

class TracedAzureChatOpenAI(AzureChatOpenAI):
    """
    Wrapper for AzureChatOpenAI that integrates with tracing services like Langfuse.
    
    This class automatically handles callback integration, making it easier
    to trace and debug your interactions with the Azure OpenAI service.

    **Tracing Integration (e.g., Langfuse):**
    Tracing is automatically enabled when the respective environment variables are set.
    For Langfuse:
    - LANGFUSE_PUBLIC_KEY: Your Langfuse public key
    - LANGFUSE_SECRET_KEY: Your Langfuse secret key  
    - LANGFUSE_HOST: Langfuse host URL (optional, defaults to https://cloud.langfuse.com)
    
    You can explicitly control this with the `enable_tracing` parameter or disable
    it for specific calls by adding `{"metadata": {"tracing_disabled": True}}`
    to the `config` argument.

    Attributes:
        logger (Optional[logging.Logger]): An optional logger instance.
        enable_tracing (Optional[bool]): Enable/disable tracing (auto-detect if None).

    Example:
        .. code-block:: python

            # Set Langfuse environment variables (optional)
            import os
            os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."
            os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."

            from crewplus.services.azure_chat_model import TracedAzureChatOpenAI
            from langchain_core.messages import HumanMessage

            # Initialize the model
            model = TracedAzureChatOpenAI(
                azure_deployment="your-deployment",
                api_version="2024-05-01-preview",
            )

            # --- Text-only usage (automatically traced if env vars set) ---
            response = model.invoke("Hello, how are you?")
            print("Text response:", response.content)

            # --- Tracing with session/user tracking (for Langfuse) ---
            response = model.invoke(
                "What is AI?",
                config={
                    "metadata": {
                        "langfuse_session_id": "chat-session-123",
                        "user_id": "user-456"
                    }
                }
            )
            
            # --- Disable tracing for a specific call ---
            response = model.invoke(
                "Hello without tracing",
                config={"metadata": {"tracing_disabled": True}}
            )

            # --- Asynchronous Streaming Usage ---
            import asyncio
            from langchain_core.messages import HumanMessage

            async def main():
                messages = [HumanMessage(content="Tell me a short story about a brave robot.")]
                print("\nAsync Streaming response:")
                async for chunk in model.astream(messages):
                    print(chunk.content, end="", flush=True)
                print()

            # In a real application, you would run this with:
            # asyncio.run(main())
    """
    logger: Optional[logging.Logger] = Field(default=None, description="Optional logger instance", exclude=True)
    enable_tracing: Optional[bool] = Field(default=None, description="Enable tracing (auto-detect if None)")
    
    _tracing_manager: Optional[TracingManager] = None

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        
        # Initialize logger
        if self.logger is None:
            self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
            if not self.logger.handlers:
                self.logger.addHandler(logging.StreamHandler())
                self.logger.setLevel(logging.INFO)
        
        self._tracing_manager = TracingManager(self)

    def get_model_identifier(self) -> str:
        """Return a string identifying this model for tracing and logging."""
        return f"{self.__class__.__name__} (deployment='{self.deployment_name}')"

    def invoke(self, input, config=None, **kwargs):
        config = self._tracing_manager.add_callbacks_to_config(config)
        return super().invoke(input, config=config, **kwargs)

    async def ainvoke(self, input, config=None, **kwargs):
        config = self._tracing_manager.add_callbacks_to_config(config)
        return await super().ainvoke(input, config=config, **kwargs)

    def stream(self, input, config=None, **kwargs):
        # Add stream_options to get usage data for Langfuse
        stream_options = kwargs.get("stream_options", {})
        stream_options["include_usage"] = True
        kwargs["stream_options"] = stream_options
        
        config = self._tracing_manager.add_callbacks_to_config(config)
        yield from super().stream(input, config=config, **kwargs)

    async def astream(self, input, config=None, **kwargs) :
        # Add stream_options to get usage data for Langfuse
        stream_options = kwargs.get("stream_options", {})
        stream_options["include_usage"] = True
        kwargs["stream_options"] = stream_options
        
        config = self._tracing_manager.add_callbacks_to_config(config)
        async for chunk in super().astream(input, config=config, **kwargs):
            yield chunk
