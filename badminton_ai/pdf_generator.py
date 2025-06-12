"""Module for generating professional PDF reports."""
from pathlib import Path
from typing import Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import textwrap
import re

# Define styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name='Heading1',
    parent=styles['Heading1'],
    fontSize=16,
    spaceAfter=12,
    alignment=TA_CENTER
))
styles.add(ParagraphStyle(
    name='Heading2',
    parent=styles['Heading2'],
    fontSize=14,
    spaceAfter=6,
    spaceBefore=12
))
styles.add(ParagraphStyle(
    name='BodyText',
    parent=styles['BodyText'],
    spaceAfter=6,
    leading=14,
    alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    name='SmallText',
    parent=styles['BodyText'],
    fontSize=8,
    textColor=colors.grey,
    alignment=TA_CENTER
))

def clean_text(text: str) -> str:
    """Remove emojis and clean up text for PDF."""
    # Remove emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def create_pdf_report(
    output_path: str,
    title: str,
    player_name: str,
    role: str,
    content: str,
    language: str = 'en',
    logo_path: Optional[str] = None
) -> str:
    """
    Create a professional PDF report.
    
    Args:
        output_path: Path to save the PDF
        title: Report title
        player_name: Name of the player
        role: Type of report (coach/student/parent)
        content: Report content
        language: Language code
        logo_path: Optional path to logo image
    
    Returns:
        Path to the generated PDF
    """
    # Clean and prepare content
    content = clean_text(content)
    
    # Create document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40
    )
    
    # Prepare elements
    elements = []
    
    # Add logo if provided
    if logo_path and Path(logo_path).exists():
        logo = Image(logo_path, width=2*inch, height=0.5*inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 20))
    
    # Add title
    elements.append(Paragraph(title.upper(), styles['Heading1']))
    elements.append(Spacer(1, 12))
    
    # Add metadata
    metadata = [
        ["Player:", player_name],
        ["Report Type:", role.capitalize()],
        ["Language:", get_language_name(language)]
    ]
    
    table = Table(metadata, colWidths=[100, 300])
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # Add content sections
    sections = content.split('\n\n')
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Check if this is a section header
        if ':' in section and len(section) < 100:  # Simple heuristic for section headers
            title, content = section.split(':', 1)
            elements.append(Paragraph(title.strip() + ':', styles['Heading2']))
            content = content.strip()
            if content:
                elements.append(Paragraph(content, styles['BodyText']))
        else:
            # Wrap long lines for better readability
            wrapped = '\n'.join(textwrap.wrap(section, width=100))
            elements.append(Paragraph(wrapped, styles['BodyText']))
        
        elements.append(Spacer(1, 6))
    
    # Add footer
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Confidential - For training purposes only", styles['SmallText']))
    
    # Build PDF
    doc.build(elements)
    return output_path

def get_language_name(code: str) -> str:
    """Convert language code to full name."""
    languages = {
        'en': 'English',
        'hi': 'हिंदी (Hindi)',
        'ta': 'தமிழ் (Tamil)',
        'te': 'తెలుగు (Telugu)',
        'kn': 'ಕನ್ನಡ (Kannada)'
    }
    return languages.get(code, code)

def convert_txt_to_pdf(txt_path: str, output_dir: str, role: str, language: str = 'en') -> str:
    """
    Convert a text report to a formatted PDF.
    
    Args:
        txt_path: Path to the text report
        output_dir: Directory to save the PDF
        role: Type of report (coach/student/parent)
        language: Language code
        
    Returns:
        Path to the generated PDF
    """
    # Read the text content
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract player info from filename
    filename = Path(txt_path).stem
    player_match = re.search(r'player(\d+)', filename, re.IGNORECASE)
    player_num = player_match.group(1) if player_match else '1'
    player_name = f"Player {player_num}"
    
    # Create output filename
    pdf_filename = f"{Path(txt_path).stem}.pdf"
    pdf_path = str(Path(output_dir) / pdf_filename)
    
    # Generate title based on role
    role_titles = {
        'coach': f"Badminton Performance Analysis - {player_name}",
        'student': f"Your Badminton Training Report - {player_name}",
        'parent': f"Badminton Progress Report - {player_name}"
    }
    title = role_titles.get(role.lower(), f"Badminton Report - {player_name}")
    
    # Generate the PDF
    return create_pdf_report(
        output_path=pdf_path,
        title=title,
        player_name=player_name,
        role=role.capitalize(),
        content=content,
        language=language
    )
