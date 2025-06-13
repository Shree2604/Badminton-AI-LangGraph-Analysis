"""Module for generating professional PDF reports."""
# Global font variables - must be declared at module level before any assignments
global DEFAULT_FONT_FAMILY, DEFAULT_FONT, DEFAULT_BOLD, DEFAULT_ITALIC, DEFAULT_BOLD_ITALIC

# Default to Noto Sans for better Unicode support
DEFAULT_FONT_FAMILY = 'NotoSans'
DEFAULT_FONT = 'NotoSans'
DEFAULT_BOLD = 'NotoSans-Bold'
DEFAULT_ITALIC = 'NotoSans-Italic'
DEFAULT_BOLD_ITALIC = 'NotoSans-BoldItalic'

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageTemplate, Frame, NextPageTemplate, PageBreak, ListFlowable, ListItem
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
import sys
import requests
import zipfile
import io

# Define a single consistent font family for the entire document
# DejaVu fonts support a wide range of Unicode characters
DEFAULT_FONT_FAMILY = 'DejaVuSans'
DEFAULT_FONT = f'{DEFAULT_FONT_FAMILY}'
DEFAULT_BOLD = f'{DEFAULT_FONT_FAMILY}-Bold'
DEFAULT_ITALIC = f'{DEFAULT_FONT_FAMILY}-Oblique'
DEFAULT_BOLD_ITALIC = f'{DEFAULT_FONT_FAMILY}-BoldOblique'

# Font size consistency
DEFAULT_FONT_SIZE = 11
HEADING1_FONT_SIZE = 16
HEADING2_FONT_SIZE = 14
SMALL_FONT_SIZE = 8

# Define font download URLs and directory
FONT_URLS = {
    'dejavu': "https://sourceforge.net/projects/dejavu/files/dejavu/2.37/dejavu-fonts-ttf-2.37.zip/download",
    'noto': "https://github.com/googlefonts/noto-fonts/archive/refs/heads/main.zip"
}
FONT_DIR = os.path.join(os.path.dirname(__file__), 'fonts')

# Indian language font mapping
INDIAN_LANGUAGE_FONTS = {
    'hi': 'NotoSansDevanagari',  # Hindi
    'ta': 'NotoSansTamil',      # Tamil
    'te': 'NotoSansTelugu',     # Telugu
    'kn': 'NotoSansKannada',    # Kannada
    'ml': 'NotoSansMalayalam',  # Malayalam
    'bn': 'NotoSansBengali',    # Bengali
    'gu': 'NotoSansGujarati',   # Gujarati
    'pa': 'NotoSansGurmukhi',   # Punjabi
    'or': 'NotoSansOriya',      # Odia
    'as': 'NotoSansBengali',    # Assamese (using Bengali as fallback)
    'mr': 'NotoSansDevanagari'  # Marathi
}

def download_and_extract_fonts():
    os.makedirs(FONT_DIR, exist_ok=True)
    
    # Download and extract Noto fonts (for better Unicode support)
    noto_fonts = [
        'NotoSans-Regular.ttf', 'NotoSans-Bold.ttf', 'NotoSans-Italic.ttf', 'NotoSans-BoldItalic.ttf',
        'NotoSansDevanagari-Regular.ttf', 'NotoSansTamil-Regular.ttf', 'NotoSansTelugu-Regular.ttf',
        'NotoSansKannada-Regular.ttf', 'NotoSansMalayalam-Regular.ttf', 'NotoSansBengali-Regular.ttf',
        'NotoSansGujarati-Regular.ttf', 'NotoSansGurmukhi-Regular.ttf', 'NotoSansOriya-Regular.ttf'
    ]
    
    # Check if we have all required fonts
    missing_fonts = [f for f in noto_fonts if not os.path.exists(os.path.join(FONT_DIR, f))]
    
    if missing_fonts:
        print(f"[INFO] Missing {len(missing_fonts)} Noto font files. Attempting to download...")
        try:
            # Download Noto fonts from Google Fonts
            response = requests.get(FONT_URLS['noto'], stream=True)
            response.raise_for_status()
            
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # Extract only the required font files
                for member in z.namelist():
                    if 'hinted/ttf/' in member and any(font in member for font in noto_fonts):
                        filename = os.path.basename(member)
                        if filename in noto_fonts:  # Only extract the ones we need
                            target_path = os.path.join(FONT_DIR, filename)
                            with open(target_path, 'wb') as outfile:
                                outfile.write(z.read(member))
                            print(f"[INFO] Extracted {filename} to {FONT_DIR}")
            
            print("[INFO] Noto fonts downloaded and extracted successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to download or extract Noto fonts: {e}")
    else:
        print("[INFO] All required Noto fonts are available.")

# Call this function before font registration
download_and_extract_fonts()

# Initialize default fonts (standard PDF fonts)
DEFAULT_FONT_FAMILY = 'Helvetica'
DEFAULT_FONT = 'Helvetica'
DEFAULT_BOLD = 'Helvetica-Bold'
DEFAULT_ITALIC = 'Helvetica-Oblique'
DEFAULT_BOLD_ITALIC = 'Helvetica-BoldOblique'

# Try to register better fonts if available
try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont, TTFontFace, TTFontFile, TTFOpenFile
    from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
    from reportlab.lib.fonts import addMapping
    
    # Standard PDF fonts are always available, no need to register them
    
    
    # Try to register Noto fonts first (better Unicode support)
    noto_found = False
    noto_font_files = {
        'NotoSans-Regular.ttf': 'NotoSans',
        'NotoSans-Bold.ttf': 'NotoSans-Bold',
        'NotoSans-Italic.ttf': 'NotoSans-Italic',
        'NotoSans-BoldItalic.ttf': 'NotoSans-BoldItalic',
    }
    
    # Also try DejaVu as fallback
    dejavu_found = False
    dejavu_font_files = {
        'DejaVuSans.ttf': 'DejaVuSans',
        'DejaVuSans-Bold.ttf': 'DejaVuSans-Bold',
        'DejaVuSans-Oblique.ttf': 'DejaVuSans-Oblique',
        'DejaVuSans-BoldOblique.ttf': 'DejaVuSans-BoldOblique',
    }

    all_dejavu_registered = True
    for font_file, font_name in dejavu_font_files.items():
        full_path = os.path.join(FONT_DIR, font_file)
        if os.path.exists(full_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, full_path))
            except Exception as e:
                all_dejavu_registered = False
                break
        else:
            all_dejavu_registered = False
            break

    if all_dejavu_registered:
        dejavu_found = True
        # These assignments are now to the global variables
        DEFAULT_FONT_FAMILY = 'DejaVuSans'
        DEFAULT_FONT = 'DejaVuSans'
        DEFAULT_BOLD = 'DejaVuSans-Bold'
        DEFAULT_ITALIC = 'DejaVuSans-Oblique'
        DEFAULT_BOLD_ITALIC = 'DejaVuSans-BoldOblique'
        pass
    else:
        pass

    # If DejaVu fonts not fully registered, try to use Noto fonts
    # Try to register Noto fonts first
    all_noto_registered = True
    for font_file, font_name in noto_font_files.items():
        full_path = os.path.join(FONT_DIR, font_file)
        if os.path.exists(full_path):
            try:
                # Register the font with proper encoding
                font = TTFont(font_name, full_path, 'UTF-8')
                pdfmetrics.registerFont(font)

                
                # Set as default if this is the regular variant
                if font_name == 'NotoSans':
                    DEFAULT_FONT = 'NotoSans'
                    DEFAULT_FONT_FAMILY = 'NotoSans'
                    DEFAULT_BOLD = 'NotoSans-Bold'
                    DEFAULT_ITALIC = 'NotoSans-Italic'
                    DEFAULT_BOLD_ITALIC = 'NotoSans-BoldItalic'
                    noto_found = True
            except Exception as e:
                all_noto_registered = False
        else:
            print(f"[WARNING] Required Noto font not found: {full_path}")
            all_noto_registered = False

    if all_noto_registered:
        print("[INFO] Successfully registered all essential Noto fonts.")
        # Register the font family
        try:
            registerFontFamily(
                'NotoSans',
                normal='NotoSans',
                bold='NotoSans-Bold',
                italic='NotoSans-Italic',
                boldItalic='NotoSans-BoldItalic'
            )
        except Exception as e:
            pass
    else:
        # Fall back to DejaVu if Noto failed
        if not noto_found:
            all_dejavu_registered = True
            for font_file, font_name in dejavu_font_files.items():
                full_path = os.path.join(FONT_DIR, font_file)
                if os.path.exists(full_path):
                    try:
                        font = TTFont(font_name, full_path, 'UTF-8')
                        pdfmetrics.registerFont(font)
                        print(f"[DEBUG] Registered DejaVu font: {font_name} from {full_path}")
                        
                        if font_name == 'DejaVuSans':
                            DEFAULT_FONT = 'DejaVuSans'
                            DEFAULT_FONT_FAMILY = 'DejaVuSans'
                            DEFAULT_BOLD = 'DejaVuSans-Bold'
                            DEFAULT_ITALIC = 'DejaVuSans-Oblique'
                            DEFAULT_BOLD_ITALIC = 'DejaVuSans-BoldOblique'
                            dejavu_found = True
                    except Exception as e:
                        print(f"[ERROR] Could not register DejaVu font {font_file} from {full_path}: {e}")
                        all_dejavu_registered = False
                else:
                    print(f"[WARNING] Required DejaVu font not found: {full_path}")
                    all_dejavu_registered = False

            if all_dejavu_registered and dejavu_found:
                print("[INFO] Successfully registered all essential DejaVu fonts.")
                # Register the font family
                try:
                    registerFontFamily(
                        'DejaVuSans',
                        normal='DejaVuSans',
                        bold='DejaVuSans-Bold',
                        italic='DejaVuSans-Oblique',
                        boldItalic='DejaVuSans-BoldOblique'
                    )
                except Exception as e:
                    print(f"[WARNING] Could not register DejaVu font family: {e}")
            else:
                print("[INFO] Not all essential DejaVu fonts could be registered.")
                
    # Final fallback to Helvetica if no other fonts were registered
    if not noto_found and not dejavu_found:
        print("[WARNING] Neither Noto nor DejaVu fonts were found. Using Helvetica as fallback font. Non-Latin scripts may not display correctly.")
        DEFAULT_FONT_FAMILY = 'Helvetica'
        DEFAULT_FONT = 'Helvetica'
        DEFAULT_BOLD = 'Helvetica-Bold'
        DEFAULT_ITALIC = 'Helvetica-Oblique'
        DEFAULT_BOLD_ITALIC = 'Helvetica-BoldOblique'
        
except Exception as e:
    print(f"[CRITICAL] Could not initialize fonts: {e}")
    # Fall back to basic fonts
    DEFAULT_FONT_FAMILY = 'Helvetica'
    DEFAULT_FONT = 'Helvetica'
    DEFAULT_BOLD = 'Helvetica-Bold'
    DEFAULT_ITALIC = 'Helvetica-Oblique'
    DEFAULT_BOLD_ITALIC = 'Helvetica-BoldOblique'
    print("[INFO] Falling back to Helvetica due to font initialization error.")

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

# Add or update styles with consistent font family and sizes
add_style_if_not_exists(
    'Heading1',
    parent_style='Heading1',
    fontSize=HEADING1_FONT_SIZE,
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName=DEFAULT_BOLD
)

add_style_if_not_exists(
    'Heading2',
    parent_style='Heading2',
    fontSize=HEADING2_FONT_SIZE,
    spaceAfter=6,
    spaceBefore=12,
    fontName=DEFAULT_BOLD
)

add_style_if_not_exists(
    'BodyText',
    parent_style='BodyText',
    fontSize=DEFAULT_FONT_SIZE,
    spaceAfter=6,
    leading=14,
    alignment=TA_LEFT,
    fontName=DEFAULT_FONT
)

add_style_if_not_exists(
    'SmallText',
    parent_style='BodyText',
    fontSize=SMALL_FONT_SIZE,
    textColor=colors.grey,
    alignment=TA_CENTER,
    fontName=DEFAULT_FONT
)

# Enhanced bullet point styles with better spacing and indentation
add_style_if_not_exists(
    'BulletPoint',
    parent_style='BodyText',
    fontSize=DEFAULT_FONT_SIZE,
    leading=14,
    leftIndent=20,
    firstLineIndent=0,
    spaceBefore=0,
    spaceAfter=0,
    fontName=DEFAULT_FONT,
    bulletFontName=DEFAULT_FONT,
    bulletIndent=10,
    bulletColor=colors.black,
    bulletFontSize=10,
    bulletOffsetY=2,
    textColor=colors.black
)

# Add a style for numbered lists
add_style_if_not_exists(
    'NumberedList',
    parent_style='BulletPoint',
    leftIndent=25,
    bulletIndent=5,
    bulletFontName=f"{DEFAULT_FONT}-Bold" if f"{DEFAULT_FONT}-Bold" in pdfmetrics.getRegisteredFontNames() else DEFAULT_FONT
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
    text = emoji_pattern.sub('', text)
    
    # Remove any remaining control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    
    # Clean up any corrupted text patterns
    text = re.sub(r'=+.*?=+', '', text)  # Remove ====== patterns
    
    # Clean up the text by removing any non-printable characters
    text = ''.join(char for char in text if char.isprintable() or char in '\n\r\t')
    
    # Process markdown formatting
    # Convert bold (**text**) to <b>text</b> for proper rendering
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # Process bullet points - we'll handle these specially in the document building
    # but we need to standardize them first
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip lines that look like binary or corrupted data
        if re.search(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', line):
            continue
        # Skip lines that are just symbols or non-text
        if re.match(r'^[^\w\s]+$', line):
            continue
            
        # Standardize bullet points (* or - or •) to a consistent format
        # We'll use • as our standard bullet point character
        if line.strip().startswith(('* ', '- ', '• ')):
            # Replace the bullet character with a standard one
            line = '• ' + line.strip()[2:]
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def process_bullet_points(text: str) -> List:
    """
    Process text to extract bullet points and convert to proper ListFlowable items.
    
    Supports different bullet styles:
    - • for regular bullet points
    - - for second level bullet points
    - * for third level bullet points
    - 1., 2., 3. for numbered lists
    """
    story = []
    current_paragraph = []
    bullet_stack = []  # Stack to track nested bullet points
    
    def add_bullet_list(items, level=0, bullet_type='bullet'):
        """Helper function to add a bullet list with proper indentation."""
        if not items:
            return
            
        # Define bullet characters based on level and type
        if bullet_type == 'number':
            bullet_char = '1'  # Will be auto-incremented by ListFlowable
        else:
            bullets = ['•', '◦', '▪']  # Different bullets for different levels
            bullet_char = bullets[level % len(bullets)]
        
        # Define indentation based on level
        left_indent = 20 + (level * 15)
        bullet_indent = 10 + (level * 15)
        
        # Create bullet list with proper styling
        bullet_style = styles['BulletPoint'].clone('BulletPoint' + str(level))
        bullet_style.leftIndent = left_indent
        bullet_style.bulletIndent = bullet_indent
        
        # Create list items with proper styling
        list_items = []
        for item in items:
            if isinstance(item, tuple):
                # Handle nested lists
                nested_items, nested_level = item
                list_items.extend(add_bullet_list(nested_items, nested_level, bullet_type))
            else:
                # Handle regular bullet points
                list_items.append(ListItem(Paragraph(item, bullet_style)))
        
        # Create the list flowable
        if bullet_type == 'number':
            return [ListFlowable(
                list_items,
                bulletType='1',
                start='1',
                bulletFontName=bullet_style.fontName,
                leftIndent=left_indent,
                bulletIndent=bullet_indent,
                bulletColor=colors.black,
                spaceBefore=6 if level == 0 else 0,
                spaceAfter=6 if level == 0 else 0
            )]
        else:
            return [ListFlowable(
                list_items,
                bulletType='bullet',
                start=bullet_char,
                bulletFontName=bullet_style.fontName,
                leftIndent=left_indent,
                bulletIndent=bullet_indent,
                bulletColor=colors.black,
                spaceBefore=6 if level == 0 else 0,
                spaceAfter=6 if level == 0 else 0
            )]
    
    # Process each line
    for line in text.split('\n'):
        line = line.strip()
        
        # Skip empty lines between bullet points
        if not line and not current_paragraph and not bullet_stack:
            continue
            
        # Check for bullet points
        if line.startswith(('• ', '- ', '* ', '1. ')):
            # Add current paragraph if exists
            if current_paragraph:
                story.append(Paragraph(' '.join(current_paragraph), styles['BodyText']))
                current_paragraph = []
            
            # Determine bullet type and level
            if line.startswith('1. '):
                bullet_type = 'number'
                content = line[3:].strip()
                level = 0
            elif line.startswith('• '):
                bullet_type = 'bullet'
                content = line[2:].strip()
                level = 0
            elif line.startswith('- '):
                bullet_type = 'bullet'
                content = line[2:].strip()
                level = 1
            elif line.startswith('* '):
                bullet_type = 'bullet'
                content = line[2:].strip()
                level = 2
            
            # Add to bullet stack
            while len(bullet_stack) <= level:
                bullet_stack.append([])
            bullet_stack[level].append(content)
            
            # Reset higher levels
            for i in range(level + 1, len(bullet_stack)):
                if bullet_stack[i]:
                    # Add existing items as nested
                    if level >= 0:
                        bullet_stack[level].append((bullet_stack[i], level + 1))
                    bullet_stack[i] = []
        else:
            # Add to current paragraph or last bullet point
            if bullet_stack and any(bullet_stack):
                # Find the last non-empty level
                last_level = max(i for i, items in enumerate(bullet_stack) if items)
                if isinstance(bullet_stack[last_level][-1], str):
                    # Append to last bullet point
                    bullet_stack[last_level][-1] += ' ' + line
                else:
                    # Add as a new bullet point at current level
                    bullet_stack[last_level].append(line)
            else:
                # Add to current paragraph
                if current_paragraph or line:
                    current_paragraph.append(line)
    
    # Add any remaining bullet points
    if any(bullet_stack):
        for level, items in enumerate(bullet_stack):
            if items:
                bullet_type = 'number' if level == 0 and any(isinstance(item, str) and item[0].isdigit() for item in items) else 'bullet'
                story.extend(add_bullet_list(items, level, bullet_type))
    
    # Add any remaining paragraph
    if current_paragraph:
        story.append(Paragraph(' '.join(current_paragraph), styles['BodyText']))
    
    return story

def create_header_footer(canvas, doc, title, player_name, language_font):
    """Create header and footer with page numbers using the specified font."""
    # Save the current state of the canvas
    canvas.saveState()
    
    # Get page dimensions
    width, height = doc.pagesize
    
    # Define a local get_safe_font function for header/footer
    def get_safe_font(base_name, variant='Regular'):
        font_name = f"{base_name}-{variant}"
        if font_name in pdfmetrics.getRegisteredFontNames():
            return font_name
        # Fall back to regular variant if the requested variant doesn't exist
        regular_font = f"{base_name}-Regular"
        if regular_font in pdfmetrics.getRegisteredFontNames():
            return regular_font
        # If even regular variant doesn't exist, fall back to default font
        return DEFAULT_FONT
    
    # Set the font for header and footer with safe fallback
    font_name = get_safe_font(language_font, 'Bold')
    
    # Add header
    header_text = f"{title} - {player_name}"
    canvas.setFont(font_name, 9)
    canvas.drawRightString(width-50, height-30, header_text)
    
    # Add footer with page number
    page_num = canvas.getPageNumber()
    footer_text = f"Page {page_num}"
    # Use regular font for footer
    footer_font = get_safe_font(language_font, 'Regular')
    canvas.setFont(footer_font, 8)
    canvas.drawCentredString(width/2, 20, footer_text)
    
    # Add a line above footer
    canvas.line(50, 30, width-50, 30)
    
    # Restore the canvas state
    canvas.restoreState()

def get_language_font(language: str) -> tuple:
    """
    Get the appropriate font family and register all its variants for the given language.
    
    Returns:
        tuple: (font_family, is_unicode_font)
    """
    # Default to Noto Sans for English
    font_family = 'NotoSans'
    is_unicode_font = False
    
    # Check if we have a specific font for this language
    if language in INDIAN_LANGUAGE_FONTS:
        font_family = INDIAN_LANGUAGE_FONTS[language]
        # Check if the font files exist
        regular_path = os.path.join(FONT_DIR, f"{font_family}-Regular.ttf")
        if os.path.exists(regular_path):
            is_unicode_font = True
            
            # Define all possible variants
            variants = {
                'Regular': regular_path,
                'Bold': os.path.join(FONT_DIR, f"{font_family}-Bold.ttf"),
                'Italic': os.path.join(FONT_DIR, f"{font_family}-Italic.ttf"),
                'BoldItalic': os.path.join(FONT_DIR, f"{font_family}-BoldItalic.ttf")
            }
            
            # Track which variants are successfully registered
            registered_variants = {}
            
            # Try to register regular variant first
            if os.path.exists(regular_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_family, regular_path))
                    registered_variants['Regular'] = font_family
                    print(f"[DEBUG] Registered font: {font_family}")
                except Exception as e:
                    print(f"[WARNING] Could not register {font_family}: {e}")
                    # If we can't register the regular variant, fall back to Noto Sans
                    return 'NotoSans', False
            
            # Try to register other variants
            for variant, path in variants.items():
                if variant == 'Regular':
                    continue  # Already handled
                    
                variant_name = f"{font_family}-{variant}"
                if os.path.exists(path) and variant_name not in pdfmetrics.getRegisteredFontNames():
                    try:
                        pdfmetrics.registerFont(TTFont(variant_name, path))
                        registered_variants[variant] = variant_name
                        print(f"[DEBUG] Registered font variant: {variant_name}")
                    except Exception as e:
                        print(f"[WARNING] Could not register {variant_name}: {e}")
                        # If we can't register a variant, use the regular variant as fallback
                        registered_variants[variant] = font_family
            
            # Register font family with available variants
            try:
                registerFontFamily(
                    font_family,
                    normal=registered_variants.get('Regular', font_family),
                    bold=registered_variants.get('Bold', font_family),
                    italic=registered_variants.get('Italic', font_family),
                    boldItalic=registered_variants.get('BoldItalic', font_family)
                )
            except Exception as e:
                print(f"[WARNING] Could not register font family {font_family}: {e}")
        else:
            print(f"[WARNING] Font {font_family} not found. Falling back to Noto Sans.")
            font_family = 'NotoSans'
    
    # Ensure we have at least the regular variant registered
    if font_family not in pdfmetrics.getRegisteredFontNames():
        try:
            # Try to register the regular variant if not already registered
            regular_path = os.path.join(FONT_DIR, f"{font_family}-Regular.ttf")
            if os.path.exists(regular_path):
                pdfmetrics.registerFont(TTFont(font_family, regular_path))
            else:
                # Fall back to Noto Sans if the regular variant doesn't exist
                font_family = 'NotoSans'
        except Exception as e:
            print(f"[WARNING] Could not register fallback font {font_family}: {e}")
            font_family = 'Helvetica'
    
    return font_family, is_unicode_font

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
    
    # Get the appropriate font for the specified language and register all its variants
    language_font, is_unicode = get_language_font(language)
    
    # Create a fresh stylesheet
    styles = getSampleStyleSheet()
    
    # Function to safely get font name with fallback
    def get_safe_font(base_name, variant='Regular'):
        font_name = f"{base_name}-{variant}"
        if font_name in pdfmetrics.getRegisteredFontNames():
            return font_name
        # Fall back to regular variant if the requested variant doesn't exist
        regular_font = f"{base_name}-Regular"
        if regular_font in pdfmetrics.getRegisteredFontNames():
            return regular_font
        # If even regular variant doesn't exist, fall back to default font
        return DEFAULT_FONT
        
    # Define base styles with consistent font settings
    base_styles = {
        'fontName': get_safe_font(language_font, 'Regular'),
        'leading': 13.5,
        'spaceAfter': 6,
        'wordWrap': 'LTR',
        'encoding': 'UTF-8',
        'splitLongWords': False,
        'backColor': None,
        'borderWidth': 0,
        'borderColor': None,
        'borderPadding': 0,
        'allowWidows': 1,
        'allowOrphans': 1,
    }
    
    # Define style variations with safe font selection
    style_variations = {
        'Normal': {
            'fontName': get_safe_font(language_font, 'Regular'),
            'fontSize': 11,
            'leading': 13.5,
            'spaceAfter': 6,
        },
        'Heading1': {
            'fontName': get_safe_font(language_font, 'Bold'),
            'fontSize': 20,
            'leading': 24,
            'spaceAfter': 12,
            'textColor': colors.HexColor('#2c3e50'),
            'alignment': TA_CENTER,
        },
        'Heading2': {
            'fontName': get_safe_font(language_font, 'Bold'),
            'fontSize': 16,
            'leading': 20,
            'spaceAfter': 10,
            'textColor': colors.HexColor('#2c3e50'),
            'leftIndent': 0,
        },
        'Heading3': {
            'fontName': get_safe_font(language_font, 'Bold'),
            'fontSize': 14,
            'leading': 18,
            'spaceAfter': 8,
            'textColor': colors.HexColor('#34495e'),
        },
        'Italic': {
            'fontName': get_safe_font(language_font, 'Italic'),
        },
        'Bold': {
            'fontName': get_safe_font(language_font, 'Bold'),
        },
        'Title': {
            'fontName': get_safe_font(language_font, 'Bold'),
            'fontSize': 24,
            'leading': 28,
            'spaceAfter': 24,
            'textColor': colors.HexColor('#1a5276'),
            'alignment': TA_CENTER,
        },
        'Bullet': {
            'fontName': get_safe_font(language_font, 'Regular'),
            'leftIndent': 20,
            'firstLineIndent': -10,
            'spaceAfter': 3,
        },
    }
    
    # Apply base styles and variations to all styles
    for style_name, style_obj in styles.byName.items():
        # Reset the style with base styles
        for prop, value in base_styles.items():
            setattr(style_obj, prop, value)
        
        # Apply style-specific variations
        for var_name, var_style in style_variations.items():
            if var_name in style_name:
                for prop, value in var_style.items():
                    setattr(style_obj, prop, value)
        
        # Special handling for list items and other elements
        if 'List' in style_name:
            style_obj.leftIndent = 20
            style_obj.spaceBefore = 3
            style_obj.spaceAfter = 3
        
        # Ensure all text is left-aligned by default unless specified otherwise
        if not hasattr(style_obj, 'alignment'):
            style_obj.alignment = TA_LEFT
    
    # Add custom styles if they don't exist - using consistent font family
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
            fontName=DEFAULT_BOLD
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
            fontName=DEFAULT_BOLD,
            borderLeft=4,
            borderColor=colors.HexColor('#3498db'),
            leftPadding=8
        ))
    
    if 'BodyText' not in styles:
        styles.add(ParagraphStyle(
            name='BodyText',
            parent=styles['Normal'],
            fontSize=DEFAULT_FONT_SIZE,
            leading=14,
            spaceAfter=8,
            textColor=colors.HexColor('#2c3e50'),
            fontName=DEFAULT_FONT,
            wordWrap='LTR',
            splitLongWords=True,
            alignment=TA_LEFT
        ))
        
    # Add bullet point style
    if 'Bullet' not in styles:
        styles.add(ParagraphStyle(
            name='Bullet',
            parent=styles['BodyText'],
            leftIndent=20,
            firstLineIndent=0,
            spaceBefore=2,
            spaceAfter=2,
            fontName=DEFAULT_FONT,
            bulletFontName=DEFAULT_FONT
        ))
    
    if 'Footer' not in styles:
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Italic'],
            fontSize=SMALL_FONT_SIZE,
            alignment=TA_CENTER,
            spaceBefore=12,
            textColor=colors.HexColor('#7f8c8d'),
            fontName=DEFAULT_ITALIC
        ))
    
    # Create document with margins
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=60,  # More space for header
        bottomMargin=50  # More space for footer
    )
    
    # Add header and footer to each page using the same font
    def on_every_page(canvas, doc):
        create_header_footer(canvas, doc, title, player_name, language_font)
    
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
    
    # Add content sections using the new bullet point processor
    content_style = styles['BodyText']
    section_style = styles['SectionHeader']
    
    # Process the content to handle bullet points properly
    # First, split content into major sections
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
        
        # Process this section with our bullet point handler
        section_story = process_bullet_points(section)
        story.extend(section_story)
        
        # Add extra space after each major section
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
        page_text = f"Page {page_num}"
        canvas.setFont(DEFAULT_FONT, SMALL_FONT_SIZE)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        canvas.drawRightString(doc.width + doc.leftMargin, 30, page_text)

        # Add copyright text
        copyright_text = f"© {datetime.now().year} Badminton AI Analysis Tool | Confidential - For Training Purposes Only"
        canvas.setFont(DEFAULT_FONT, SMALL_FONT_SIZE)
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

def get_localized_title(role: str, player_name: str, language: str) -> str:
    """Generate a localized title based on role and language."""
    # English titles
    en_titles = {
        'coach': f"Badminton Performance Analysis - {player_name}",
        'student': f"Your Badminton Training Report - {player_name}",
        'parent': f"Badminton Progress Report - {player_name}"
    }
    
    # Hindi titles
    hi_titles = {
        'coach': f"बैडमिंटन प्रदर्शन विश्लेषण - {player_name}",
        'student': f"आपकी बैडमिंटन प्रशिक्षण रिपोर्ट - {player_name}",
        'parent': f"बैडमिंटन प्रगति रिपोर्ट - {player_name}"
    }
    
    # Tamil titles
    ta_titles = {
        'coach': f"பேட்மிண்டன் செயல்திறன் பகுப்பாய்வு - {player_name}",
        'student': f"உங்கள் பேட்மிண்டன் பயிற்சி அறிக்கை - {player_name}",
        'parent': f"பேட்மிண்டன் முன்னேற்ற அறிக்கை - {player_name}"
    }
    
    # Telugu titles
    te_titles = {
        'coach': f"బ్యాడ్మింటన్ ప్రదర్శన విశ్లేషణ - {player_name}",
        'student': f"మీ బ్యాడ్మింటన్ శిక్షణ నివేదిక - {player_name}",
        'parent': f"బ్యాడ్మింటన్ పురోగతి నివేదిక - {player_name}"
    }
    
    # Kannada titles
    kn_titles = {
        'coach': f"ಬ್ಯಾಡ್ಮಿಂಟನ್ ಕಾರ್ಯಕ್ಷಮತೆ ವಿಶ್ಲೇಷಣೆ - {player_name}",
        'student': f"ನಿಮ್ಮ ಬ್ಯಾಡ್ಮಿಂಟನ್ ತರಬೇತಿ ವರದಿ - {player_name}",
        'parent': f"ಬ್ಯಾಡ್ಮಿಂಟನ್ ಪ್ರಗತಿ ವರದಿ - {player_name}"
    }
    
    # Map language codes to title dictionaries
    title_maps = {
        'en': en_titles,
        'hi': hi_titles,
        'ta': ta_titles,
        'te': te_titles,
        'kn': kn_titles
    }
    
    # Get the appropriate title dictionary for the language
    title_dict = title_maps.get(language, en_titles)
    
    # Get the title for the role, or use a default if not found
    return title_dict.get(role.lower(), f"Badminton Report - {player_name}")

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
    
    # Generate localized title based on role and language
    title = get_localized_title(role, player_name, language)
    
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
