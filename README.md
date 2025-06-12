# 🏸 Badminton AI LangGraph Analysis

> **AI-powered badminton performance analysis using computer vision and LangGraph**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://github.com/Shree2604/Badminton-AI-LangGraph-Analysis/pulls)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Shree2604/Badminton-AI-LangGraph-Analysis)

## 🚀 What it does

Transform your badminton videos into detailed performance insights with:
- **Real-time pose detection** (33 body points tracking)
- **AI-generated reports** for coaches, players & parents  
- **Multi-language support** (English, Hindi, Tamil, Telugu, Kannada)
- **Video annotations** with movement analysis
- **Performance metrics** and improvement recommendations
- **PDF report generation** with professional formatting
- **Parallel processing** for faster analysis

## 🛠️ Prerequisites

- Python 3.8 or higher
- FFmpeg (for video processing)
- Google Gemini API Key (for AI analysis)
- CUDA-compatible GPU (recommended for faster processing)

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Shree2604/Badminton-AI-LangGraph-Analysis.git
cd Badminton-AI-LangGraph-Analysis
```

### 2. Set Up Virtual Environment
```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root with your Gemini API key:
```bash
GEMINI_API_KEY=your_api_key_here
```

### 5. Run the Analysis
```bash
# Basic usage
python main.py --video_path your_match.mp4

# With additional options
python main.py \
  --video_path your_match.mp4 \
  --num_players 2 \
  --roles coach,student,parent \
  --language en \
  --output_dir ./analysis_results
```

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🎥 **Video Processing** | Extract frames, detect poses, track movements |
| 📊 **Performance Analytics** | Speed, accuracy, positioning metrics |
| 📝 **Smart Reports** | Role-based insights (coach/player/parent) |
| 🌍 **Multi-language** | Reports in 5+ languages |
| ⚡ **Parallel Processing** | Fast analysis with LangGraph workflows |
| 📄 **PDF Reports** | Professional PDF generation with page numbers |
| 🎯 **Pose Visualization** | Annotated video with keypoint tracking |
| 🔊 **Audio Analysis** | Shot detection and audio processing |

## 🏗️ System Architecture

<div align="center">
  <img src="./docs/architecture.png" alt="System Architecture" width="400"/>
  <p><em>High-level architecture of the Badminton AI Analysis Tool</em></p>
</div>

## 🎮 Demo

<div align="center">
  <img src="./output_videos/sample_analysis.gif" alt="Pose Detection Demo" width="600"/>
  <p><em>Real-time pose detection and movement analysis on badminton player</em></p>
</div>

## 📁 Project Structure

```
Badminton-AI-LangGraph-Analysis/
├── badminton_ai/           # Core analysis modules
│   ├── pipeline.py         # LangGraph workflow
│   ├── video_utils.py      # Pose detection & processing
│   └── report_generator.py # AI report generation
├── main.py                 # CLI interface
└── analyze_sample.py       # Quick demo script
```

## 🚀 Advanced Usage

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--video_path` | Path to the input video file | Required |
| `--num_players` | Number of players in the video (1 or 2) | 1 |
| `--roles` | Comma-separated roles for reports (coach,student,parent) | coach |
| `--language` | Report language (en, hi, ta, te, kn) | en |
| `--output_dir` | Directory to save analysis results | ./output |
| `--api_key` | Gemini API key (can also use GEMINI_API_KEY env var) | |
| `--yes` | Skip confirmation prompts | False |

### Example Commands

**Basic Analysis with Default Settings**
```bash
python main.py --video_path match.mp4
```

**Multi-Player Analysis**
```bash
python main.py --video_path doubles_match.mp4 --num_players 2
```

**Generate Reports in Hindi**
```bash
python main.py --video_path match.mp4 --language hi --roles coach,student
```

**Custom Output Directory**
```bash
python main.py --video_path match.mp4 --output_dir ./my_analysis_results
```

**Using Environment Variable for API Key**
```bash
export GEMINI_API_KEY="your-api-key-here"
python main.py --video_path match.mp4
```

## 📂 Output Structure

After analysis, the following files will be generated in the output directory:

```
output/
├── videos/               # Annotated video with pose tracking
│   └── match_analysis.mp4
├── frames/               # Extracted frames (if enabled)
├── reports/              # Generated reports
│   ├── coach/           # Coach-specific reports
│   │   ├── player1_coach_report.pdf
│   │   └── player1_coach_report.txt
│   ├── student/         # Student-specific reports
│   └── parent/          # Parent-specific reports
└── analysis_results/    # Raw analysis data
    ├── poses/          # Pose estimation data
    └── metrics/        # Performance metrics
```

## 📊 Report Features

- **Professional PDF Formatting** with page numbers and headers
- **Role-Specific Content** tailored for different audiences
- **Multi-language Support** with proper text rendering
- **Visual Elements** including charts and annotated frames
- **Actionable Insights** with improvement recommendations

## 🖥️ System Requirements

- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 2GB free space for processing
- **GPU**: NVIDIA GPU with CUDA support (recommended)
- **Python**: 3.8 or higher

## 🐛 Troubleshooting

**1. Dependencies Installation Issues**
```bash
# If you encounter any installation errors, try:
pip install --upgrade pip setuptools wheel
```

**2. FFmpeg Not Found**
- **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt install ffmpeg`

**3. CUDA Errors**
If you don't have a compatible GPU, you can force CPU mode by modifying the code to use CPU for inference.

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- MediaPipe for pose estimation
- Google Gemini for AI analysis
- ReportLab for PDF generation
- OpenCV for computer vision processing

## 🌟 Features in Development

- [ ] Web interface for easier interaction
- [ ] Real-time analysis with webcam input
- [ ] Advanced shot recognition
- [ ] Player performance comparison
- [ ] Mobile app integration

## 🤝 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📧 Contact

**Questions?** Open an issue or email: [shree.xai.dev@gmail.com](mailto:shree.xai.dev@gmail.com)

---
<div align="center">
<b>Built with ❤️ by ShreeRaj Mummidivarapu</b><br>
<i>Elevating badminton training through AI</i>
</div>