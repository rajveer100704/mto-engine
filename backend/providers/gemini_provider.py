# =============================================================================
# GeminiVisionProvider — Google Gemini 2.5 Flash vision extraction
# =============================================================================
from __future__ import annotations

import asyncio
import io
import json
import logging
import os

from google.api_core.exceptions import GoogleAPIError
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

                # Get token count usage metadata
                usage = getattr(response, "usage_metadata", None)
                tokens = getattr(usage, "total_token_count", "unknown") if usage else "unknown"

                # Log detailed API request stats
                logger.info(
                    f"Gemini API Call: attempt={attempt} finish_reason={finish_reason_name} "
                    f"provider=gemini model={self.MODEL_ID} tokens={tokens}"
                )

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

                # 3. Parse JSON (with fallback to json-repair for robustness)
                try:
                    data = json.loads(raw_text)
                except json.JSONDecodeError as parse_err:
                    logger.warning(f"Initial json.loads failed: {parse_err}. Attempting automatic json-repair fallback.")
                    from json_repair import repair_json
                    repaired_text = repair_json(raw_text)
                    try:
                        data = json.loads(repaired_text)
                    except Exception:
                        # Raise the original parse error if repair also fails
                        raise parse_err

                # 4. Verify basic schema structure to detect partial/truncated response
                if not isinstance(data, dict) or "drawing_meta" not in data or "items" not in data:
                    raise json.JSONDecodeError("Response JSON missing drawing_meta or items keys", raw_text, 0)

                return data

            except (AttributeError, TypeError, ValueError, NameError):
                # Programming/type errors should fail immediately without retry to avoid obscuring bugs
                raise

            except (json.JSONDecodeError, GoogleAPIError) as e:
                # Catch and retry only JSON parsing and Google API errors
                logger.error("=" * 80)
                logger.error(f"Attempt {attempt} failed due to transient API/parsing error: {e}")
                try:
                    logger.error(f"Finish Reason: {response.candidates[0].finish_reason}")
                except Exception:
                    pass
                logger.error("RAW TEXT RECEIVED:")
                logger.error(raw_text if 'raw_text' in locals() else "<no text retrieved>")
                logger.error("=" * 80)

                if attempt == 2:
                    raise ProviderError(self.name, f"Invalid JSON or API error from Gemini after retry: {e}") from e

            except Exception as e:
                # Any other unexpected exception fails immediately
                logger.error(f"Unretryable failure on attempt {attempt}: {e}")
                raise ProviderError(self.name, f"Gemini provider failure: {e}") from e

