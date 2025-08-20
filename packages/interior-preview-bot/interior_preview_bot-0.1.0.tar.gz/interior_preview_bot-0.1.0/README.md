# Interior Preview Bot

A Python package to generate interior design previews using the IPPrompter-1, Segment-Anything-v2, and IPPreview-1 models on Poe.

## Installation

```bash
pip install interior_preview_bot
```

## Usage

1.  **Get a Poe API Key:**
    Create an API key from [poe.com/api_key](https://poe.com/api_key) and set it as an environment variable named `POE_API_KEY`.

2.  **Run the preview pipeline:**

```python
import os
from interior_preview_bot import InteriorPreviewBot

api_key = os.getenv("POE_API_KEY")

bot = InteriorPreviewBot(api_key=api_key)

# Generate a preview
result_image = bot.generate_preview(
    room_image_path="path/to/your/room.png",
    reference_image_path="path/to/your/material.png",
    prompt="Replace the floor with this marble texture.",
    # Optional parameters
    # quality="high", 
    # aspect="1:1",
    # use_sam_mask=True
)

# The result is a bytes object, you can save it to a file
with open("preview_result.png", "wb") as f:
    f.write(result_image)

print("Preview image saved to preview_result.png")
```
