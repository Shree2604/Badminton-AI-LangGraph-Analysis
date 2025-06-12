<div align="center">

# 🏸 Badminton AI LangGraph Analysis

> *"Transforming badminton training with AI-powered performance insights"*

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/yourusername/badminton-ai-langgraph/pulls)

</div>

## 📝 Description

*"An intelligent badminton analysis tool that leverages LangGraph for parallel processing of match footage, delivering real-time performance metrics, multi-language reports, and AI-powered insights for players and coaches to elevate their game."*

## 🏗️ System Architecture

<div align="center">
  <img src="./docs/architecture.png" alt="System Architecture" width="800"/>
  <p><em>Figure: High-level architecture of the Badminton AI Analysis system</em></p>
</div>

## ✨ Features

- 🎯 **Advanced Pose Detection**: Real-time tracking of 33 key body points using MediaPipe
- 🎥 **Video Processing**: Efficient frame extraction and processing with OpenCV
- 📊 **Performance Metrics**: Detailed analysis of player movements, strokes, and positioning
- 📝 **AI-Powered Reports**: Generate detailed reports for coaches, players, and parents
- 🌍 **Multi-language Support**: Reports available in multiple languages including English, Hindi, and more
- ⚡ **Parallel Processing**: Optimized for performance with multi-threading and batch processing
- 📹 **Video Visualization**: Generate annotated videos with pose detection overlays

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/badminton-ai-langgraph.git
   cd badminton-ai-langgraph
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

## 🚀 Quick Start Guide

### Option 1: Simple Video Analysis

1. Place your badminton video sample2.mp4 (MP4 format) in the project root directory
2. Run the analysis script:
   ```bash
   python analyze_sample.py
   ```
3. Find the processed video in the `output_videos` directory

### Option 2: Full Analysis with `main.py`

The `main.py` script provides a complete analysis pipeline with additional features:

```bash
python main.py
```

#### Main Features:
- **Interactive CLI**: Guided interface for analysis
- **Multi-Player Support**: Analyze multiple players in the same video
- **Role-Based Reports**: Generate different report types:
  - Coach Report: Technical analysis and recommendations
  - Player Report: Performance metrics and improvement areas
  - Parent Report: Progress tracking and achievements
- **Multi-language Support**: Reports available in multiple languages

#### Command Line Arguments:
```
usage: main.py [-h] [--video_path VIDEO_PATH] [--output_dir OUTPUT_DIR]
               [--gemini_key GEMINI_KEY] [--num_players NUM_PLAYERS]
               [--roles {coach,player,parent,all}] [--language LANGUAGE]

Badminton AI Analysis Tool

options:
  -h, --help            show this help message and exit
  --video_path VIDEO_PATH
                        Path to the input video file
  --output_dir OUTPUT_DIR
                        Directory to save output files
  --gemini_key GEMINI_KEY
                        Google Gemini API key for advanced analysis
  --num_players NUM_PLAYERS
                        Number of players in the video (default: 1)
  --roles {coach,player,parent,all}
                        Type of report to generate (default: all)
  --language LANGUAGE   Language for the report (e.g., en, hi, ta, te, kn)
```

#### Example Usage:

1. Basic analysis with default settings:
   ```bash
   python main.py --video_path match.mp4
   ```

2. Advanced analysis for 2 players with specific reports:
   ```bash
   python main.py --video_path match.mp4 --num_players 2 --roles coach,player --language hi
   ```

3. Using environment variable for API key:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   python main.py --video_path match.mp4
   ```

## 📂 Project Structure

```
badminton-ai-langgraph/
├── badminton_ai/
│   ├── __init__.py
│   ├── pipeline.py          # LangGraph workflow orchestration
│   ├── video_utils.py       # Frame processing & pose detection
│   ├── video_visualizer.py  # Video visualization with pose detection
│   ├── audio_utils.py       # Audio processing and transcription
│   ├── report_generator.py  # AI-powered insights generation
│   └── pdf_generator.py     # Report generation in PDF format
├── analyze_sample.py        # Sample script for video analysis
├── main.py                  # Main CLI interface
└── requirements.txt         # Project dependencies
```

## 🎮 Demo

### Video Analysis with Pose Detection

<div align="center">
  <video src="./output_videos/sample_analysis.mp4" width="800" controls></video>
  <p><em>Figure: Example of pose detection on a badminton player showing key joint tracking</em></p>
</div>

### Key Features Demonstrated:

- **Real-time Pose Tracking**: 33 key body points with MediaPipe
- **Stroke Analysis**: Detect and analyze different badminton strokes
- **Movement Patterns**: Track player positioning and footwork
- **Performance Metrics**: Calculate speed, reach, and form metrics

## 🛠 Technical Details

### Video Processing Pipeline

1. **Frame Extraction**: Efficiently sample frames from the input video
2. **Pose Detection**: Use MediaPipe to detect and track body keypoints
3. **Analysis**: Process keypoints to extract meaningful metrics
4. **Visualization**: Generate annotated video with pose overlays
5. **Reporting**: Create detailed performance reports

### Performance Optimization

- Multi-threaded frame processing
- Batch processing for efficient GPU utilization
- Smart frame sampling to reduce processing time
- Memory-efficient video handling

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch:
   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/YourFeatureName
   ```
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for robust pose estimation
- [OpenCV](https://opencv.org/) for computer vision capabilities
- [LangChain](https://python.langchain.com/) for workflow orchestration
- [Google Gemini](https://gemini.google.com/) for AI-powered insights

## 📬 Contact

For questions or feedback, please open an issue on GitHub or contact the project maintainers at [shree.xai.dev@gmail.com](mailto:shree.xai.dev@gmail.com)

---

<div align="center">
Made with ❤️ by ShreeRaj Mummidivarapu
