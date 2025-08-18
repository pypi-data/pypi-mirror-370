# TypeGPT Moderation Client

A simple and powerful Python client for the **TypeGPT Multimodal Moderation API**.

This library provides an easy-to-use interface to moderate various types of content—**text, images, videos, and voice**—by communicating with the deployed API at `http://mono.typegpt.net`.

## Key Features

-   **Truly Multimodal:** Moderate text, images, videos, and voice audio in a single API call.
-   **Flexible Inputs:** Provide content via local file paths, public URLs, or raw in-memory bytes.
-   **Simple Interface:** A clean and intuitive client that can be used as a context manager.
-   **Typed Responses:** API responses are parsed into Pydantic models for easy and reliable access to data.
-   **Robust Error Handling:** Catches API and network errors, raising a custom `ModerationAPIError` with details.

## Installation

Install the library directly from PyPI using pip:

```bash
pip install typegpt-moderation
```

This will also install the required dependencies: `httpx` and `pydantic`.

## Quickstart

Get started in just a few lines of code. The primary interface is the `ModerationClient`.

```python
from typegpt_moderation import ModerationClient, ModerationAPIError

# It is recommended to use the client as a context manager
try:
    with ModerationClient() as client:
        # 1. Send content for moderation
        response = client.moderate(text="This is a test to see if the content is safe.")
        
        # 2. The API returns a response object containing a list of results
        result = response.results[0]
        
        # 3. Check the results
        if result.flagged:
            print("❌ Content was flagged as unsafe.")
            print(f"   Reason: {result.reason}")
            
            # See which specific categories were violated
            violated_categories = [cat for cat, flagged in result.categories.items() if flagged]
            print(f"   Categories: {violated_categories}")
        else:
            print("✅ Content is safe.")

except ModerationAPIError as e:
    print(f"An API error occurred: Status {e.status_code} - {e.detail}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

## Usage Examples

The `moderate()` method can handle any combination of text, image, video, or voice.

### 1. Moderating Text

You can provide a single string or a list of strings.

```python
with ModerationClient() as client:
    response = client.moderate(text="This is a simple text moderation request.")
    print(f"Flagged: {response.results[0].flagged}")
```

### 2. Moderating an Image

Provide a local file path or a public URL. The library handles the encoding.

```python
with ModerationClient() as client:
    # From a local file
    response_from_file = client.moderate(image="/path/to/your/image.jpg")
    print(f"Image file flagged: {response_from_file.results[0].flagged}")

    # From a URL
    response_from_url = client.moderate(image="https://www.example.com/some-image.png")
    print(f"Image URL flagged: {response_from_url.results[0].flagged}")
```

### 3. Moderating a Video

Just like images, you can use a local file path or a public URL for videos.

```python
with ModerationClient() as client:
    # From a local file
    response = client.moderate(video="/path/to/local/video.mp4")
    print(f"Video flagged: {response.results[0].flagged}")
```

### 4. Moderating Voice Audio

The API will transcribe the audio and moderate the resulting text.

```python
with ModerationClient() as client:
    response = client.moderate(voice="/path/to/audio/note.mp3")
    result = response.results[0]
    
    print(f"Voice note flagged: {result.flagged}")
    
    # You can access the transcribed text from the result
    if result.transcribed_text:
        print(f"Transcribed Text: '{result.transcribed_text}'")
```

### 5. Multimodal Moderation (Combined Inputs)

The true power of the library is combining inputs. The API analyzes all provided content together for a single, holistic moderation result.

```python
with ModerationClient() as client:
    response = client.moderate(
        text="Please review the attached media and voice note from the user.",
        image="/path/to/user_avatar.png",
        video="/path/to/user_post.mp4",
        voice="/path/to/user_voice_message.wav"
    )
    
    result = response.results[0]
    print(f"Overall content flagged: {result.flagged}")
    if result.flagged:
        print(f"Reason: {result.reason}")
```

## API Reference

### `ModerationClient`

The main class for interacting with the API.

-   `__init__(self, base_url="http://mono.typegpt.net", timeout=180)`
    -   `base_url`: The base URL of the moderation service.
    -   `timeout`: Request timeout in seconds.

### `moderate()` method

-   `moderate(self, text=None, image=None, video=None, voice=None, ...)`
    -   **`text`** (`Optional[Union[str, List[str]]]`): A string or list of strings to moderate.
    -   **`image`** (`Optional[Union[str, bytes]]`): A URL, local file path, or raw bytes for an image.
    -   **`video`** (`Optional[Union[str, bytes]]`): A URL, local file path, or raw bytes for a video.
    -   **`voice`** (`Optional[Union[str, bytes]]`): A URL, local file path, or raw bytes for an audio file.
    -   **Returns:** A `ModerationResponse` object.

### Response Objects

Your results are returned as Pydantic models.

-   **`ModerationResponse`**: The top-level response object.
    -   `id` (`str`): A unique ID for the moderation request.
    -   `model` (`str`): The model used for moderation.
    -   `results` (`List[ModerationResultItem]`): A list containing the moderation result.

-   **`ModerationResultItem`**: Contains the detailed moderation verdict.
    -   `flagged` (`bool`): `True` if the content is unsafe, otherwise `False`.
    -   `moderation_type` (`str`): Indicates which modalities were moderated (e.g., `text_and_image`).
    -   `categories` (`Dict[str, bool]`): A dictionary of safety categories and whether they were violated.
    -   `category_scores` (`Dict[str, float]`): A dictionary of scores for each category.
    -   `reason` (`Optional[str]`): A human-readable explanation if the content was flagged.
    -   `transcribed_text` (`Optional[str]`): The text transcribed from a provided voice file.

## License

This project is licensed under the MIT License.