# =============================================================================
# GeminiVisionProvider — Google Gemini 2.5 Flash vision extraction
# =============================================================================
from __future__ import annotations

import asyncio
import io
import json
import logging
import os

import google.generativeai as genai
from PIL import Image

from providers.base import ProviderError, VisionExtractionProvider
from prompts.system_prompt import SYSTEM_PROMPT
from prompts.response_schema import EXTRACTION_USER_PROMPT, RESPONSE_SCHEMA

logger = logging.getLogger(__name__)


class GeminiVisionProvider(VisionExtractionProvider):
    """Extracts MTO from piping isometrics using Google Gemini 2.5 Flash.

    Requires GOOGLE_API_KEY environment variable.
    Uses structured JSON output (response_mime_type=application/json)
    constrained by RESPONSE_SCHEMA to guarantee schema-compliant responses.
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
        # Convert PIL image to bytes for Gemini
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        image_bytes = buf.getvalue()

        image_part = {
            "mime_type": "image/png",
            "data": image_bytes,
        }

        # Attempt up to 2 times to handle transient JSON parse errors and API anomalies
        for attempt in range(1, 3):
            try:
                # Wrap blocking generate_content call in executor
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self._model.generate_content(
                        [image_part, EXTRACTION_USER_PROMPT],
                        generation_config=genai.types.GenerationConfig(
                            response_mime_type="application/json",
                            response_schema=RESPONSE_SCHEMA,
                            temperature=0.1,  # Low temperature for deterministic engineering output
                            max_output_tokens=8192,
                        ),
                    )
                )

                # 1. Safely check candidates
                if not getattr(response, "candidates", None):
                    raise ProviderError(self.name, "Gemini returned no candidates (response may have been blocked).")

                candidate = response.candidates[0]
                finish_reason_name = getattr(getattr(candidate, "finish_reason", None), "name", "UNKNOWN")

                # Check finish reason before parsing
                if finish_reason_name != "STOP":
                    logger.warning(f"Generation candidate finished with reason: {finish_reason_name}")

                # 2. Safely read response text
                raw_text = ""
                try:
                    raw_text = response.text
                except Exception as text_err:
                    logger.error(f"Failed to read response.text: {text_err}")

                if not raw_text:
                    raise ProviderError(
                        self.name,
                        f"Gemini returned an empty response. Candidate finish reason: {finish_reason_name}"
                    )

                raw_text = raw_text.strip()

                # Strip any accidental markdown fences
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("\n", 1)[-1]
                    raw_text = raw_text.rsplit("```", 1)[0]
                    raw_text = raw_text.strip()

                # 3. Parse JSON
                data = json.loads(raw_text)

                # 4. Verify basic schema structure to detect partial/truncated response
                if not isinstance(data, dict) or "drawing_meta" not in data or "items" not in data:
                    raise json.JSONDecodeError("Response JSON missing drawing_meta or items keys", raw_text, 0)

                return data

            except (AttributeError, TypeError, ValueError, NameError):
                # Programming/type errors should fail immediately without retry to avoid obscuring bugs
                raise

            except json.JSONDecodeError as e:
                logger.error("=" * 80)
                logger.error(f"Attempt {attempt} failed to parse JSON from Gemini: {e}")
                try:
                    logger.error(f"Finish Reason: {response.candidates[0].finish_reason}")
                except Exception:
                    pass
                logger.error("RAW TEXT RECEIVED:")
                logger.error(raw_text if 'raw_text' in locals() else "<no text retrieved>")
                logger.error("=" * 80)

                if attempt == 2:
                    raise ProviderError(self.name, f"Invalid JSON from Gemini after retry: {e}") from e

            except Exception as e:
                logger.error(f"Attempt {attempt} failed with Gemini API error: {e}")
                if attempt == 2:
                    raise ProviderError(self.name, f"Gemini API error: {e}") from e

