# 🏸 Badminton AI LangGraph Analysis

> **AI-powered badminton performance analysis using computer vision, LangGraph orchestration, and Gemini AI**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://github.com/Shree2604/Badminton-AI-LangGraph-Analysis/pulls)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Shree2604/Badminton-AI-LangGraph-Analysis)

## 🚀 What it does

Transform your badminton videos into detailed performance insights with:
- **Real-time pose detection** with MediaPipe (tracking 33 body keypoints)
- **LangGraph orchestration** for linear pipeline processing
- **AI-generated reports** customized for coaches, players & parents  
- **Multi-language support** (English, Hindi, Tamil, Telugu, Kannada)
- **Video annotations** with pose tracking visualization
- **Performance metrics** including elbow angles and wrist distances
- **PDF report generation** with professional formatting

<div align="center">
  <img src="./output_videos/sample_analysis.gif" alt="Pose Detection Demo" width="600"/>
  <p><em>Real-time pose detection and movement analysis on badminton player</em></p>
</div>

## 🏗️ System Architecture

<div align="center">
  <img src="./docs/architecture.png" alt="System Architecture" width="400"/>
  <p><em>Linear pipeline architecture with LangGraph orchestration</em></p>
</div>

## 🛠️ Prerequisites

- Python 3.8 or higher
- OpenCV and MediaPipe for video processing
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
  --roles coach,student \
  --language en \
  --output_dir ./analysis_results
```

## 🌐 Web Application Deployment

### Local Deployment

```bash
# Navigate to the web app directory
cd web_app

# Install web app dependencies
pip install -r requirements.txt

# Run the Flask application
python app.py
```

```
Access the web interface at http://localhost:5000


## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🎥 **Video Processing** | MediaPipe pose detection, frame extraction, RGB conversion |
| 📊 **Performance Metrics** | Elbow angles, wrist distances, pose tracking |
| 📝 **Smart Reports** | Role-based insights (coach/player/parent) |
| 🌍 **Multi-language** | Reports in 5+ languages |
| ⚡ **LangGraph Pipeline** | Linear orchestration with state management |
| 📄 **PDF Reports** | Professional PDF generation with multilingual support |
| 🎯 **Pose Visualization** | Annotated video with keypoint tracking |
| 🔊 **Audio Analysis** | Speech transcription with Google Web Speech API |

## 📂 Output Structure

After analysis, the following files will be generated in the output directory:

```
output/
├── videos/               # Annotated video with pose tracking
│   └── match_analysis.mp4
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

## 🖥️ System Requirements

- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 2GB free space for processing
- **GPU**: NVIDIA GPU with CUDA support (recommended)
- **Python**: 3.8 or higher

## 🌟 Features in Development

- [ ] Strategy Agent implementation for tactical analysis
- [ ] Advanced shot recognition and classification
- [ ] Real-time analysis with webcam input
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