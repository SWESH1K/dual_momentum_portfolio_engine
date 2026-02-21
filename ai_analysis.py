import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(strategy_A_score, strategy_B_score):
  prompt = f"""
  You are a quantitative investment analyst.

  You will receive JSON input containing performance metrics of two investment strategies.
  The JSON will include (but may not be limited to):

  - total_return
  - cagr
  - max_drawdown
  - volatility
  - sharpe_ratio (if available)
  - time_period
  - any additional risk metrics

  Your task is to perform a structured professional comparison of the two strategies.

  Please follow these steps strictly:

  1. Compare Overall Performance
    - Compare total return and CAGR.
    - Identify which strategy generated higher compounded growth.
    - Comment on consistency if implied by the data.

  2. Compare Risk Characteristics
    - Compare volatility.
    - Compare maximum drawdown.
    - Identify which strategy is riskier and in what sense.

  3. Discuss Risk-Return Trade-off
    - Evaluate whether higher returns are justified by higher risk.
    - If Sharpe ratio is available, use it.
    - If not available, infer trade-off qualitatively from return vs volatility.

  4. When Each Strategy May Outperform
    - Describe market environments (bullish, bearish, high volatility, trending, sideways).
    - Suggest conditions under which one strategy is structurally favored.

  5. Suggest One Concrete Improvement Idea
      - Suggest one realistic quantitative improvement.
      - Example categories: risk management, dynamic allocation, longer lookback, volatility scaling, drawdown control, diversification.
      - The suggestion must be actionable and technically meaningful.

    Formatting Rules:
    - Use clear section headings.
    - Be analytical, not promotional.
    - Avoid generic statements.
    - Base reasoning strictly on provided metrics.
    - If metrics are missing, state reasonable assumptions.
    - Do not fabricate data.

    Tone:
    Professional, analytical, concise but insightful.

    Now analyze the following JSON:

    Strategy A : {strategy_A_score}
    Strategy B : {strategy_B_score}
  """

  client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

  model = "gemini-2.5-flash-lite"
  contents = [
      types.Content(
          role="user",
          parts=[
              types.Part.from_text(text=prompt),
          ],
      ),
  ]
  tools = [
      types.Tool(googleSearch=types.GoogleSearch(
      )),
  ]
  generate_content_config = types.GenerateContentConfig(
      tools=tools,
  )

  for chunk in client.models.generate_content_stream(
      model=model,
      contents=contents,
      config=generate_content_config,
  ):
    print(chunk.text, end="")