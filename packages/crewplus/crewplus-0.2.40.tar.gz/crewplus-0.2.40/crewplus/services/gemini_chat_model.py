import os
import asyncio
import logging
from typing import Any, Dict, Iterator, List, Optional, AsyncIterator, Union, Tuple
from google import genai
from google.genai import types
from google.oauth2 import service_account
import base64
import requests
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.callbacks import (
    CallbackManagerForLLMRun,
    AsyncCallbackManagerForLLMRun
)
from pydantic import Field, SecretStr
from langchain_core.utils import convert_to_secret_str
from .tracing_manager import TracingManager, TracingContext

class GeminiChatModel(BaseChatModel):
    """Custom chat model for Google Gemini, supporting text, image, and video.
    
    This model provides a robust interface to Google's Gemini Pro and Flash models,
    handling various data formats for multimodal inputs while maintaining compatibility
    with the LangChain ecosystem.

    It supports standard invocation, streaming, and asynchronous operations.
    By default, it uses Google AI with an API key. It can also be configured to use
    Google Cloud Vertex AI.

    **Authentication:**
    - **Google AI (Default):** The `google_api_key` parameter or the `GOOGLE_API_KEY` 
      environment variable is used.
    - **Vertex AI:** To use Vertex AI, set `use_vertex_ai=True` and provide
      GCP configuration (`project_id`, `location`). Authentication is handled
      via `service_account_file`, `credentials`, or Application Default Credentials (ADC).

    **Tracing Integration:**
    Tracing (e.g., with Langfuse) is automatically enabled when the respective
    environment variables are set. For Langfuse:
    - LANGFUSE_PUBLIC_KEY: Your Langfuse public key
    - LANGFUSE_SECRET_KEY: Your Langfuse secret key  
    - LANGFUSE_HOST: Langfuse host URL (optional, defaults to https://cloud.langfuse.com)
    
    You can also configure it explicitly or disable it. Session and user tracking 
    can be set per call via metadata.

    Attributes:
        model_name (str): The Google model name to use (e.g., "gemini-1.5-flash").
        google_api_key (Optional[SecretStr]): Your Google API key.
        temperature (Optional[float]): The sampling temperature for generation.
        max_tokens (Optional[int]): The maximum number of tokens to generate.
        top_p (Optional[float]): The top-p (nucleus) sampling parameter.
        top_k (Optional[int]): The top-k sampling parameter.
        logger (Optional[logging.Logger]): An optional logger instance.
        enable_tracing (Optional[bool]): Enable/disable all tracing (auto-detect if None).
        use_vertex_ai (bool): If True, uses Vertex AI instead of Google AI Platform. Defaults to False.
        project_id (Optional[str]): GCP Project ID, required for Vertex AI.
        location (Optional[str]): GCP Location for Vertex AI (e.g., "us-central1").
        service_account_file (Optional[str]): Path to GCP service account JSON for Vertex AI.
        credentials (Optional[Any]): GCP credentials object for Vertex AI (alternative to file).

    Example:
        .. code-block:: python

            # Set Langfuse environment variables (optional)
            import os
            os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."
            os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."
            os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"  # EU region or self-hosted
            # os.environ["LANGFUSE_HOST"] = "https://us.cloud.langfuse.com"  # US region

            from crewplus.services import GeminiChatModel
            from langchain_core.messages import HumanMessage
            import base64
            import logging

            # Initialize the model with optional logger
            logger = logging.getLogger("my_app.gemini")
            model = GeminiChatModel(model_name="gemini-2.0-flash", logger=logger)

            # --- Text-only usage (automatically traced if env vars set) ---
            response = model.invoke("Hello, how are you?")
            print("Text response:", response.content)

            # --- Tracing with session/user tracking (for Langfuse) ---
            response = model.invoke(
                "What is AI?",
                config={
                    "metadata": {
                        "langfuse_session_id": "chat-session-123",
                        "langfuse_user_id": "user-456"
                    }
                }
            )

            # --- Image processing with base64 data URI ---
            # Replace with a path to your image
            image_path = "path/to/your/image.jpg"
            try:
                with open(image_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                
                image_message = HumanMessage(
                    content=[
                        {"type": "text", "text": "What is in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_string}"
                            }
                        },
                    ]
                )
                image_response = model.invoke([image_message])
                print("Image response (base64):", image_response.content)
            except FileNotFoundError:
                print(f"Image file not found at {image_path}, skipping base64 example.")


            # --- Image processing with URL ---
            url_message = HumanMessage(
                content=[
                    {"type": "text", "text": "Describe this image:"},
                    {
                        "type": "image_url",
                        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                    },
                ]
            )
            url_response = model.invoke([url_message])
            print("Image response (URL):", url_response.content)
            
            # --- Video processing with file path (>=20MB) ---
            video_path = "path/to/your/video.mp4"
            video_file = client.files.upload(file=video_path)

            try:
                video_message = HumanMessage(
                    content=[
                        {"type": "text", "text": "Summarize this video."},
                        {"type": "video_file", "file": video_file},
                    ]
                )
                video_response = model.invoke([video_message])
                print("Video response (file path):", video_response.content)
            except Exception as e:
                print(f"Video processing with file path failed: {e}")

            # --- Video processing with raw bytes (<20MB) ---
            video_path = "path/to/your/video.mp4"
            try:
                with open(video_path, "rb") as video_file:
                    video_bytes = video_file.read()
                
                video_message = HumanMessage(
                    content=[
                        {"type": "text", "text": "What is happening in this video?"},
                        {
                            "type": "video_file",
                            "data": video_bytes,
                            "mime_type": "video/mp4"
                        },
                    ]
                )
                video_response = model.invoke([video_message])
                print("Video response (bytes):", video_response.content)
            except FileNotFoundError:
                print(f"Video file not found at {video_path}, skipping bytes example.")
            except Exception as e:
                print(f"Video processing with bytes failed: {e}")
            
            # --- Streaming usage (works with text, images, and video) ---
            print("Streaming response:")
            for chunk in model.stream([url_message]):
                print(chunk.content, end="", flush=True)

            # --- Traditional Langfuse callback approach still works ---
            from langfuse.langchain import CallbackHandler
            langfuse_handler = CallbackHandler(
                session_id="session-123",
                user_id="user-456"
            )
            response = model.invoke(
                "Hello with manual callback",
                config={"callbacks": [langfuse_handler]}
            )

            # --- Disable Langfuse for specific calls ---
            response = model.invoke(
                "Hello without tracing",
                config={"metadata": {"tracing_disabled": True}}
            )

    Example (Vertex AI):
        .. code-block:: python

            # Assumes GCP environment is configured (e.g., gcloud auth application-default login)
            # or environment variables are set:
            # os.environ["GCP_PROJECT_ID"] = "your-gcp-project-id"
            # os.environ["GCP_LOCATION"] = "us-central1"
            # os.environ["GCP_SERVICE_ACCOUNT_FILE"] = "path/to/your/service-account-key.json"

            vertex_model = GeminiChatModel(
                model_name="gemini-1.5-flash-001",
                use_vertex_ai=True,
            )
            response = vertex_model.invoke("Hello from Vertex AI!")
            print(response.content)
    """
    
    # Model configuration
    model_name: str = Field(default="gemini-2.5-flash", description="The Google model name to use")
    google_api_key: Optional[SecretStr] = Field(default=None, description="Google API key")
    temperature: Optional[float] = Field(default=0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(default=None, description="Top-p sampling parameter")
    top_k: Optional[int] = Field(default=None, description="Top-k sampling parameter")
    
    # Vertex AI specific configuration
    use_vertex_ai: bool = Field(default=False, description="Use Vertex AI instead of Google AI Platform")
    project_id: Optional[str] = Field(default=None, description="Google Cloud Project ID for Vertex AI")
    location: Optional[str] = Field(default=None, description="Google Cloud Location for Vertex AI (e.g., 'us-central1')")
    service_account_file: Optional[str] = Field(default=None, description="Path to Google Cloud service account key file")
    credentials: Optional[Any] = Field(default=None, description="Google Cloud credentials object", exclude=True)

    # Configuration for tracing and logging
    logger: Optional[logging.Logger] = Field(default=None, description="Optional logger instance", exclude=True)
    enable_tracing: Optional[bool] = Field(default=None, description="Enable tracing (auto-detect if None)")
    
    # Internal clients and managers
    _client: Optional[genai.Client] = None
    _tracing_manager: Optional[TracingManager] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize logger
        if self.logger is None:
            self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
            if not self.logger.handlers:
                self.logger.addHandler(logging.StreamHandler())
                self.logger.setLevel(logging.INFO)
        
        self._initialize_client()
        
        self._tracing_manager = TracingManager(self)

    def _initialize_client(self):
        """Initializes the Google GenAI client for either Google AI or Vertex AI."""
        if self.use_vertex_ai:
            self._init_vertex_ai_client()
        else:
            self._init_google_ai_client()

    def _init_google_ai_client(self):
        """Initializes the client for Google AI Platform."""
        # Get API key from environment if not provided
        if self.google_api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                self.google_api_key = convert_to_secret_str(api_key)
        
        # Initialize the Google GenAI client
        if self.google_api_key:
            self._client = genai.Client(api_key=self.google_api_key.get_secret_value())
            self.logger.info(f"Initialized GeminiChatModel with model: {self.model_name} for Google AI")
        else:
            error_msg = "Google API key is required. Set GOOGLE_API_KEY environment variable or pass google_api_key parameter."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    def _init_vertex_ai_client(self):
        """Initializes the client for Vertex AI."""
        # Get config from environment if not provided
        if self.project_id is None:
            self.project_id = os.getenv("GCP_PROJECT_ID")
        if self.location is None:
            self.location = os.getenv("GCP_LOCATION")
        
        if not self.project_id or not self.location:
            error_msg = "For Vertex AI, 'project_id' and 'location' are required."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        creds = self.credentials
        if creds is None:
            # Get service account file from env if not provided
            sa_file = self.service_account_file or os.getenv("GCP_SERVICE_ACCOUNT_FILE")
            self.logger.debug(f"Service account file: {sa_file}")
            if sa_file:
                try:
                    creds = service_account.Credentials.from_service_account_file(
                        sa_file,
                        scopes=['https://www.googleapis.com/auth/cloud-platform']
                    )
                except Exception as e:
                    error_msg = f"Failed to load credentials from service account file '{sa_file}': {e}"
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)
        
        # If creds is still None, the client will use Application Default Credentials (ADC).
        
        try:
            self._client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location,
                credentials=creds,
            )
            self.logger.info(
                f"Initialized GeminiChatModel with model: {self.model_name} for Vertex AI "
                f"(Project: {self.project_id}, Location: {self.location})"
            )
        except Exception as e:
            error_msg = f"Failed to initialize GenAI Client for Vertex AI: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)

    def get_model_identifier(self) -> str:
        """Return a string identifying this model for tracing and logging."""
        return f"{self.__class__.__name__} (model='{self.model_name}')"

    def invoke(self, input, config=None, **kwargs):
        """Override invoke to add tracing callbacks automatically."""
        config = self._tracing_manager.add_callbacks_to_config(config)
        return super().invoke(input, config=config, **kwargs)

    async def ainvoke(self, input, config=None, **kwargs):
        """Override ainvoke to add tracing callbacks automatically."""
        config = self._tracing_manager.add_callbacks_to_config(config)
        return await super().ainvoke(input, config=config, **kwargs)

    def stream(self, input, config=None, **kwargs):
        """Override stream to add tracing callbacks automatically."""
        config = self._tracing_manager.add_callbacks_to_config(config)
        return super().stream(input, config=config, **kwargs)

    async def astream(self, input, config=None, **kwargs):
        """Override astream to add tracing callbacks automatically."""
        config = self._tracing_manager.add_callbacks_to_config(config)
        # We must call an async generator,
        async for chunk in super().astream(input, config=config, **kwargs):
            yield chunk
    
    @property
    def _llm_type(self) -> str:
        """Return identifier for the model type."""
        return "custom_google_genai"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters for tracing."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
        }
    
    def _convert_messages(self, messages: List[BaseMessage]) -> Union[types.ContentListUnion, types.ContentListUnionDict]:
        """
        Converts LangChain messages to a format suitable for the GenAI API.
        - For single, multi-part HumanMessage, returns a direct list of parts (e.g., [File, "text"]).
        - For multi-turn chats, returns a list of Content objects.
        - For simple text, returns a string.
        """
        self.logger.debug(f"Converting {len(messages)} messages.")
        
        # Filter out system messages (handled in generation_config)
        chat_messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]

        # Case 1: A single HumanMessage. This is the most common path for single prompts.
        if len(chat_messages) == 1 and isinstance(chat_messages[0], HumanMessage):
            content = chat_messages[0].content
            # For a simple string, return it directly.
            if isinstance(content, str):
                return content
            # For a list of parts, parse them into a direct list for the API.
            return list(self._parse_message_content(content, is_simple=True))


        # Case 2: Multi-turn chat history. This requires a list of Content objects.
        self.logger.debug("Handling as a multi-turn chat conversation.")
        genai_contents: List[types.Content] = []
        for msg in chat_messages:
            role = "model" if isinstance(msg, AIMessage) else "user"
            parts = []
            
            # Process each part and ensure proper typing
            for part in self._parse_message_content(msg.content, is_simple=False):
                if isinstance(part, types.File):
                    # put File directly into types.Content
                    parts.append(part)
                elif isinstance(part, types.Part):
                    parts.append(part)
                else:
                    self.logger.warning(f"Unexpected part type: {type(part)}")
            
            if parts:
                genai_contents.append(types.Content(parts=parts, role=role))
        
        # If there's only one Content object, return it directly instead of a list
        if len(genai_contents) == 1:
            return genai_contents[0]
            
        return genai_contents

    def _create_image_part(self, image_info: Dict[str, Any]) -> Union[types.Part, types.File]:
        """Creates a GenAI Part or File from various image source formats."""
        self.logger.debug(f"Creating image part from info: {list(image_info.keys())}")

        if "path" in image_info:
            return self._client.files.upload(file=image_info["path"])
        
        if "data" in image_info:
            data = image_info["data"]
            if image_info.get("source_type") == "base64":
                data = base64.b64decode(data)
            return types.Part.from_bytes(data=data, mime_type=image_info["mime_type"])

        url = image_info.get("image_url", image_info.get("url"))
        if isinstance(url, dict):
            url = url.get("url")
        
        if not url:
            raise ValueError(f"Invalid image info, requires 'path', 'data', or 'url'. Received: {image_info}")

        if url.startswith("data:"):
            header, encoded = url.split(",", 1)
            mime_type = header.split(":", 1)[-1].split(";", 1)[0]
            image_data = base64.b64decode(encoded)
            return types.Part.from_bytes(data=image_data, mime_type=mime_type)
        else:
            response = requests.get(url)
            response.raise_for_status()
            mime_type = response.headers.get("Content-Type", "image/jpeg")
            return types.Part.from_bytes(data=response.content, mime_type=mime_type)

    def _create_video_part(self, video_info: Dict[str, Any]) -> Union[types.Part, types.File]:
        """Creates a Google GenAI Part or File from video information.
        
        Supports multiple video input formats:
        - File object: {"type": "video_file", "file": file_object}
        - File path: {"type": "video_file", "path": "/path/to/video.mp4"}
        - Raw bytes: {"type": "video_file", "data": video_bytes, "mime_type": "video/mp4"}
        - URL/URI: {"type": "video_file", "url": "https://example.com/video.mp4"}
        - YouTube URL: {"type": "video_file", "url": "https://www.youtube.com/watch?v=..."}
        - URL with offset: {"type": "video_file", "url": "...", "start_offset": "12s", "end_offset": "50s"}
        
        Args:
            video_info: Dictionary containing video information
            
        Returns:
            Either a types.Part or File object for Google GenAI
            
        Raises:
            FileNotFoundError: If video file path doesn't exist
            ValueError: If video_info is invalid or missing required fields
        """
        self.logger.debug(f"Creating video part from info: {list(video_info.keys())}")
        
        # Handle pre-uploaded file object
        if "file" in video_info:
            if isinstance(video_info["file"], types.File):
                return video_info["file"]
            else:
                raise ValueError(f"The 'file' key must contain a google.genai.File object, but got {type(video_info['file'])}")

        if "path" in video_info:
            self.logger.debug(f"Uploading video file from path: {video_info['path']}")

            uploaded_file =self._client.files.upload(file=video_info["path"])

            self.logger.debug(f"Uploaded video file: {uploaded_file}")

            return uploaded_file
        
        mime_type = video_info.get("mime_type")

        if "data" in video_info:
            data = video_info["data"]
            if not mime_type:
                raise ValueError("'mime_type' is required when providing video data.")
            max_size = 20 * 1024 * 1024  # 20MB
            if len(data) > max_size:
                raise ValueError(f"Video data size ({len(data)} bytes) exceeds 20MB limit for inline data.")
            return types.Part(inline_data=types.Blob(data=data, mime_type=mime_type))

        url = video_info.get("url")
        if not url:
            raise ValueError(f"Invalid video info, requires 'path', 'data', 'url', or 'file'. Received: {video_info}")

        mime_type = video_info.get("mime_type", "video/mp4")
        
        # Handle video offsets
        start_offset = video_info.get("start_offset")
        end_offset = video_info.get("end_offset")

        self.logger.debug(f"Video offsets: {start_offset} to {end_offset}.")
        
        if start_offset or end_offset:
            video_metadata = types.VideoMetadata(start_offset=start_offset, end_offset=end_offset)
            return types.Part(
                file_data=types.FileData(file_uri=url, mime_type=mime_type),
                video_metadata=video_metadata
            )

        return types.Part(file_data=types.FileData(file_uri=url, mime_type=mime_type))

    def _parse_message_content(
        self, content: Union[str, List[Union[str, Dict]]], *, is_simple: bool = True
    ) -> Iterator[Union[str, types.Part, types.File]]:
        """
        Parses LangChain message content and yields parts for Google GenAI.

        Args:
            content: The message content to parse.
            is_simple: If True, yields raw objects where possible (e.g., str, File)
                               for single-turn efficiency. If False, ensures all yielded
                               parts are `types.Part` by converting raw strings and
                               Files as needed, which is required for multi-turn chat.

        Supports both standard LangChain formats and enhanced video formats:
        - Text: "string" or {"type": "text", "text": "content"}
        - Image: {"type": "image_url", "image_url": "url"} or {"type": "image_url", "image_url": {"url": "url"}}
        - Video: {"type": "video_file", ...} or {"type": "video", ...}                               
        """
        if isinstance(content, str):
            yield content if is_simple else types.Part(text=content)
            return

        if not isinstance(content, list):
            self.logger.warning(f"Unsupported content format: {type(content)}")
            return

        for i, part_spec in enumerate(content):
            try:
                if isinstance(part_spec, str):
                    yield part_spec if is_simple else types.Part(text=part_spec)
                    continue
                
                if isinstance(part_spec, types.File):
                    if is_simple:
                        yield part_spec
                    else:
                        yield types.Part(file_data=types.FileData(
                            mime_type=part_spec.mime_type,
                            file_uri=part_spec.uri
                        ))
                    continue

                if not isinstance(part_spec, dict):
                    self.logger.warning(f"Skipping non-dict part in content list: {type(part_spec)}")
                    continue

                part_type = part_spec.get("type", "").lower()
                
                if part_type == "text":
                    if text_content := part_spec.get("text"):
                        yield text_content if is_simple else types.Part(text=text_content)
                elif part_type in ("image", "image_url"):
                    yield self._create_image_part(part_spec)
                elif part_type in ("video", "video_file"):
                    yield self._create_video_part(part_spec)
                else:
                    self.logger.debug(f"Part with unknown type '{part_type}' was ignored at index {i}.")
            except Exception as e:
                self.logger.error(f"Failed to process message part at index {i}: {part_spec}. Error: {e}", exc_info=True)

    def _prepare_generation_config(
        self, messages: List[BaseMessage], stop: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Prepares the generation configuration, including system instructions."""
        # Base config from model parameters
        config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
        }
        if stop:
            config["stop_sequences"] = stop
        
        # Handle system instructions
        system_prompts = [msg.content for msg in messages if isinstance(msg, SystemMessage) and msg.content]
        if system_prompts:
            system_prompt_str = "\n\n".join(system_prompts)
            config["system_instruction"] = system_prompt_str
        
        # Filter out None values before returning
        return {k: v for k, v in config.items() if v is not None}

    def _trim_for_logging(self, contents: Any) -> Any:
        """Helper to trim large binary data from logging payloads."""
        if isinstance(contents, str):
            return contents
        
        if isinstance(contents, types.Content):
            return {
                "role": contents.role,
                "parts": [self._trim_part(part) for part in contents.parts]
            }
        
        if isinstance(contents, list):
            return [self._trim_for_logging(item) for item in contents]
        
        return contents

    def _trim_part(self, part: types.Part) -> dict:
        """Trims individual part data for safe logging."""
        part_dict = {}
        if part.text:
            part_dict["text"] = part.text
        if part.inline_data:
            part_dict["inline_data"] = {
                "mime_type": part.inline_data.mime_type,
                "data_size": f"{len(part.inline_data.data)} bytes"
            }
        if part.file_data:
            part_dict["file_data"] = {
                "mime_type": part.file_data.mime_type,
                "file_uri": part.file_data.file_uri
            }
        return part_dict

    def _map_usage_metadata(self, usage_metadata: Any) -> Optional[dict]:
        """
        Maps Google's rich usage metadata to LangChain's expected format,
        including detailed breakdowns by modality.
        """
        if not usage_metadata:
            return None
        
        # --- Basic Token Counts ---
        input_tokens = getattr(usage_metadata, "prompt_token_count", 0)
        output_tokens = getattr(usage_metadata, "candidates_token_count", 0)
        thoughts_tokens = getattr(usage_metadata, "thoughts_token_count", 0)
        total_tokens = getattr(usage_metadata, "total_token_count", 0)

        # In some cases, total_tokens is not provided, so we calculate it
        if total_tokens == 0 and (input_tokens > 0 or output_tokens > 0):
            total_tokens = input_tokens + output_tokens

        # --- Detailed Token Counts (The Fix) ---
        input_details = {}
        # The `prompt_tokens_details` is a list of ModalityTokenCount objects.
        # We convert it to a dictionary.
        if prompt_details_list := getattr(usage_metadata, "prompt_tokens_details", None):
            for detail in prompt_details_list:
                # Convert enum e.g., <MediaModality.TEXT: 'TEXT'> to "text"
                modality_key = detail.modality.name.lower()
                input_details[modality_key] = detail.token_count
        
        # Add cached tokens to input details if present
        #if cached_tokens := getattr(usage_metadata, "cached_content_token_count", 0):
        #    input_details["cached_content"] = cached_tokens

        output_details = {}
        # The `candidates_tokens_details` is also a list, so we convert it.
        if candidate_details_list := getattr(usage_metadata, "candidates_tokens_details", None):
            for detail in candidate_details_list:
                modality_key = detail.modality.name.lower()
                output_details[modality_key] = detail.token_count

        # --- Construct the final dictionary ---
        final_metadata = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "thoughts_tokens": thoughts_tokens,
            "total_tokens": total_tokens,
        }

        ## COMMENTED BEGIN: This is not working as expected.
        # if input_details:
        #     final_metadata["input_token_details"] = input_details
        # if output_details:
        #     final_metadata["output_token_details"] = output_details
        ## COMMENTED END
            
        return final_metadata

    def _extract_usage_metadata(self, response) -> Optional[Any]:
        """Extracts the raw usage_metadata object from a Google GenAI response."""
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            self.logger.debug(f"[_extract_usage_metadata] Found usage_metadata: {response.usage_metadata}")
            return response.usage_metadata
        return None

    def _create_chat_generation_chunk(self, chunk_response) -> ChatGenerationChunk:
        """Creates a ChatGenerationChunk for streaming."""
        # For streaming, we do not include usage metadata in individual chunks
        # to prevent merge conflicts. The final, aggregated response will contain
        # the full usage details for callbacks like Langfuse.
        return ChatGenerationChunk(
            message=AIMessageChunk(
                content=chunk_response.text,
                response_metadata={"model_name": self.model_name},
            ),
            generation_info=None,
        )

    def _create_chat_result_with_usage(self, response) -> ChatResult:
        """Creates a ChatResult with usage metadata for Langfuse tracking."""
        generated_text = response.text
        finish_reason = response.candidates[0].finish_reason.name if response.candidates else None
        
        # Use the new mapping function here for invoke calls
        usage_metadata = self._extract_usage_metadata(response)
        usage_dict = self._map_usage_metadata(usage_metadata) or {}

        message = AIMessage(
            content=generated_text,
            response_metadata={
                "model_name": self.model_name,
                "finish_reason": finish_reason,
                **usage_dict
            }
        )
        
        generation = ChatGeneration(
            message=message,
            generation_info={"token_usage": usage_dict} if usage_dict else None
        )
        
        # We also construct the llm_output dictionary in the format expected
        # by LangChain callback handlers, with a specific "token_usage" key.
        chat_result = ChatResult(
            generations=[generation],
            llm_output={
                "token_usage": usage_dict,
                "model_name": self.model_name
            } if usage_dict else {
                "model_name": self.model_name
            }
        )
        
        return chat_result

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generates a chat response from a list of messages."""
        self.logger.info(f"Generating response for {len(messages)} messages.")
        
        # Remove the problematic add_handler call - callbacks are now handled in invoke methods
        
        contents = self._convert_messages(messages)
        config = self._prepare_generation_config(messages, stop)

        try:
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
                **kwargs,
            )
            
            return self._create_chat_result_with_usage(response)
            
        except Exception as e:
            self.logger.error(f"Error generating content with Google GenAI: {e}", exc_info=True)
            raise ValueError(f"Error during generation: {e}")

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Asynchronously generates a chat response."""
        self.logger.info(f"Async generating response for {len(messages)} messages.")
        
        contents = self._convert_messages(messages)
        config = self._prepare_generation_config(messages, stop)

        try:
            response = await self._client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
                **kwargs,
            )
            
            return self._create_chat_result_with_usage(response)

        except Exception as e:
            self.logger.error(f"Error during async generation: {e}", exc_info=True)
            raise ValueError(f"Error during async generation: {e}")

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Streams the chat response and properly handles final usage metadata."""
        self.logger.info(f"Streaming response for {len(messages)} messages.")
        
        contents = self._convert_messages(messages)
        config = self._prepare_generation_config(messages, stop)

        try:
            stream = self._client.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=config,
                **kwargs,
            )
            
            final_usage_metadata = None
            for chunk_response in stream:
                if chunk_response.usage_metadata:
                    final_usage_metadata = self._extract_usage_metadata(chunk_response)

                if chunk_response.text:
                    yield self._create_chat_generation_chunk(chunk_response)
            
            # **FIX:** Yield a final chunk with the mapped usage data
            if final_usage_metadata:
                lc_usage_metadata = self._map_usage_metadata(final_usage_metadata)
                if lc_usage_metadata:
                    yield ChatGenerationChunk(
                        message=AIMessageChunk(content="", usage_metadata=lc_usage_metadata)
                    )

        except Exception as e:
            self.logger.error(f"Error streaming content: {e}", exc_info=True)
            raise ValueError(f"Error during streaming: {e}")

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """Asynchronously streams the chat response and properly handles final usage metadata."""
        self.logger.info(f"Async streaming response for {len(messages)} messages.")
        
        contents = self._convert_messages(messages)
        config = self._prepare_generation_config(messages, stop)

        try:
            stream = await self._client.aio.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=config,
                **kwargs,
            )
            
            final_usage_metadata = None
            async for chunk_response in stream:
                if chunk_response.usage_metadata:
                    final_usage_metadata = self._extract_usage_metadata(chunk_response)
                
                if chunk_response.text:
                    yield self._create_chat_generation_chunk(chunk_response)
            
            # **FIX:** Yield a final chunk with the mapped usage data
            if final_usage_metadata:
                lc_usage_metadata = self._map_usage_metadata(final_usage_metadata)
                if lc_usage_metadata:
                    yield ChatGenerationChunk(
                        message=AIMessageChunk(content="", usage_metadata=lc_usage_metadata)
                    )
                    
        except Exception as e:
            self.logger.error(f"Error during async streaming: {e}", exc_info=True)
            raise ValueError(f"Error during async streaming: {e}")