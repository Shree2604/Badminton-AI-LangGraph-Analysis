"""
Command-line entry point for parallel badminton video analysis with role-based reporting.
Generates detailed analysis reports for coaches, players, and parents using parallel processing.
"""
import argparse
import os
import asyncio
import sys
import logging
import shutil
import platform
from datetime import datetime
from pathlib import Path
from typing import List, Literal, Optional, Dict, Any, Tuple, Callable, Union

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

# Platform-specific optimizations
if platform.system() == 'Windows':
    # Windows-specific optimizations
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Local imports
try:
    from badminton_ai.pipeline import run_analysis
    from badminton_ai.report_generator import init_gemini, generate_report
    from badminton_ai.pdf_generator import convert_txt_to_pdf
    from badminton_ai.video_utils import extract_frames, analyze_pose
    from badminton_ai.audio_utils import extract_audio, transcribe
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    raise

# Type aliases
ReportRole = Literal["coach", "student", "parent"]

def get_language_choice() -> str:
    """Prompt user to select a language from available options."""
    languages = {
        "1": {"code": "en", "name": "English"},
        "2": {"code": "hi", "name": "हिंदी (Hindi)"},
        "3": {"code": "ta", "name": "தமிழ் (Tamil)"},
        "4": {"code": "te", "name": "తెలుగు (Telugu)"},
        "5": {"code": "kn", "name": "ಕನ್ನಡ (Kannada)"}
    }
    
    print("\n" + "="*50)
    print("SELECT REPORT LANGUAGE")
    print("="*50)
    for key, lang in languages.items():
        print(f"{key}. {lang['name']}")
    print("="*50)
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice in languages:
            return languages[choice]["code"]
        print("Invalid choice. Please enter a number between 1 and 5.")


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"{title:^70}")
    print("="*70)


def get_video_path() -> str:
    """Prompt user for video file path with validation."""
    while True:
        video_path = input("\n📹 Enter the path to your badminton video file: ").strip('"')
        if os.path.isfile(video_path):
            return video_path
        print("❌ File not found. Please enter a valid file path.")


def get_gemini_key() -> str:
    """Prompt user for Gemini API key."""
    print("\n🔑 You'll need a Google Gemini API key to continue.")
    print("   Get it from: https://aistudio.google.com/app/apikey")
    while True:
        api_key = input("\n🔑 Enter your Google Gemini API key: ").strip()
        if api_key:
            return api_key
        print("❌ API key cannot be empty. Please try again.")


def get_player_count() -> int:
    """Prompt user for number of players."""
    while True:
        try:
            count = int(input("\n👥 Enter number of players (1 or 2): "))
            if count in (1, 2):
                return count
            print("❌ Please enter 1 or 2.")
        except ValueError:
            print("❌ Please enter a valid number (1 or 2).")


def get_roles() -> list[str]:
    """Prompt user to select report roles."""
    print("\n📋 Select which reports to generate:")
    print("1. Coach Report (Detailed technical analysis)")
    print("2. Student Report (Player-focused feedback)")
    print("3. Parent Report (General progress summary)")
    print("4. All Reports")
    
    role_map = {
        "1": ["coach"],
        "2": ["student"],
        "3": ["parent"],
        "4": ["coach", "student", "parent"]
    }
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        if choice in role_map:
            return role_map[choice]
        print("❌ Invalid choice. Please enter a number between 1 and 4.")


def get_language_choice() -> str:
    """Prompt user to select a language from available options."""
    languages = {
        "1": {"code": "en", "name": "English"},
        "2": {"code": "hi", "name": "हिंदी (Hindi)"},
        "3": {"code": "ta", "name": "தமிழ் (Tamil)"},
        "4": {"code": "te", "name": "తెలుగు (Telugu)"},
        "5": {"code": "kn", "name": "ಕನ್ನಡ (Kannada)"}
    }
    
    print("\n🌍 Select report language:")
    for key, lang in languages.items():
        print(f"{key}. {lang['name']}")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice in languages:
            return languages[choice]["code"]
        print("❌ Invalid choice. Please enter a number between 1 and 5.")


def confirm_settings(settings: dict) -> bool:
    """Display settings and confirm before proceeding."""
    print_header("REVIEW SETTINGS")
    for key, value in settings.items():
        print(f"{key}: {value}")
    
    while True:
        confirm = input("\nStart analysis with these settings? (y/n): ").lower()
        if confirm in ('y', 'n'):
            return confirm == 'y'
        print("❌ Please enter 'y' to continue or 'n' to cancel.")


def ensure_directory(directory: str) -> Path:
    """Ensure the output directory exists."""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


async def generate_reports(
    video_path: str,
    output_dir: Path,
    gemini_key: str,
    num_players: int,
    roles: List[ReportRole],
    locale: str
) -> Dict[str, Dict[str, str]]:
    """
    Generate reports for specified roles and players using parallel processing.
    
    Args:
        video_path: Path to the input video file
        output_dir: Directory to save generated reports
        gemini_key: API key for Gemini
        num_players: Number of players in the video (1 or 2)
        roles: List of report roles to generate (coach, student, parent)
        locale: Language/locale code for the reports
        
    Returns:
        Dictionary mapping report identifiers to their file paths
    """
    def progress_callback(progress: Dict[str, Any]) -> None:
        """Handle progress updates from the analysis pipeline."""
        step = progress.get('step', 'unknown')
        percent = int(progress.get('progress', 0) * 100)
        elapsed = f"{progress.get('timestamp', 0):.1f}s"
        print(f"\r[Progress] {step.capitalize()}: {percent}% ({elapsed})", end="")
        if percent >= 100:
            print()  # New line when complete

    try:
        # Initialize Gemini
        init_gemini(gemini_key)
        
        # Create output directories
        text_dir = output_dir / "text_reports"
        pdf_dir = output_dir / "pdf_reports"
        ensure_directory(text_dir)
        ensure_directory(pdf_dir)
        
        # Track generated reports
        reports: Dict[str, Dict[str, str]] = {}
        video_name = Path(video_path).stem
        
        # Run the enhanced analysis pipeline with progress updates
        logger.info("Starting parallel video analysis...")
        print("\n" + "="*50)
        print("VIDEO ANALYSIS IN PROGRESS")
        print("="*50)
        
        analysis_results = await run_analysis(
            video_path=video_path,
            api_key=gemini_key,
            callback=progress_callback
        )
        
        # Check for analysis errors
        if analysis_results.get('errors'):
            for error in analysis_results['errors']:
                logger.error(f"Analysis error in {error.get('step')}: {error.get('error')}")
        
        # Generate reports for each role and player in parallel
        logger.info("\nGenerating reports...")
        report_tasks = []
        
        for player_num in range(1, num_players + 1):
            for role in roles:
                report_id = f"player{player_num}_{role}"
                report_tasks.append(
                    generate_single_report(
                        analysis_results=analysis_results,
                        video_name=video_name,
                        player_num=player_num,
                        role=role,
                        locale=locale,
                        text_dir=text_dir,
                        pdf_dir=pdf_dir
                    )
                )
        
        # Run report generation in parallel
        report_results = await asyncio.gather(*report_tasks, return_exceptions=True)
        
        # Process results
        for result in report_results:
            if isinstance(result, Exception):
                logger.error(f"Report generation failed: {str(result)}")
                continue
            if result:
                reports.update(result)
        
        # Create README file with analysis summary
        create_readme_file(
            output_dir=output_dir,
            video_name=video_name,
            num_players=num_players,
            roles=roles,
            locale=locale
        )
        
        logger.info("\n" + "="*50)
        logger.info("ANALYSIS COMPLETE")
        logger.info("="*50)
        
        # Print summary of generated reports
        print("\n" + "="*50)
        print("GENERATED REPORTS")
        print("="*50)
        for report_id, paths in reports.items():
            print(f"\n{report_id.upper()}:")
            print(f"  Text: {paths['txt']}")
            print(f"  PDF:  {paths['pdf']}")
        
        print("\n" + "="*50)
        print(f"Analysis completed successfully! Reports saved to: {output_dir}")
        
        return reports
        
    except Exception as e:
        logger.exception("Fatal error in report generation")
        raise

async def generate_single_report(
    analysis_results: Dict[str, Any],
    video_name: str,
    player_num: int,
    role: str,
    locale: str,
    text_dir: Path,
    pdf_dir: Path
) -> Dict[str, Dict[str, str]]:
    """Generate a single report and its PDF version."""
    try:
        report_id = f"player{player_num}_{role}"
        logger.info(f"Generating {role} report for Player {player_num}...")
        
        # Generate report content
        report = generate_report(
            pose_metrics=analysis_results.get("pose", []),
            transcription=analysis_results.get("transcript", ""),
            role=role,
            player_num=player_num,
            locale=locale
        )
        
        # Save text report
        report_filename = f"{video_name}_{report_id}_report.txt"
        report_path = text_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Generate PDF report
        pdf_filename = f"{video_name}_{report_id}_report.pdf"
        pdf_path = pdf_dir / pdf_filename
        
        convert_txt_to_pdf(
            str(report_path),
            str(pdf_path),
            title=f"Badminton Analysis - Player {player_num} ({role.capitalize()})",
            language=locale
        )
        
        logger.info(f"Generated reports for {report_id}: {report_path}, {pdf_path}")
        
        return {
            report_id: {
                'txt': str(report_path),
                'pdf': str(pdf_path)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating {role} report for Player {player_num}: {str(e)}")
        raise


def create_readme_file(output_dir: Path, video_name: str, num_players: int, 
                      roles: List[str], locale: str) -> None:
    """Create a README file in the output directory."""
    readme_path = output_dir / 'README.txt'
    
    content = f"""Badminton AI Analysis Report
{'=' * 80}

This directory contains the analysis reports for the video: {video_name}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Language: {get_language_name(locale)}
Number of Players: {num_players}
Report Types: {', '.join(roles)}

Directory Structure:
- text_reports/: Contains the raw text reports
- pdf_reports/: Contains the formatted PDF reports

Each report is named in the format:
<video_name>_player<number>_<role>_report.<txt|pdf>

Example: {video_name}_player1_coach_report.pdf
"""
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)


def print_loading_bar(progress: int, total: int, message: str = ""):
    """Display a simple loading bar."""
    bar_length = 40
    filled_length = int(bar_length * progress / total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    percentage = int(100 * progress / total)
    print(f"\r{message} [{bar}] {percentage}%", end="")
    if progress == total:
        print()  # New line when complete


def generate_pdf_report(txt_path: str, output_dir: Path, role: str, language: str) -> Optional[str]:
    """Generate a PDF version of the text report."""
    try:
        print(f"   📄 Creating PDF for {Path(txt_path).name}...")
        pdf_path = convert_txt_to_pdf(
            txt_path=txt_path,
            output_dir=output_dir,
            role=role,
            language=language
        )
        return pdf_path
    except Exception as e:
        logger.error(f"Error generating PDF for {txt_path}: {str(e)}", exc_info=True)
        return None

async def generate_reports(
    video_path: str,
    output_dir: Path,
    gemini_key: str,
    num_players: int,
    roles: List[str],
    locale: str
) -> Dict[str, Dict[str, str]]:
    """
    Generate text and PDF reports with progress updates.
    
    Returns:
        Dictionary containing paths to generated files:
        {
            'player1_coach': {'txt': 'path/to/txt', 'pdf': 'path/to/pdf'},
            'player1_student': {'txt': 'path/to/txt', 'pdf': 'path/to/pdf'},
            ...
        }
    """
    try:
        # Initialize Gemini
        init_gemini(gemini_key)
        
        # Create text and PDF subdirectories
        txt_dir = output_dir / 'text_reports'
        pdf_dir = output_dir / 'pdf_reports'
        txt_dir.mkdir(parents=True, exist_ok=True)
        pdf_dir.mkdir(parents=True, exist_ok=True)
        
        # Run the analysis pipeline with progress updates
        print("\n🔍 Analyzing video...")
        analysis_results = await run_analysis(video_path, api_key=gemini_key)
        
        # Generate reports for each role and player
        reports = {}
        video_name = Path(video_path).stem
        total_reports = num_players * len(roles)
        completed = 0
        
        for player_num in range(1, num_players + 1):
            for role in roles:
                report_key = f"player{player_num}_{role}"
                reports[report_key] = {}
                
                try:
                    # Update progress
                    completed += 1
                    print_loading_bar(
                        completed, total_reports,
                        f"📝 Generating {role} report for Player {player_num}..."
                    )
                    
                    # Generate and save text report
                    report = generate_report(
                        pose_metrics=analysis_results.get("pose_metrics", []),
                        transcription=analysis_results.get("transcription", ""),
                        role=role,
                        player_num=player_num,
                        locale=locale
                    )
                    
                    # Save text report
                    txt_filename = f"{video_name}_player{player_num}_{role}_report.txt"
                    txt_path = txt_dir / txt_filename
                    
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(report)
                    
                    reports[report_key]['txt'] = str(txt_path.resolve())
                    
                    # Generate PDF report
                    pdf_path = generate_pdf_report(
                        txt_path=str(txt_path),
                        output_dir=pdf_dir,
                        role=role,
                        language=locale
                    )
                    
                    if pdf_path:
                        reports[report_key]['pdf'] = pdf_path
                    
                except Exception as e:
                    error_msg = f"Error generating {role} report for Player {player_num}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    reports[f"{report_key}_error"] = error_msg
        
        # Create a README file in the output directory
        create_readme_file(output_dir, video_name, num_players, roles, locale)
        
        return reports
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise


async def main_async():
    """Async main entry point for the parallel badminton analysis."""
    clear_screen()
    print_header("PARALLEL BADMINTON AI ANALYSIS TOOL")
    
    try:
        # Get user inputs
        video_path = get_video_path()
        gemini_key = get_gemini_key()
        num_players = get_player_count()
        roles = get_roles()
        locale = get_language_choice()
        
        # Confirm settings
        settings = {
            "Video Path": video_path,
            "Number of Players": num_players,
            "Report Types": ", ".join(roles),
            "Language": get_language_name(locale),
            "Processing Mode": "Parallel"
        }
        
        if not confirm_settings(settings):
            print("\nOperation cancelled by user.")
            return
        
        # Create output directories
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("reports") / f"analysis_{timestamp}"
        (output_dir / "text_reports").mkdir(parents=True, exist_ok=True)
        (output_dir / "pdf_reports").mkdir(parents=True, exist_ok=True)
        
        # Display processing information
        print("\n" + "="*50)
        print("PARALLEL PROCESSING STARTED")
        print("="*50)
        print(f"Using up to {multiprocessing.cpu_count()} CPU cores")
        print(f"Reports will be saved to: {output_dir.absolute()}")
        
        # Generate reports with progress tracking
        reports = await generate_reports(
            video_path=video_path,
            output_dir=output_dir,
            gemini_key=gemini_key,
            num_players=num_players,
            roles=roles,
            locale=locale
        )
        
        # Print summary of generated files
        print("\n" + "="*50)
        print("ANALYSIS COMPLETE")
        print("="*50)
        
        # Show generated files by category
        print("\nGenerated Reports:")
        print("-" * 50)
        
        text_reports = output_dir / "text_reports"
        pdf_reports = output_dir / "pdf_reports"
        
        print("\nText Reports:")
        for file in sorted(text_reports.glob("*.txt")):
            print(f"- {file.name}")
            
        print("\nPDF Reports:")
        for file in sorted(pdf_reports.glob("*.pdf")):
            print(f"- {file.name}")
        
        # Create README file with analysis summary
        create_readme_file(
            output_dir=output_dir,
            video_name=Path(video_path).stem,
            num_players=num_players,
            roles=roles,
            locale=locale
        )
        print(f"✅ Analysis completed successfully!")
        print(f"📄 Reports are available in: {output_dir.resolve()}")
        print("="*60)
        
        input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        print(f"\n❌ An error occurred: {str(e)}")
        print("Check the log file for more details.")
        input("\nPress Enter to exit...")
    
    logger.info("Analysis completed successfully")


def main():
    """Synchronous entry point that runs the async main function."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        logger.exception("Application error")
        sys.exit(1)

if __name__ == "__main__":
    main()
