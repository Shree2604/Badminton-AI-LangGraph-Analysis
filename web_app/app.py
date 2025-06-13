from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sys
from flask import Flask, render_template, request, jsonify
import asyncio
from datetime import datetime

# Add the project root to the Python path to allow importing badminton_ai
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import the pipeline components
from badminton_ai.pipeline import build_pipeline, BadmintonState
from badminton_ai.report_generator import init_gemini
from badminton_ai.pdf_generator import convert_txt_to_pdf

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

REPORTS_FOLDER = os.path.join(app.root_path, 'reports')
if not os.path.exists(REPORTS_FOLDER):
    os.makedirs(REPORTS_FOLDER)

app.config['REPORTS_FOLDER'] = REPORTS_FOLDER

# Serve files from the reports folder statically
app.static_folder = os.path.join(app.root_path, 'static')
app.add_url_rule('/reports/<path:filename>',
                 endpoint='reports',
                 view_func=lambda filename: send_from_directory(app.config['REPORTS_FOLDER'], filename))

@app.route('/generate_report', methods=['POST'])
async def generate_report():
    language = request.form.get('language')
    report_type = request.form.get('report_type')  # This is not directly used by the pipeline, but can be passed for custom logic
    api_key = request.form.get('api_key')
    role = request.form.get('role')  # student, coach, parent
    player_num = int(request.form.get('player_num', 1)) # Default to 1

    if 'video_file' not in request.files:
        return jsonify({
            'report_content': 'Error: No video file part in the request.',
            'visualization_data': {}
        }), 400

    video_file = request.files['video_file']
    if video_file.filename == '':
        return jsonify({
            'report_content': 'Error: No selected video file.',
            'visualization_data': {}
        }), 400

    if video_file:
        filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video_file.save(video_path)
    else:
        return jsonify({
            'report_content': 'Error: Video file not uploaded correctly.',
            'visualization_data': {}
        }), 500

    print(f"Received request: video={video_path}, lang={language}, type={report_type}, role={role}, player_num={player_num}")

    if not api_key or not role:
        return jsonify({
            'report_content': 'Error: Missing API key or role.',
            'visualization_data': {}
        }), 400

    try:
        # Initialize Gemini with the API key
        init_gemini(api_key)

        # Build and run the pipeline
        pipeline = build_pipeline(api_key)
        
        # Initial state for the pipeline
        initial_state = BadmintonState(
            video_path=video_path,
            frames=[],
            pose=[],
            transcript="",
            report="",
            errors=[],
            player_num=player_num, # Pass player_num to the state
            locale=language # Pass language to the state
        )

        # Run the pipeline asynchronously
        final_state = await pipeline.ainvoke(initial_state)

        report_content = final_state.get('report', 'No report generated.')
        errors = final_state.get('errors', [])
        progress = final_state.get('progress', [])

        pdf_report_path = None
        if report_content != 'No report generated.':
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_filename = f"badminton_analysis_report_{timestamp}.txt"
                pdf_filename = f"badminton_analysis_report_{timestamp}.pdf"
                
                txt_report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
                pdf_report_path = os.path.join(app.config['REPORTS_FOLDER'], pdf_filename)

                with open(txt_report_path, "w", encoding="utf-8") as f:
                    f.write(report_content)
                
                convert_txt_to_pdf(txt_report_path, app.config['REPORTS_FOLDER'], role, language)
                # Construct a URL relative to the static reports folder
                import posixpath
                pdf_report_path = posixpath.join('/reports', os.path.basename(pdf_filename))
                print(f"PDF report generated at: {pdf_report_path}")
            except Exception as pdf_e:
                print(f"Error generating PDF report: {pdf_e}")
                errors.append({"step": "pdf_generation", "error": str(pdf_e)})

        if errors:
            report_content += "\n\nErrors during analysis:\n" + "\n".join([f"- {e['step']}: {e['error']}" for e in errors])

        # Placeholder for actual visualization data from pipeline if available
        # For now, using a simulated one or an empty one if no report
        return jsonify({
            'report_content': report_content,
            'progress': progress,
            'pdf_report_path': pdf_report_path # Add PDF report path
        })

    except Exception as e:
        print(f"Error during pipeline execution: {e}")
        return jsonify({
            'report_content': f'An error occurred during analysis: {str(e)}'
        }), 500

from werkzeug.exceptions import HTTPException

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the exception for debugging
    print(f"Unhandled exception: {e}")

    # Default error message and status code
    status_code = 500
    error_message = f'An unexpected server error occurred: {str(e)}'

    # If it's an HTTPException, use its code and description
    if isinstance(e, HTTPException):
        status_code = e.code if e.code else 500
        error_message = e.description if e.description else str(e)

    response = jsonify({
        'report_content': f'Error: {error_message}'
    })
    response.status_code = status_code
    return response

if __name__ == '__main__':
    app.run(debug=True)