"""Generate role-based badminton analysis reports from multimodal data."""
from typing import Dict, List, Literal, Optional
import textwrap
from pathlib import Path
import json

from google.generativeai import configure, GenerativeModel

# Type aliases
ReportRole = Literal["coach", "student", "parent"]

def init_gemini(api_key: str):
    """Initialize the Gemini API client."""
    configure(api_key=api_key)


def _get_role_prompt(role: ReportRole, player_num: int, locale: str) -> str:
    """Get the appropriate system prompt based on role and player number."""
    player_ref = f"Player {player_num}" if player_num > 0 else "the player"
    
    prompts = {
        "coach": textwrap.dedent(f"""
        You are an elite badminton coach analyzing a match with {player_ref}.
        Provide a detailed technical analysis with specific, actionable feedback.
        Focus on technical corrections, tactical improvements, and measurable metrics.
        """),
        
        "student": textwrap.dendet(f"""
        You are a supportive badminton coach providing feedback directly to {player_ref}.
        Use an encouraging, constructive tone. Focus on 2-3 key areas for improvement.
        Include specific drills or exercises to practice.
        """),
        
        "parent": textwrap.dedent(f"""
        You are providing feedback to {player_ref}'s parent/guardian.
        Focus on progress, effort, and development areas in non-technical terms.
        Highlight positive aspects and suggest how they can support {player_ref}'s development.
        """)
    }
    
    base_prompt = prompts.get(role, prompts["coach"])
    return f"{base_prompt}\n\nPlease provide the report in {locale} language.\n"


def _get_report_structure(role: ReportRole) -> str:
    """Get the appropriate report structure based on role."""
    structures = {
        "coach": """
        1. Technical Performance (stance, grip, swing mechanics)
        2. Tactical Analysis (shot selection, court coverage)
        3. Physical Metrics (speed, endurance, reaction time)
        4. Key Areas for Improvement (with specific drills)
        5. Next Training Focus
        """,
        "student": """
        1. What Went Well (2-3 strengths)
        2. Key Areas to Work On (2-3 focus areas)
        3. Practice Drills (specific exercises to improve)
        4. Weekly Goals
        """,
        "parent": """
        1. Overall Performance Summary
        2. Key Strengths to Encourage
        3. Development Areas
        4. How You Can Help (support suggestions)
        5. Next Steps
        """
    }
    return structures.get(role, structures["coach"])


def generate_report(
    pose_metrics: List[Dict], 
    transcription: str, 
    role: ReportRole = "coach",
    player_num: int = 1,
    locale: str = "en"
) -> str:
    """
    Generate a role-specific badminton analysis report.
    
    Args:
        pose_metrics: List of pose detection metrics
        transcription: Text transcription of audio
        role: Target audience for the report (coach/student/parent)
        player_num: Player number (1 or 2)
        locale: Language code for the report
        
    Returns:
        Formatted analysis report
    """
    try:
        # Get role-specific prompt and structure
        role_prompt = _get_role_prompt(role, player_num, locale)
        structure = _get_report_structure(role)
        
        # Prepare analysis data
        analysis_data = {
            "player": f"Player {player_num}",
            "pose_metrics": pose_metrics[:100],  # Sample to avoid huge context
            "transcription": transcription,
        }
        
        # Create the full prompt
        system_prompt = textwrap.dedent(f"""
        {role_prompt}
        
        Report Structure:
        {structure}
        
        Analysis Guidelines:
        - Be specific and actionable in your feedback
        - Reference the pose data when relevant (confidence > 0.3)
        - Include timestamps for key moments when possible
        - Provide concrete examples from the match
        - Keep the tone professional but approachable
        - Use bullet points for clarity
        - Focus on observable behaviors and metrics
        """)
        
        # Generate the report
        model = GenerativeModel("gemini-1.5-flash")
        prompt = f"{system_prompt}\n\nAnalysis Data (first 100 pose metrics shown):\n{json.dumps(analysis_data, indent=2)[:2000]}"
        
        response = model.generate_content(prompt)
        report = response.text
        
        # Add header and format
        header = f"BADMINTON ANALYSIS REPORT\n" \
                f"Role: {role.title()}\n" \
                f"Player: {player_num}\n" \
                f"Language: {locale.upper()}\n" \
                f"{"="*50}\n\n"
                
        return header + report
        
    except Exception as e:
        error_msg = f"Error generating {role} report: {str(e)}"
        logging.error(error_msg)
        return f"Error generating report: {error_msg}"
