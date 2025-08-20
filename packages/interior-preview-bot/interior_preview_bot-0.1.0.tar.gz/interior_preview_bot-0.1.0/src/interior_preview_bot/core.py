
import os
import base64
import json
from openai import OpenAI

class InteriorPreviewBot:
    """
    A bot to generate interior design previews using Poe API models.
    """

    def __init__(self, api_key: str):
        """
        Initializes the Poe API client.

        Args:
            api_key: Your Poe API key.
        """
        if not api_key:
            raise ValueError("Poe API key is required.")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.poe.com/v1",
        )

    def _encode_image(self, image_path: str) -> str:
        """
        Encodes an image file to a base64 string.

        Args:
            image_path: The path to the image file.

        Returns:
            The base64-encoded image string.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _get_structured_prompt(self, prompt: str, room_image_path: str = None, reference_image_path: str = None) -> dict:
        """
        Calls the IPPrompter-1 model to get a structured JSON prompt.

        Args:
            prompt: The user's freeform request.
            room_image_path: Optional path to the room image.
            reference_image_path: Optional path to the reference image.

        Returns:
            A dictionary with the structured prompt.
        """
        messages = [{"role": "user", "content": prompt}]
        
        # This part is an assumption based on the documentation, 
        # as it mentions optionally sending images to IPPrompter-1
        if room_image_path:
            room_img_base64 = self._encode_image(room_image_path)
            messages[0]["content"] = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{room_img_base64}"}},
            ]
            if reference_image_path:
                 ref_img_base64 = self._encode_image(reference_image_path)
                 messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{ref_img_base64}"}})


        chat = self.client.chat.completions.create(
            model="IPPrompter-1",
            messages=messages,
            stream=False,
        )
        response_content = chat.choices[0].message.content
        try:
            return json.loads(response_content)
        except json.JSONDecodeError:
            # Handle cases where the output is not valid JSON
            # For simplicity, we'll create a basic structure.
            return {"image_prompt": response_content, "mask_prompt": None}


    def _generate_mask(self, mask_prompt: str, room_image_path: str) -> str:
        """
        Calls the Segment-Anything-v2 model to generate a mask.

        Args:
            mask_prompt: The prompt for the mask (text or coordinates).
            room_image_path: The path to the room image.

        Returns:
            The base64-encoded mask image string.
        """
        room_img_base64 = self._encode_image(room_image_path)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": mask_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{room_img_base64}"}},
                ],
            }
        ]

        chat = self.client.chat.completions.create(
            model="Segment-Anything-v2",
            messages=messages,
            stream=False,
        )
        
        # Assuming the API returns the image in a format that can be accessed this way.
        # Based on OpenAI's DALL-E API, the response might contain a base64-encoded image
        # or a URL. We'll assume base64 for now.
        # This part might need adjustment based on the actual Poe API response for images.
        # For this implementation, we'll assume the content of the message is the base64 string.
        return chat.choices[0].message.content


    def generate_preview(
        self,
        room_image_path: str,
        reference_image_path: str,
        prompt: str,
        quality: str = "medium",
        aspect: str = "1:1",
        use_sam_mask: bool = False,
    ) -> bytes:
        """
        Generates an interior design preview.

        Args:
            room_image_path: Path to the room image.
            reference_image_path: Path to the reference material image.
            prompt: The user's freeform request.
            quality: The quality of the output image ('high', 'medium', 'low').
            aspect: The aspect ratio of the output image ('1:1', '3:2', '2:3').
            use_sam_mask: Whether to generate and use a mask from SAM.

        Returns:
            The generated preview image as a bytes object.
        """
        structured_prompt_data = self._get_structured_prompt(prompt, room_image_path, reference_image_path)
        image_prompt = structured_prompt_data.get("image_prompt", prompt)
        mask_prompt = structured_prompt_data.get("mask_prompt")

        room_img_base64 = self._encode_image(room_image_path)
        ref_img_base64 = self._encode_image(reference_image_path)

        messages_content = []
        
        mask_img_base64 = None
        if use_sam_mask and mask_prompt:
            mask_img_base64 = self._generate_mask(mask_prompt, room_image_path)
            final_prompt = f"{image_prompt} --quality {quality} --aspect {aspect} --use_mask"
        else:
            final_prompt = f"{image_prompt} --quality {quality} --aspect {aspect}"
            
        messages_content.append({"type": "text", "text": final_prompt})
        messages_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{room_img_base64}"}})
        messages_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{ref_img_base64}"}})

        if mask_img_base64:
            messages_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{mask_img_base64}"}})

        response = self.client.chat.completions.create(
            model="IPPreview-1",
            messages=[{"role": "user", "content": messages_content}],
        )

        # Assuming the API returns the final image as a base64 encoded string in the first choice's message content.
        # This might need adjustment based on the actual Poe API response structure for images.
        image_data_base64 = response.choices[0].message.content
        
        # The user might get a response that is not a base64 string, for example a text message.
        # We try to decode it, and if it fails, we raise an error.
        try:
            return base64.b64decode(image_data_base64)
        except (base64.binascii.Error, TypeError):
            raise ValueError(f"Failed to decode the image from the API response. The response was: {image_data_base64}")

