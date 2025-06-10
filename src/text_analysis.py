import google.generativeai as genai
from config import GEMINI_API_KEY

class TextAnalyzer:
    """
    Analyzes text content using the Google Gemini Pro model.
    It provides functionalities for summarization, entity recognition,
    and sentiment analysis tailored for badminton context.
    """
    def __init__(self):
        """Initializes the TextAnalyzer and configures the Gemini API."""
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            print("TextAnalyzer initialized with Gemini Pro.")
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            self.model = None

    def analyze_text(self, text: str, task: str = "summarize") -> str:
        """
        Performs a specified analysis task on the given text.

        Args:
            text (str): The text to be analyzed.
            task (str): The analysis task to perform. 
                        Options: 'summarize', 'extract_entities', 'sentiment'.

        Returns:
            A string containing the analysis result.
        """
        if not self.model:
            return "Text analyzer is not available."

        prompts = {
            "summarize": f"Summarize the following text from a badminton match commentary:\n\n{text}",
            "extract_entities": f"Extract key entities (players, scores, specific shots) from this text:\n\n{text}",
            "sentiment": f"Analyze the sentiment (positive, negative, neutral) of this commentary:\n\n{text}"
        }

        prompt = prompts.get(task.lower())

        if not prompt:
            return f"Unknown task: {task}. Available tasks: summarize, extract_entities, sentiment."

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"An error occurred during text analysis: {e}"

# Example usage:
if __name__ == '__main__':
    analyzer = TextAnalyzer()
    sample_text = "Player A executes a brilliant cross-court smash, winning the point. The score is now 15-10. The crowd is ecstatic."
    
    summary = analyzer.analyze_text(sample_text, task="summarize")
    print("--- Summary ---")
    print(summary)

    entities = analyzer.analyze_text(sample_text, task="extract_entities")
    print("\n--- Entities ---")
    print(entities)

    sentiment = analyzer.analyze_text(sample_text, task="sentiment")
    print("\n--- Sentiment ---")
    print(sentiment)
