"""Generate coaching report from multimodal analysis."""
from typing import Dict, List
import textwrap

from google.generativeai import configure, GenerativeModel


def init_gemini(api_key: str):
    configure(api_key=api_key)


def generate_report(pose_metrics: List[Dict], transcription: str, locale: str = "en") -> str:
    """Use Gemini to craft a coaching report. If locale != 'en', translate accordingly."""
    system_prompt = textwrap.dedent(
        f"""You are an elite badminton coach analysing a player's match video and associated on-court audio conversations.
        Summarise key findings and provide actionable feedback.
        Return the report in {locale} language.
        Sections:
        1. Overall performance summary
        2. Footwork & positioning insights (use pose data when confidence>0.3)
        3. Shot selection / technique observations
        4. Communication & mindset (from audio)
        5. Actionable next-steps (bullet points)
        """
    )
    user_content = {
        "pose_metrics": pose_metrics[:100],  # sample first 100 entries to avoid huge context
        "transcription": transcription,
    }
    model = GenerativeModel("gemini-1.5-flash")
    # Combine system prompt and user content into a single prompt
    prompt = f"{system_prompt}\n\nHere's the analysis data:\n{str(user_content)}"
    response = model.generate_content(prompt)
    return response.text
