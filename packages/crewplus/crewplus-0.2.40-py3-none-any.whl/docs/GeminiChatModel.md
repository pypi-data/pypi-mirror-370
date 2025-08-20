# GeminiChatModel Documentation

## 1. Introduction

The `GeminiChatModel` is a custom LangChain-compatible chat model that provides a robust interface to Google's Gemini Pro and Flash models. It is designed to handle multimodal inputs, including text, images, and videos, making it a versatile tool for building advanced AI applications.

### Key Features:
- **LangChain Compatibility**: Seamlessly integrates into the LangChain ecosystem as a `BaseChatModel`.
- **Multimodal Support**: Natively processes text, images (from URLs, local paths, or base64), and videos (from local paths, Google Cloud URIs, or raw bytes).
- **Streaming**: Supports streaming for both standard and multimodal responses.
- **Advanced Configuration**: Allows fine-tuning of generation parameters like temperature, top-p, top-k, and max tokens.
- **Video Segment Analysis**: Can process specific time ranges within a video using start and end offsets.

## 2. Installation

To use the `GeminiChatModel`, you need to install the `crewplus` package. If you are working within the project repository, you can install it in editable mode:

```bash
pip install crewplus
```

## 3. Initialization

First, ensure you have set your Google API key as an environment variable:

```bash
# For Linux/macOS
export GOOGLE_API_KEY="YOUR_API_KEY"

# For Windows PowerShell
$env:GEMINI_API_KEY = "YOUR_API_KEY"
```

Then, you can import and initialize the model in your Python code.

```python
import logging
from crewplus.services import GeminiChatModel
from langchain_core.messages import HumanMessage

# Optional: Configure a logger for detailed output
logging.basicConfig(level=logging.INFO)
test_logger = logging.getLogger(__name__)

# Initialize the model
# You can also pass the google_api_key directly as a parameter
model = GeminiChatModel(
    model_name="gemini-2.5-flash", # Or "gemini-1.5-pro"
    logger=test_logger,
    temperature=0.0,
)
```

## 4. Basic Usage (Text-only)

The model can be used for simple text-based conversations using `.invoke()` or `.stream()`.

```python
# Using invoke for a single response
response = model.invoke("Hello, how are you?")
print(response.content)

# Using stream for a chunked response
print("\n--- Streaming Response ---")
for chunk in model.stream("Tell me a short story about a brave robot."):
    print(chunk.content, end="", flush=True)

# Using astream for an asynchronous chunked response
import asyncio

async def main():
    print("\n--- Async Streaming Response ---")
    async for chunk in model.astream("Tell me a short story about a brave robot."):
        print(chunk.content, end="", flush=True)

# To run the async function in a Jupyter Notebook or a script:
# await main()
# Or, if not in an async context:
# asyncio.run(main())
```

## 5. Image Understanding

`GeminiChatModel` can understand images provided via a URL or as base64 encoded data.

### Example 1: Image from a URL

You can provide a direct URL to an image.

```python
from langchain_core.messages import HumanMessage

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
```
> **Sample Output:**
> The image shows a wooden boardwalk stretching into the distance through a field of tall, green grass... The overall impression is one of tranquility and natural beauty.

### Example 2: Local Image (Base64)

You can also send a local image file by encoding it in base64.

```python
import base64
from langchain_core.messages import HumanMessage

image_path = "./notebooks/test_image_202506191.jpg"
try:
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    image_message = HumanMessage(
        content=[
            {"type": "text", "text": "Describe this photo and its background story."},
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

### Example 3: Streaming a Multimodal Response

Streaming also works with complex, multimodal inputs. This is useful for getting faster time-to-first-token while the model processes all the data.

```python
# The url_message is from the previous example
print("\n--- Streaming Multimodal Response ---")
for chunk in model.stream([url_message]):
    print(chunk.content, end="", flush=True)
```

## 6. Video Understanding

The model supports video analysis from uploaded files, URIs, and raw bytes.

**Important Note:** The Gemini API does **not** support common public video URLs (e.g., YouTube, Loom, or public MP4 links). Videos must be uploaded to Google's servers first to get a processable URI.

### Example 1: Large Video File (>20MB)

For large videos, you must first upload the file using the `google-genai` client to get a file object.

```python
from google import genai
import os
from langchain_core.messages import HumanMessage

# Initialize the Google GenAI client
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

# Upload the video file
video_path = "./notebooks/manufacturing_process_tutorial.mp4"
print("Uploading video... this may take a moment.")
video_file_obj = client.files.upload(file=video_path)
print(f"Video uploaded successfully. File name: {video_file_obj.name}")

# Use the uploaded file object in the prompt
video_message = HumanMessage(
    content=[
        {"type": "text", "text": "Summarize this video and provide timestamps for key events."},
        {"type": "video_file", "file": video_file_obj},
    ]
)
video_response = model.invoke([video_message])
print("Video response:", video_response.content)
```

> **Sample Output:**
> This video provides a step-by-step guide on how to correct a mis-set sidewall during tire manufacturing...
> **Timestamps:**
> * **0:04:** Applying product package to some material
> * **0:12:** Splice product Together and Prepare some material
> ...

### Example 2: Video with Time Offsets

You can analyze just a specific portion of a video by providing a `start_offset` and `end_offset`. This works with video URIs obtained after uploading.

```python
# Assuming 'video_file_obj' is available from the previous step
video_uri = video_file_obj.uri

offset_message = HumanMessage(
    content=[
        {"type": "text", "text": "Transcribe the events in this video segment."},
        {
            "type": "video_file", 
            "url": video_uri,
            "start_offset": "5s",
            "end_offset": "30s"
        }
    ]
)

print("Streaming response for video segment:")
for chunk in model.stream([offset_message]):
    print(chunk.content, end="", flush=True)
```
> **Sample Output:**
> This video demonstrates the process of applying Component A/Component B material to an assembly drum in a manufacturing setting...
> **Transcription:**
> **0:05 - 0:12:** A worker is shown applying a material...
> **0:12 - 0:23:** The worker continues to prepare the material on the drum...

### Example 3: Small Video File (<20MB)

For small videos, you can pass the raw bytes directly without a separate upload step.

```python
from langchain_core.messages import HumanMessage

try:
    with open("./notebooks/product_demo_v1.mp4", "rb") as video_file:
        video_bytes = video_file.read()
    
    video_message = HumanMessage(
        content=[
            {"type": "text", "text": "What is happening in this video?"},
            {
                "type": "video_file",
                "data": video_bytes,
                "mime_type": "video/mp4" # Mime type is required for raw data
            },
        ]
    )
    video_response = model.invoke([video_message])
    print("Video response (bytes):", video_response.content)
except FileNotFoundError:
    print("Video file not found.")
except Exception as e:
    print(f"Video processing with bytes failed: {e}")
```