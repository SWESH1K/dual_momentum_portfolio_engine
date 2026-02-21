import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class AIAnalysisError(Exception):
    """Raised when AI analysis fails."""
    pass


def get_ai_analysis(
    strategy_A_score: Dict[str, Any],
    strategy_B_score: Dict[str, Any],
    model: str = "gemini-2.5-flash-lite",
    stream: bool = False
) -> str:
    """
    Generates structured AI comparison of two strategies.
    Returns analysis as a string.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not found in environment variables.")

    if not isinstance(strategy_A_score, dict):
        raise TypeError("strategy_A_score must be a dictionary.")

    if not isinstance(strategy_B_score, dict):
        raise TypeError("strategy_B_score must be a dictionary.")

    try:
        strategy_A_json = json.dumps(strategy_A_score, indent=2)
        strategy_B_json = json.dumps(strategy_B_score, indent=2)
    except Exception as e:
        raise ValueError("Failed to serialize strategy scores to JSON.") from e

    prompt = f"""
    You are a quantitative investment analyst.

    You will receive JSON input containing performance metrics of two investment strategies.

    Your task is to perform a structured professional comparison.

    Follow these sections strictly:

    1. Overall Performance
    2. Risk Characteristics
    3. Risk-Return Trade-off
    4. Market Regime Suitability
    5. One Concrete Improvement Suggestion

    Formatting:
    - Use section headings
    - Be analytical and concise
    - Do not fabricate data
    - Base reasoning strictly on provided metrics

    Strategy A:
    {strategy_A_json}

    Strategy B:
    {strategy_B_json}
    """

    try:
        client = genai.Client(api_key=api_key)

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]

        response_text = ""

        if stream:
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
            ):
                if chunk.text:
                    response_text += chunk.text
        else:
            response = client.models.generate_content(
                model=model,
                contents=contents,
            )
            response_text = response.text

        if not response_text:
            raise AIAnalysisError("Empty response received from AI model.")

        return response_text.strip()

    except Exception as e:
        raise AIAnalysisError("AI analysis request failed.") from e