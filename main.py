"""Command-line entry point to run badminton agentic analysis."""
import argparse
import os, asyncio, sys, traceback, logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('badminton_analysis.log')
    ]
)
logger = logging.getLogger(__name__)

from badminton_ai.pipeline import run_analysis
from badminton_ai.report_generator import init_gemini


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("video", help="Path to input video")
    p.add_argument("--gemini-key", help="Google Gemini API Key", required=True)
    return p.parse_args()


def main():
    try:
        args = parse_args()
        if not os.path.exists(args.video):
            raise FileNotFoundError(f"Video not found: {args.video}")

        logger.info("Initialising Gemini...")
        init_gemini(args.gemini_key)
        logger.info("Running analysis – this may take a few minutes...")
        
        # run_analysis is async
        report = asyncio.run(run_analysis(args.video, api_key=args.gemini_key))
        
        # Ensure reports directory exists
        reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Create report filename based on input video name
        video_name = os.path.splitext(os.path.basename(args.video))[0]
        out_path = os.path.join(reports_dir, f"{video_name}_coach_report.txt")
        
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"Report successfully saved to {os.path.abspath(out_path)}")
        except IOError as e:
            logger.error(f"Failed to save report: {e}")
            # Fallback to current directory if reports/ fails
            out_path = f"{video_name}_coach_report.txt"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"Report saved to fallback location: {os.path.abspath(out_path)}")

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
