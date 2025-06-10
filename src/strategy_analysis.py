import google.generativeai as genai
from config import GEMINI_API_KEY
from typing import Dict, Any

class StrategyAnalyzer:
    """
    Analyzes badminton game strategy by synthesizing data from video and text analysis.
    Uses the Google Gemini Pro model to identify patterns, strengths, and weaknesses.
    """
    def __init__(self):
        """Initializes the StrategyAnalyzer and configures the Gemini API."""
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            print("StrategyAnalyzer initialized with Gemini Pro.")
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            self.model = None

    def analyze_strategy(self, video_analysis_results: Dict[str, Any], text_analysis_results: str) -> str:
        """
        Generates a strategic analysis based on combined video and text data.

        Args:
            video_analysis_results (Dict[str, Any]): A dictionary containing results from video processing,
                                                     such as player positions and shot types.
            text_analysis_results (str): A string containing insights from text analysis,
                                         like commentary summaries and sentiment.

        Returns:
            A string containing the strategic analysis.
        """
        if not self.model:
            return "Strategy analyzer is not available."

        # Create a detailed prompt for the generative model
        prompt = f"""
        Analyze the badminton strategy based on the following data:

        --- Video Analysis Summary ---
        {video_analysis_results}

        --- Text Analysis Summary ---
        {text_analysis_results}

        --- Analysis Task ---
        Based on the data above, provide a strategic analysis covering:
        1.  **Player A's Strengths and Weaknesses:** Identify dominant shots, movement patterns, and potential vulnerabilities.
        2.  **Player B's Strengths and Weaknesses:** Similarly, analyze the opponent's patterns.
        3.  **Key Strategic Patterns:** Describe any recurring tactical exchanges or patterns in the rally.
        4.  **Suggested Adjustments:** Recommend strategic changes for one or both players to gain an advantage.

        Provide a concise, insightful report.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"An error occurred during strategy analysis: {e}"

# Example usage:
if __name__ == '__main__':
    strategy_analyzer = StrategyAnalyzer()

    # Mock analysis results
    mock_video_results = {
        "player_A_position": "aggressive, near the net",
        "player_B_position": "defensive, baseline",
        "dominant_shot": "Player A cross-court smash"
    }
    mock_text_results = "Player A is controlling the pace with powerful smashes. Player B is struggling to return them effectively."

    strategy_report = strategy_analyzer.analyze_strategy(mock_video_results, mock_text_results)

    print("--- Strategy Analysis Report ---")
    print(strategy_report)
