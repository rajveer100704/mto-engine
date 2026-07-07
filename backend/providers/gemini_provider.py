# =============================================================================
# GeminiVisionProvider — Google Gemini 2.5 Flash vision extraction
# =============================================================================
from __future__ import annotations

import io
import json
import os

import google.generativeai as genai
from PIL import Image

from providers.base import ProviderError, VisionExtractionProvider
from prompts.system_prompt import SYSTEM_PROMPT
from prompts.response_schema import EXTRACTION_USER_PROMPT, RESPONSE_SCHEMA


class GeminiVisionProvider(VisionExtractionProvider):
    """Extracts MTO from piping isometrics using Google Gemini 2.5 Flash.

    Requires GOOGLE_API_KEY environment variable.
    Uses structured JSON output (response_mime_type=application/json)
    to guarantee schema-compliant responses without regex parsing.
    """

    MODEL_ID = "gemini-2.5-flash"

    def __init__(self) -> None:
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            raise ProviderError(self.name, "GOOGLE_API_KEY is not set")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(
            model_name=self.MODEL_ID,
            system_instruction=SYSTEM_PROMPT,
        )

    @property
    def name(self) -> str:
        return f"Gemini {self.MODEL_ID}"

    async def extract(self, image: Image.Image) -> dict:
        """Send image to Gemini and return raw MTO dict."""
        try:
            # Convert PIL image to bytes for Gemini
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            image_bytes = buf.getvalue()

            image_part = {
                "mime_type": "image/png",
                "data": image_bytes,
            }

            response = self._model.generate_content(
                [image_part, EXTRACTION_USER_PROMPT],
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1,  # Low temperature for deterministic engineering output
                    max_output_tokens=8192,
                ),
            )

            raw_text = response.text.strip()

            # Strip any accidental markdown fences
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[-1]
                raw_text = raw_text.rsplit("```", 1)[0]

            data = json.loads(raw_text)
            return data

        except json.JSONDecodeError as e:
            raise ProviderError(self.name, f"Invalid JSON from Gemini: {e}") from e
        except Exception as e:
            raise ProviderError(self.name, f"Gemini API error: {e}") from e
