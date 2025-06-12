"""Module for generating professional PDF reports."""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageTemplate, Frame, NextPageTemplate, PageBreak
)
from reportlab.platypus.frames import Frame
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import textwrap
import re
import os

# Standard PDF fonts that work across all platforms
DEFAULT_FONT = 'Helvetica'
DEFAULT_BOLD = 'Helvetica-Bold'
DEFAULT_ITALIC = 'Helvetica-Oblique'
DEFAULT_BOLD_ITALIC = 'Helvetica-BoldOblique'

# Try to register better fonts if available
try:
    # First try to use the default PDF fonts
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase import pdfmetrics
    
    # Register standard PDF fonts without trying to load TTF files
    pdfmetrics.registerFont(pdfmetrics.Font('Helvetica', 'Helvetica'))
    pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-Bold', 'Helvetica-Bold'))
    pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-Oblique', 'Helvetica-Oblique'))
    pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-BoldOblique', 'Helvetica-BoldOblique'))
    
    # Also register the standard Type 1 fonts that come with ReportLab
    pdfmetrics.registerFont(pdfmetrics.Font('Times-Roman', 'Times-Roman'))
    pdfmetrics.registerFont(pdfmetrics.Font('Times-Bold', 'Times-Bold'))
    pdfmetrics.registerFont(pdfmetrics.Font('Times-Italic', 'Times-Italic'))
    pdfmetrics.registerFont(pdfmetrics.Font('Times-BoldItalic', 'Times-BoldItalic'))
    pdfmetrics.registerFont(pdfmetrics.Font('Courier', 'Courier'))
    pdfmetrics.registerFont(pdfmetrics.Font('Courier-Bold', 'Courier-Bold'))
    pdfmetrics.registerFont(pdfmetrics.Font('Courier-Oblique', 'Courier-Oblique'))
    pdfmetrics.registerFont(pdfmetrics.Font('Courier-BoldOblique', 'Courier-BoldOblique'))
    
    # Try to register Noto fonts if available
    try:
        font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        if os.path.exists(font_dir):
            # Look for Noto fonts first
            noto_fonts = [f for f in os.listdir(font_dir) 
                         if f.lower().startswith('noto') and f.lower().endswith('.ttf')]
            for font_file in noto_fonts:
                try:
                    font_name = os.path.splitext(font_file)[0]
                    pdfmetrics.registerFont(TTFont(font_name, os.path.join(font_dir, font_file)))
                    # If we successfully registered a Noto font, use it as default
                    if 'NotoSans' in font_name and 'Bold' not in font_name and 'Italic' not in font_name:
                        DEFAULT_FONT = font_name
                except Exception as e:
                    print(f"Warning: Could not register font {font_file}: {e}")
    except Exception as e:
        print(f"Warning: Could not process font directory: {e}")
        
except Exception as e:
    print(f"Warning: Could not initialize fonts: {e}")
    # Fall back to basic fonts
    from reportlab.pdfbase import pdfmetrics
    DEFAULT_FONT = 'Helvetica'
    DEFAULT_BOLD = 'Helvetica-Bold'
    DEFAULT_ITALIC = 'Helvetica-Oblique'
    DEFAULT_BOLD_ITALIC = 'Helvetica-BoldOblique'

# Define styles
styles = getSampleStyleSheet()

# Function to safely add a style if it doesn't exist
def add_style_if_not_exists(style_name, parent_style='Normal', **kwargs):
    if style_name not in styles:
        styles.add(ParagraphStyle(
            name=style_name,
            parent=styles[parent_style],
            **kwargs
        ))

# Add or update styles
add_style_if_not_exists(
    'Heading1',
    parent_style='Heading1',
    fontSize=16,
    spaceAfter=12,
    alignment=TA_CENTER
)

add_style_if_not_exists(
    'Heading2',
    parent_style='Heading2',
    fontSize=14,
    spaceAfter=6,
    spaceBefore=12
)

add_style_if_not_exists(
    'BodyText',
    parent_style='BodyText',
    spaceAfter=6,
    leading=14,
    alignment=TA_LEFT
)

add_style_if_not_exists(
    'SmallText',
    parent_style='BodyText',
    fontSize=8,
    textColor=colors.grey,
    alignment=TA_CENTER
)

def clean_text(text: str) -> str:
    """Clean up text for PDF by removing unwanted characters and formatting."""
    if not text:
        return ""
        
    # Remove emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    
    # Remove markdown formatting (**text** -> text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    
    # Remove any remaining control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    
    # Clean up any corrupted text patterns
    text = re.sub(r'=+.*?=+', '', text)  # Remove ====== patterns
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    
    # Clean up the text by removing any non-printable characters
    text = ''.join(char for char in text if char.isprintable() or char in '\n\r\t')
    
    # Remove any lines that look like binary or corrupted data
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip lines that look like binary or corrupted data
        if re.search(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', line):
            continue
        # Skip lines that are just symbols or non-text
        if re.match(r'^[^\w\s]+$', line):
            continue
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def create_pdf_report(
    output_path: str,
    title: str,
    player_name: str,
    role: str,
    content: str,
    language: str = 'en',
    logo_path: Optional[str] = None
) -> Path:
    """
    Create a professional PDF report with header, footer, and clean formatting.
    
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
    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Clean and prepare content
    content = clean_text(content)
    
    # Create styles with proper font fallbacks
    styles = getSampleStyleSheet()
    
    # Set default font for all styles
    for style in styles.byName.values():
        if not hasattr(style, 'fontName') or not style.fontName:
            style.fontName = DEFAULT_FONT
    
    # Add custom styles if they don't exist
    if 'ReportTitle' not in styles:
        styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            spaceAfter=24,
            spaceBefore=36,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        ))
    
    if 'SectionHeader' not in styles:
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            leading=20,
            spaceBefore=24,
            spaceAfter=12,
            textColor=colors.HexColor('#2980b9'),
            fontName='Helvetica-Bold',
            borderLeft=4,
            borderColor=colors.HexColor('#3498db'),
            leftPadding=8
        ))
    
    if 'BodyText' not in styles:
        styles.add(ParagraphStyle(
            name='BodyText',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=8,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica',
            wordWrap='LTR',
            splitLongWords=True,
            alignment=TA_LEFT
        ))
        
    # Add bullet point style
    if 'Bullet' not in styles:
        styles.add(ParagraphStyle(
            name='Bullet',
            parent=styles['BodyText'],
            leftIndent=10,
            firstLineIndent=-5,
            spaceBefore=2,
            spaceAfter=2
        ))
    
    if 'Footer' not in styles:
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Italic'],
            fontSize=8,
            alignment=TA_CENTER,
            spaceBefore=12,
            textColor=colors.HexColor('#7f8c8d'),
            fontName='Arial-Italic'  # Changed from Helvetica-Oblique to Arial-Italic
        ))
    
    # Create document with margins
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=90,
        bottomMargin=90,
        title=f"Badminton Analysis Report - {player_name}",
        author="Badminton AI Analysis Tool"
    )
    
    # Create the story with header and title
    from datetime import datetime  # Import here to ensure it's in function scope
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    story = [
        # Header
        Paragraph("BADMINTON AI ANALYSIS", styles['Heading1']),
        Spacer(1, 12),
        Paragraph(f"Player: {player_name}", styles['Normal']),
        Paragraph(f"Report Type: {role.title()}", styles['Normal']),
        Paragraph(f"Date: {current_time}", styles['Normal']),
        Spacer(1, 24),
        # Title
        Paragraph(title.upper(), styles['ReportTitle'])
    ]
    
    # Add content sections
    content_style = styles['BodyText']
    section_style = styles['SectionHeader']
    
    # Split content into sections if they exist
    sections = content.split('\n\n')
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Check if this is a section header (looks like "Section Name: Description")
        if ':' in section and '\n' not in section[:50]:
            # Try to split into title and description
            parts = section.split(':', 1)
            if len(parts) == 2 and len(parts[0]) < 30:  # Likely a section header
                title_part = f"<b>{parts[0].strip()}:</b> {parts[1].strip()}"
                story.append(Paragraph(title_part, section_style))
                continue
        
        # Handle bullet points or numbered lists
        if section.startswith(('- ', '* ', '• ')) or section[0].isdigit() and '. ' in section[:3]:
            # Add bullet points with proper indentation
            for line in section.split('\n'):
                line = line.strip()
                if line.startswith(('- ', '* ', '• ')):
                    line = '• ' + line[2:]
                story.append(Paragraph(line, content_style))
                story.append(Spacer(1, 6))
        else:
            # Regular paragraph
            story.append(Paragraph(section, content_style))
            story.append(Spacer(1, 12))
    
    # Add analysis timestamp and footer
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add timestamp
    story.append(Spacer(1, 24))
    story.append(Paragraph(f"<i>Analysis generated on: {timestamp}</i>", styles['Italic']))
    
    # Footer will be added by the page template
    pass
    
    # Create frame for content
    frame = Frame(
        doc.leftMargin, 
        doc.bottomMargin, 
        doc.width, 
        doc.height,
        leftPadding=0,
        bottomPadding=0,
        rightPadding=0,
        topPadding=0,
        id='normal'
    )
    
    # Add page number and footer
    def add_footer(canvas, doc):
        canvas.saveState()
        
        # Add footer line
        canvas.setStrokeColor(colors.HexColor('#3498db'))
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, 50, doc.width + doc.leftMargin, 50)
        
        # Add page number
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        
        # Use default font for better compatibility
        canvas.setFont(DEFAULT_FONT, 8)
            
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        canvas.drawRightString(doc.width + doc.leftMargin, 30, text)
        
        # Add copyright text
        copyright_text = f"© {datetime.now().year} Badminton AI Analysis Tool | Confidential - For Training Purposes Only"
        
        canvas.setFont(DEFAULT_ITALIC, 8)
            
        canvas.drawString(doc.leftMargin, 30, copyright_text)
        
        # Add logo if available
        if logo_path and Path(logo_path).exists():
            try:
                logo = Image(logo_path, width=40, height=20)
                logo.drawOn(canvas, doc.leftMargin, 20)
            except:
                pass
                
        canvas.restoreState()
    
    # Create page template with footer
    template = PageTemplate(
        id='main',
        frames=frame,
        onPage=add_footer,
        pagesize=letter
    )
    
    # Assign template to document
    doc.addPageTemplates([template])
    
    # Build the PDF
    doc.build(story)
    
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
    
    # Ensure output directory exists
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create output filename
    pdf_filename = f"{Path(txt_path).stem}.pdf"
    pdf_path = str(output_dir_path / pdf_filename)
    
    # Generate title based on role
    role_titles = {
        'coach': f"Badminton Performance Analysis - {player_name}",
        'student': f"Your Badminton Training Report - {player_name}",
        'parent': f"Badminton Progress Report - {player_name}"
    }
    title = role_titles.get(role.lower(), f"Badminton Report - {player_name}")
    
    try:
        # Generate the PDF
        output_path = create_pdf_report(
            output_path=pdf_path,
            title=title,
            player_name=player_name,
            role=role.capitalize(),
            content=content,
            language=language
        )
        print(f"PDF successfully generated at: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise
